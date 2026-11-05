"""Freeze exact images, private historical regions and labels before parser runs."""
import io
import json
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import pymupdf
import yaml

from .entity_mentions import annotate_mentions
from .research_slice import check_slice, encoded, read, sha, write_new

PROTOCOL = 'spec/extensions/fidelity_campaign_v1.yaml'


def fold_whitespace(text):
    return ' '.join(text.split())


def printed_score(expected, actual, critical, equivalent_classes=()):
    """Synthetic printed content only. Missing output has no CER or pass."""
    if not isinstance(actual, str) or not actual.strip():
        return {'status': 'NO_TRANSCRIPT', 'literal_match': False, 'critical_present': {},
                'critical_count': 0, 'critical_denominator': len(critical), 'scientific_acceptance': False}
    original_actual = actual
    for variants in equivalent_classes:
        for variant in variants:
            expected = expected.replace(variant, variants[0])
            actual = actual.replace(variant, variants[0])
    expected, actual = fold_whitespace(expected), fold_whitespace(actual)
    present = {token: fold_whitespace(token) in actual for token in critical}
    return {'status': 'MEASURED_SYNTHETIC_ONLY', 'literal_match': actual == expected,
            'critical_present': present, 'critical_count': sum(present.values()),
            'critical_denominator': len(critical), 'raw_transcript_sha256': sha(original_actual.encode()),
            'equivalence_scope': 'DECLARED_DISPLAY_EQUIVALENCE_ONLY_NOT_FACT_NORMALIZATION',
            'scientific_acceptance': False}


def image_pdf(png, width_points, height_points):
    with pymupdf.open() as document:
        page = document.new_page(width=width_points, height=height_points)
        page.insert_image(page.rect, stream=png)
        raw = document.tobytes(garbage=4, deflate=True, no_new_id=True)
    with pymupdf.open(stream=raw, filetype='pdf') as check:
        if check[0].get_text().strip():
            raise ValueError('RASTER_INPUT_HAS_TEXT_LAYER')
    return raw


def validate_challenge(challenge):
    if challenge.get('synthetic') is not True or challenge.get('historical_gold') is not False:
        raise ValueError('SYNTHETIC_CHALLENGE_REQUIRED')
    ids = [panel['id'] for panel in challenge['panels']] + [case['id'] for case in challenge['context_cases']]
    if len(ids) != len(set(ids)) or any(not re.fullmatch(r'[a-z][a-z0-9-]+', ident) for ident in ids):
        raise ValueError('UNIQUE_SAFE_CASE_IDS_REQUIRED')
    for panel in challenge['panels']:
        text = '\n'.join(panel['lines'])
        if not all(token in text for token in panel['critical']):
            raise ValueError('CRITICAL_TOKEN_NOT_PRINTED')
    return challenge


def context_challenge(challenge):
    results = []
    for case in challenge['context_cases']:
        contexts = None
        if case.get('speaker_person_refs'):
            contexts = [{'context_id': 'constructed-speaker', 'start': 0, 'end': len(case['text']),
                         'speaker_person_refs': case['speaker_person_refs'],
                         'speaker_evidence_refs': ['synthetic:explicit-speaker'],
                         'quote_speaker_owned': case['quote_speaker_owned']}]
        response = annotate_mentions(case['text'], challenge['forms'], contexts, namespace='difficult:' + case['id'])
        actual = {}
        if 'expected_coreferences' in case:
            actual['coreferences'] = [[row['literal_text'], row['link_state'], row['candidate_person_refs']] for row in response['coreferences']]
        if 'expected_mentions' in case:
            actual['mentions'] = [[row['literal_text'], row['link_state'], row['candidate_entity_refs']] for row in response['mentions']]
        checks = {kind: rows == case['expected_' + kind] for kind, rows in actual.items()}
        results.append({'case_id': case['id'], 'synthetic': True, 'checks': checks,
                        'passed': bool(checks) and all(checks.values()), 'response': response})
    return results


