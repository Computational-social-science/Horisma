"""Source-bound complementary observations, without voting or constructing a quote."""
import json
from pathlib import Path
import re

import yaml

from .probe_artifacts import load_attempt
from .research_slice import check_slice, encoded, sha, write_new


def variant_ledger(channels, probes):
    """Offsets address each unchanged channel, never a reconstructed consensus text."""
    if len({channel['id'] for channel in channels}) != len(channels):
        raise ValueError('DUPLICATE_CHANNEL_ID')
    rows = []
    for probe in probes:
        observations = []
        for channel in channels:
            matches = [{'start': match.start(), 'end': match.end(), 'text': match.group()}
                       for match in re.finditer(probe['pattern'], channel['text'])]
            observations.append({'channel_id': channel['id'], 'matches': matches,
                                 'status': 'LOCATED' if len(matches) == 1 else
                                           ('NOT_LOCATED' if not matches else 'AMBIGUOUS')})
        unique = {item['matches'][0]['text'] for item in observations if item['status'] == 'LOCATED'}
        rows.append({'probe_id': probe['id'], 'observations': observations,
                     'literal_disagreement': len(unique) > 1,
                     'missing_or_ambiguous_channel': any(item['status'] != 'LOCATED' for item in observations),
                     'resolution': 'UNRESOLVED_NO_QUALIFIED_REFERENCE', 'accepted': False})
    return rows


def crosscheck_transcriptions(root, folder, audit_path, source_id):
    root, folder, audit_path = Path(root).resolve(), Path(folder).resolve(), Path(audit_path).resolve()
    if not check_slice(root, folder)['preview_eligible']:
        raise ValueError('STALE_SLICE')
    payload = json.loads((folder / 'slice.json').read_bytes())
    config_raw = (root / 'spec/extensions/transcription_crosscheck.yaml').read_bytes()
    config = yaml.safe_load(config_raw)
    if source_id != config['source_id']:
        raise ValueError('NO_DECLARED_CROSSCHECK_TARGET')
    if not audit_path.is_relative_to(folder / 'layout-audit'):
        raise ValueError('EXTERNAL_AUDIT')
    audit_raw = audit_path.read_bytes(); audit = json.loads(audit_raw)
    if audit_path.parent.name != sha(audit_raw) or audit['slice_id'] != folder.name:
        raise ValueError('AUDIT_BINDING_CHANGED')
    target = next((row for row in audit['checks'] if row['id'] == config['audit_target_id']), None)
    if target is None:
        raise ValueError('CROSSCHECK_AUDIT_TARGET_MISSING')
    source, region = payload['sources'][source_id], payload['regions'][source_id]
    comparison, unit = target['comparison'], target['unit']
    if (target['source_id'] != source_id or comparison['source_sha256'] != source['sha256']
            or comparison['page_index'] != region['page_index']
            or unit['work_version_id'] != source['version_id']
            or unit['pdf_page_index'] != region['page_index']
            or sha(unit['text'].encode()) != unit['text_sha256']):
        raise ValueError('CROSSCHECK_SOURCE_OR_PAGE_MISMATCH')
    attempt, files = load_attempt(root / 'outputs/parser-comparison/paddleocr-3.7.0', source_id)
    receipt = json.loads(files['receipt.json'])
    if (receipt['slice_id'] != folder.name or receipt['source_sha256'] != source['sha256']
            or receipt['pdf_page_index'] != region['page_index'] or len(receipt['real_regions']) != 1):
        raise ValueError('PADDLE_CONTEXT_MISMATCH')
    candidate = receipt['real_regions'][0]
    native = (root / region['native_text_blob']['path']).read_bytes()
    if (sha(native) != region['native_text_blob']['sha256']
            or candidate['region_id'] != region['region_id']
            or candidate['image_sha256'] != region['render_blob']['sha256']
            or sha(files['historical-region.png']) != candidate['image_sha256']
            or sha(files['historical-region.json']) != candidate['raw_output_sha256']
            or '\n'.join(json.loads(files['historical-region.json'])['res']['rec_texts']) != candidate['transcript']):
        raise ValueError('CROSSCHECK_CHANNEL_BYTES_CHANGED')
    channels = [
        {'id': 'native', 'text': native.decode(), 'lineage': 'UNKNOWN_EMBEDDED_TEXT',
         'region_pdf_points': region['region_pdf_points'], 'render_sha256': region['render_blob']['sha256']},
        {'id': 'paddle-v5-en', 'text': candidate['transcript'], 'lineage': 'PADDLEOCR_V5_EN',
         'region_pdf_points': candidate['region_pdf_points'], 'render_sha256': candidate['image_sha256']},
        {'id': 'rapid-v6', 'text': comparison['image_text'], 'lineage': 'PADDLEOCR_V6_SHARED',
         'region_pdf_points': comparison['region_pdf_points'], 'render_sha256': comparison['render_sha256'],
         'model_sha256': comparison.get('model_sha256')},
        {'id': 'docling-rapid-v6', 'text': unit['text'], 'lineage': 'PADDLEOCR_V6_SHARED',
         'region_pdf_points': unit['region_pdf_points'], 'render_sha256': None},
    ]
    for channel in channels:
        channel.update(text_sha256=sha(channel['text'].encode()), fidelity_qualified=False,
                       comparison_scope='REGIONAL_CONTEXT_VARIANTS_NOT_INTERCHANGEABLE_TRANSCRIPTS')
    report = {'slice_id': folder.name, 'source_sha256': source['sha256'], 'page_index': region['page_index'],
              'audit_sha256': sha(audit_raw), 'paddle_attempt_id': attempt, 'config_sha256': sha(config_raw),
              'operator_sha256': sha(Path(__file__).read_bytes()), 'channels': channels,
              'probes': variant_ledger(channels, config['probes']),
              'affected_assertions': payload['assertions'], 'affected_tasks': payload['tasks'],
              'coupling': 'RapidOCR and Docling share weights; v5/v6 share project lineage. Agreement is not independent historical corroboration.',
              'automatic_merge': False, 'majority_vote': False, 'fidelity_qualified': False,
              'scientific_acceptance': False, 'release_authorized': False}
    raw = encoded(report)
    output = folder / 'transcription-crosscheck' / sha(raw) / 'report.json'
    write_new(output, raw)
    return {'report': str(output), 'channels': len(channels), 'probes': len(report['probes']),
            'literal_disagreements': sum(row['literal_disagreement'] for row in report['probes']),
            'fidelity_qualified': False, 'model_calls': 0}
