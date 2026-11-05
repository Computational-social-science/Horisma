"""Compare preserved parser observations; select scoped candidates without merging evidence."""
import json
from pathlib import Path
from difflib import SequenceMatcher

from PIL import Image

from .fidelity_blocks import normalize_blocks, normalized_bbox
from .fidelity_campaign import load_suite
from .fidelity_suite import printed_score, context_challenge, fold_whitespace
from .probe_artifacts import load_attempt
from .research_slice import encoded, read, sha, write_new


def campaign_report(root, manifest_path):
    root, manifest_path = Path(root).resolve(), Path(manifest_path).resolve()
    suite, protocol = load_suite(root, manifest_path)
    backend_results = {}; historical = []
    for backend in protocol['backends']:
        try:
            attempt, files = load_attempt(root / 'outputs/fidelity-campaigns' / backend, manifest_path.parent.name)
        except (OSError, ValueError, KeyError) as exc:
            backend_results[backend] = {'status': 'UNAVAILABLE', 'reason': str(exc), 'planned': len(suite['jobs'])}
            continue
        process = json.loads(files['process.json']); request_raw = files['request.json']; request = json.loads(request_raw)
        if (sha(request_raw) != process['request_sha256'] or request['suite_id'] != manifest_path.parent.name
                or request['backend'] != backend or sha(files['model-manifest.json']) != request['model_manifest_sha256']
                or sha(files['worker-source.py']) != request['worker_sha256']
                or sha(files['normalizer-source.py']) != request['normalizer_sha256']
                or sha(files['operator-source.py']) != process['operator_sha256']):
            raise ValueError('CAMPAIGN_PRODUCER_BINDING_CHANGED')
        requested = {job['job_id']: job for job in request['jobs']}
        rows = []; dimensions = {}
        for job in suite['jobs']:
            ident = job['job_id']; row = {'job_id': ident, 'synthetic': job['synthetic'], 'kind': job['kind']}
            if ident not in requested or requested[ident]['png_sha256'] != job['png_sha256']:
                raise ValueError('CAMPAIGN_INPUT_MISMATCH')
            row_name = ident + '.row.json'; raw_name = ident + '.raw.json'
            if row_name not in files:
                row.update(status='NO_RESPONSE', score=None); rows.append(row); continue
            produced = json.loads(files[row_name])
            if produced['job_id'] != ident or produced['input_sha256'] != job['png_sha256']:
                raise ValueError('CAMPAIGN_ROW_BINDING_CHANGED')
            row.update(status=produced['status'], elapsed_seconds=produced['elapsed_seconds'], error=produced.get('error'))
            if raw_name not in files:
                row['score'] = None; rows.append(row); continue
            if sha(files[raw_name]) != produced.get('raw_output_sha256'):
                raise ValueError('CAMPAIGN_RAW_OUTPUT_CHANGED')
            try:
                blocks = normalize_blocks(backend, json.loads(files[raw_name]), job['kind'])
                transcript = '\n'.join(block['text'] for block in blocks)
            except (ValueError, KeyError, TypeError) as exc:
                row.update(status='RAW_RETAINED_ADAPTER_FAILED', adapter_error=str(exc), score=None)
                rows.append(row); continue
            row.update(transcript=transcript, transcript_sha256=sha(transcript.encode()), blocks=blocks,
                       raw_output_sha256=sha(files[raw_name]),
                       normalization_replayed=transcript != produced.get('transcript'))
            with Image.open(manifest_path.parent / job['png_path']) as image:
                width, height = image.size
            for block in blocks:
                try:
                    block['normalized_bbox'] = normalized_bbox(block, width, height)
                except (ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
                    block['geometry_quarantine'] = str(exc)
            if row['status'] != 'SUCCEEDED':
                row['score'] = None
                rows.append(row)
                continue
            if job['synthetic']:
                label = suite['labels'][ident]
                row['score'] = printed_score(label['expected'], transcript, label['critical'], label['equivalent_classes'])
                dimension = ident.removesuffix('-clean').removesuffix('-downsample-blur')
                bucket = dimensions.setdefault(dimension, {'critical_count': 0, 'critical_denominator': 0,
                                                           'literal_matches': 0, 'observations': 0,'valid_observations':0})
                bucket['critical_count'] += row['score']['critical_count']; bucket['critical_denominator'] += len(label['critical'])
                bucket['literal_matches'] += int(row['score']['literal_match']); bucket['observations'] += 1
                bucket['valid_observations']+=int(row['score']['status']!='NO_TRANSCRIPT')
            elif job['kind'] == 'region':
                historical.append({'backend': backend, 'attempt_id': attempt, 'job_id': ident,
                                   'source_id': job['source_id'], 'source_sha256': job['source_sha256'],
                                   'pdf_page_index': job['pdf_page_index'], 'region_pdf_points': job['source_region_pdf_points'],
                                   'input_sha256': job['png_sha256'], 'raw_output_sha256': row['raw_output_sha256'],
                                   'transcript': transcript, 'transcript_sha256': row['transcript_sha256'],
                                   'model_manifest_sha256': request['model_manifest_sha256'],
                                   'fidelity_qualified': False, 'scientific_acceptance': False})
            rows.append(row)
        synthetic_rows = [row for row in rows if row['synthetic']]
        available = [row for row in synthetic_rows if row.get('score') and row['score']['status'] != 'NO_TRANSCRIPT']
        backend_results[backend] = {'status': process['status'], 'attempt_id': attempt, 'producer': process,
                                    'request_sha256': sha(request_raw), 'rows': rows, 'dimensions': dimensions,
                                    'synthetic_planned': len(synthetic_rows), 'synthetic_transcripts': len(available),
                                    'literal_matches': sum(row['score']['literal_match'] for row in available),
                                    'missing_transcripts': len(synthetic_rows) - len(available),
                                    'historical_accuracy': None, 'fidelity_qualified': False}
    candidate_dimensions = {}
    for dimension in {dimension for result in backend_results.values() for dimension in result.get('dimensions', {})}:
        scores = {}
        for backend, result in backend_results.items():
            bucket = result.get('dimensions', {}).get(dimension)
            if bucket and bucket['valid_observations'] == 2 and bucket['critical_denominator']:
                scores[backend] = bucket['critical_count'] / bucket['critical_denominator']
        if scores:
            best = max(scores.values())
            candidate_dimensions[dimension] = {'candidate_backends': sorted(backend for backend, score in scores.items() if score == best),
                                               'observed_critical_fraction': scores, 'scope': 'SAME_CONSTRUCTED_DEVELOPMENT_CONTROLS_ONLY',
                                               'qualification_granted': False}
    disagreements = []
    page_region_comparisons=[]
    jobs={job['job_id']:job for job in suite['jobs']}
    for case in protocol['historical_sources']:
        channels = [row for row in historical if row['source_id'] == case['source_id']]
        disagreements.append({'source_id': case['source_id'], 'available_backends': [row['backend'] for row in channels],
                              'distinct_whitespace_folded_transcripts': len({fold_whitespace(row['transcript']) for row in channels}),
                              'historical_reference': None, 'resolution': 'UNQUALIFIED_VARIANTS_NO_VOTE_NO_MERGE'})
        sid=case['source_id'];page_job=jobs['historical-'+sid+'-page'];region_job=jobs['historical-'+sid+'-region']
        frame=page_job['source_region_pdf_points'];rectangle=region_job['source_region_pdf_points']
        bounds=[(rectangle[0]-frame[0])/(frame[2]-frame[0]),(rectangle[1]-frame[1])/(frame[3]-frame[1]),
                (rectangle[2]-frame[0])/(frame[2]-frame[0]),(rectangle[3]-frame[1])/(frame[3]-frame[1])]
        for backend,result in backend_results.items():
            page=next((row for row in result.get('rows',[]) if row['job_id']==page_job['job_id']),None)
            direct=next((row for row in historical if row['source_id']==sid and row['backend']==backend),None)
            if not page or not direct or 'blocks' not in page:continue
            contained=[];crossing=0;unplaced=0
            for block in page['blocks']:
                box=block.get('normalized_bbox')
                if box is None:unplaced+=1;continue
                if bounds[0]<=box[0] and bounds[1]<=box[1] and box[2]<=bounds[2] and box[3]<=bounds[3]:
                    contained.append(block['text'])
                elif box[0]<bounds[2] and box[2]>bounds[0] and box[1]<bounds[3] and box[3]>bounds[1]:crossing+=1
            projection='\n'.join(contained)
            page_region_comparisons.append({'source_id':sid,'backend':backend,'contained_block_count':len(contained),
                                             'boundary_crossing_block_count':crossing,'unplaced_block_count':unplaced,
                                             'strict_projection':projection,'direct_region_transcript_sha256':direct['transcript_sha256'],
                                             'whitespace_agreement':SequenceMatcher(None,fold_whitespace(projection),fold_whitespace(direct['transcript'])).ratio() if projection else None,
                                             'scope':'LOCATION_DIAGNOSTIC_NOT_REFERENCE_ACCURACY','fidelity_qualified':False})
    challenge = json.loads(read(root, protocol['challenge']))
    contexts = context_challenge(challenge)
    report = {'version': '1.0.0', 'suite_id': manifest_path.parent.name, 'suite_manifest': manifest_path.relative_to(root).as_posix(),
              'effective_base_slice_path': suite.get('effective_base_slice_path', suite['base_slice_path']),
              'replay_mode': 'SEALED_OUTPUT_RECOMPUTATION', 'model_calls': 0,
              'reporter_sha256': sha(Path(__file__).read_bytes()),
              'normalizer_sha256': sha(read(root, 'src/horisma_p0/fidelity_blocks.py')),
              'scoring_operator_sha256':sha(read(root,'src/horisma_p0/fidelity_suite.py')),
              'entity_operator_sha256': sha(read(root, 'src/horisma_p0/entity_mentions.py')),
              'backends': backend_results, 'historical_region_observations': historical,
              'historical_disagreements': disagreements, 'dimension_candidates': candidate_dimensions,
              'page_region_comparisons':page_region_comparisons,
              'context_cases': contexts, 'context_passed': sum(row['passed'] for row in contexts),
              'context_denominator': len(contexts), 'layout_qualification': 'NOT_ESTABLISHED_NO_SYNTHETIC_LAYOUT_GOLD',
              'lineage': 'All three recognition channels have PaddleOCR ancestry; layouts and exact weights differ. Tool count is not independent corroboration.',
              'historical_accuracy': None, 'scientific_acceptance': False, 'release_authorized': False}
    raw = encoded(report); path = root / 'outputs/fidelity-comparisons' / sha(raw) / 'report.json'; write_new(path, raw)
    return {'report': str(path), 'backends': {backend: {key: result.get(key) for key in
             ('status', 'synthetic_planned', 'synthetic_transcripts', 'literal_matches', 'missing_transcripts')}
             for backend, result in backend_results.items()}, 'historical_regions': len(historical),
            'context_passed': report['context_passed'], 'context_denominator': len(contexts), 'scientific_acceptance': False}


def load_campaign_report(root, report_path):
    root, report_path = Path(root).resolve(), Path(report_path).resolve()
    if not report_path.is_relative_to(root / 'outputs/fidelity-comparisons'):
        raise ValueError('EXTERNAL_FIDELITY_REPORT')
    raw = report_path.read_bytes(); report = json.loads(raw)
    if report_path.parent.name != sha(raw):
        raise ValueError('FIDELITY_REPORT_CHANGED')
    suite, _ = load_suite(root, root / report['suite_manifest'])
    if report.get('effective_base_slice_path') != suite.get('effective_base_slice_path', suite['base_slice_path']):
        raise ValueError('STALE_CAMPAIGN_BASE_BINDING')
    if report['reporter_sha256'] != sha(Path(__file__).read_bytes()):
        raise ValueError('STALE_REPORTER_REPORT')
    if report['entity_operator_sha256'] != sha(read(root,'src/horisma_p0/entity_mentions.py')):
        raise ValueError('STALE_ENTITY_REPORT')
    if report['normalizer_sha256'] != sha(read(root, 'src/horisma_p0/fidelity_blocks.py')):
        raise ValueError('STALE_NORMALIZER_REPORT')
    if report['scoring_operator_sha256']!=sha(read(root,'src/horisma_p0/fidelity_suite.py')):
        raise ValueError('STALE_SCORING_REPORT')
    for backend, result in report['backends'].items():
        if 'attempt_id' not in result:
            continue
        attempt, files = load_attempt(root / 'outputs/fidelity-campaigns' / backend, report['suite_id'])
        if attempt != result['attempt_id'] or sha(files['request.json']) != result['request_sha256']:
            raise ValueError('STALE_CAMPAIGN_ATTEMPT')
    return report


def regional_route(root, report_path, source_id, dimension):
    report = load_campaign_report(root, report_path)
    if dimension not in report['dimension_candidates']:
        return {'status': 'ABSTAINED_NO_SCOPED_CANDIDATE', 'scientific_acceptance': False}
    candidates = report['dimension_candidates'][dimension]['candidate_backends']
    observations = [row for row in report['historical_region_observations'] if row['source_id'] == source_id]
    preferred = [row for row in observations if row['backend'] in candidates]
    rates=report['dimension_candidates'][dimension]['observed_critical_fraction']
    if max(rates.values())<1:
        return {'status':'ABSTAINED_CRITICAL_DIMENSION_UNRESOLVED','source_id':source_id,'dimension':dimension,
                'primary_candidates':[],'diagnostic_candidates':preferred,'complementary_channels':observations,
                'merged_text':None,'scientific_acceptance':False,'model_calls':0,
                'reason':'No backend preserved every declared critical item in both constructed variants.'}
    return {'status': 'CACHED_REGION_CANDIDATES_ONLY' if preferred else 'ABSTAINED_MISSING_REGION',
            'source_id': source_id, 'dimension': dimension, 'primary_candidates': preferred,
            'complementary_channels': [row for row in observations if row['backend'] not in candidates],
            'merged_text': None, 'scientific_acceptance': False, 'release_authorized': False,
            'selection_scope': 'DEVELOPMENT_DIAGNOSTIC_NOT_QUALIFIED_HISTORICAL_TRANSCRIPTION', 'model_calls': 0}