def freeze_fidelity_suite(root):
    root = Path(root).resolve()
    lock_path=root/'spec/extensions/fidelity_campaign_v1.lock.json'
    if lock_path.is_file():
        from .fidelity_campaign import load_suite
        lock=json.loads(lock_path.read_bytes());path=root/lock['suite_manifest_path']
        suite,_=load_suite(root,path)
        return {'manifest':str(path),'jobs':len(suite['jobs']),'synthetic_jobs':len(suite['labels']),
                'context_cases':len(suite['context_cases']),'historical_gold':False,'mode':'REUSED_FROZEN_INPUTS'}
    protocol_raw = read(root, PROTOCOL); protocol = yaml.safe_load(protocol_raw)
    head = json.loads(read(root, 'ops/state/research-slice-head.json'))
    base = root / head['slice']
    if base.name != protocol['base_slice_id'] or not check_slice(root, base)['preview_eligible']:
        raise ValueError('WRONG_OR_STALE_FROZEN_BASE')
    payload = json.loads(read(root, head['slice'] + '/slice.json'))
    challenge_raw = read(root, protocol['challenge']); challenge = validate_challenge(json.loads(challenge_raw))
    options = challenge['image_policy']; font_path = Path(options['font'])
    font = ImageFont.truetype(str(font_path), options['font_size'])
    jobs, artifacts, labels = [], {}, {}

    def add_job(job, png, width_points, height_points):
        pdf = image_pdf(png, width_points, height_points)
        job.update(png_path=job['job_id'] + '.png', png_sha256=sha(png),
                   pdf_path=job['job_id'] + '.pdf', pdf_sha256=sha(pdf),
                   width_points=width_points, height_points=height_points)
        artifacts[job['png_path']] = png; artifacts[job['pdf_path']] = pdf
        jobs.append(job)

    for panel in challenge['panels']:
        height = options['margin'] * 2 + options['line_height'] * len(panel['lines'])
        image = Image.new('RGB', (options['width'], height), 'white'); draw = ImageDraw.Draw(image)
        for i, line in enumerate(panel['lines']):
            point = (options['margin'], options['margin'] + i * options['line_height'])
            box = draw.textbbox(point, line, font=font)
            if box[2] > image.width - 20 or box[3] > image.height - 10:
                raise ValueError('PRINTED_PANEL_CLIPPED')
            draw.text(point, line, font=font, fill='black')
        for variant in options['variants']:
            rendered = image.copy()
            if variant == 'downsample_blur':
                factor = options['degradation']['downsample_factor']
                rendered = rendered.resize((round(image.width * factor), round(image.height * factor)), Image.Resampling.LANCZOS)
                rendered = rendered.filter(ImageFilter.GaussianBlur(options['degradation']['gaussian_radius']))
                rendered = rendered.resize(image.size, Image.Resampling.BICUBIC)
            elif variant != 'clean':
                raise ValueError('UNKNOWN_DEGRADATION')
            stream = io.BytesIO(); rendered.save(stream, format='PNG')
            ident = panel['id'] + '-' + variant.replace('_', '-')
            add_job({'job_id': ident, 'synthetic': True, 'kind': 'region', 'variant': variant},
                    stream.getvalue(), image.width / 3, height / 3)
            labels[ident] = {'expected': '\n'.join(panel['lines']), 'critical': panel['critical'],
                             'equivalent_classes': panel.get('display_equivalent_classes', [])}
    for case in protocol['historical_sources']:
        sid = case['source_id']; source = payload['sources'][sid]; region = payload['regions'][sid]
        raw = read(root, source['preserved_blob']['path'])
        if sha(raw) != case['sha256'] or source['sha256'] != case['sha256'] or region['page_index'] != case['pdf_page_index']:
            raise ValueError('HISTORICAL_SOURCE_OR_PAGE_CHANGED')
        with pymupdf.open(stream=raw, filetype='pdf') as document:
            page = document[case['pdf_page_index']]
            if page.rotation:
                raise ValueError('ROTATED_PAGE_REQUIRES_EXPLICIT_ADAPTER')
            for kind in protocol['historical_inputs']:
                rectangle = page.rect if kind == 'page' else pymupdf.Rect(region['region_pdf_points'])
                pixmap = page.get_pixmap(matrix=pymupdf.Matrix(protocol['historical_dpi'] / 72, protocol['historical_dpi'] / 72),
                                        clip=rectangle, alpha=False)
                add_job({'job_id': 'historical-' + sid + '-' + kind, 'synthetic': False, 'kind': kind,
                         'source_id': sid, 'source_sha256': source['sha256'], 'pdf_page_index': case['pdf_page_index'],
                         'source_region_pdf_points': list(rectangle), 'historical_reference': None},
                        pixmap.tobytes('png'), rectangle.width, rectangle.height)
    if len(jobs) > protocol['budgets']['max_jobs_per_backend']:
        raise ValueError('JOB_BUDGET_EXCEEDED')
    manifest = {'version': '1.0.0', 'base_slice_id': base.name, 'base_slice_path': head['slice'],
                'protocol_sha256': sha(protocol_raw), 'challenge_sha256': sha(challenge_raw),
                'font_sha256': sha(font_path.read_bytes()), 'jobs': jobs, 'labels': labels,
                'context_cases': challenge['context_cases'], 'forms': challenge['forms'],
                'artifacts': {path: sha(body) for path, body in artifacts.items()},
                'render_code_sha256': sha(Path(__file__).read_bytes()),
                'renderer_versions': {'pymupdf': pymupdf.VersionBind, 'pillow': Image.__version__},
                'scientific_acceptance': False, 'release_authorized': False}
    raw = encoded(manifest); folder = root / 'outputs/fidelity-suites' / sha(raw)
    for path, body in artifacts.items():
        write_new(folder / path, body)
    write_new(folder / 'manifest.json', raw)
    # Human-readable statement of frozen labels is separate from worker requests.
    return {'manifest': str(folder / 'manifest.json'), 'jobs': len(jobs),
            'synthetic_jobs': len(labels), 'context_cases': len(challenge['context_cases']),
            'historical_gold': False, 'scientific_acceptance': False}
