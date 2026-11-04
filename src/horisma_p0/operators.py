"""Small reusable operators with explicit refusal and provenance boundaries."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from bs4 import BeautifulSoup
from jsonschema import Draft202012Validator
from pypdf import PdfReader
import yaml


class ContractError(ValueError):
    """A declared contract was violated; never a scientific judgment."""


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def owned_path(root: Path, relative: str) -> Path:
    root = root.resolve()
    fragment = Path(relative)
    if fragment.is_absolute() or '..' in fragment.parts or ':' in relative:
        raise ContractError('PATH_OUTSIDE_PROJECT')
    target = (root / fragment).resolve()
    if not target.is_relative_to(root):
        raise ContractError('PATH_OUTSIDE_PROJECT')
    return target


def load_json(path: Path):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ContractError(f'DUPLICATE_JSON_KEY:{key}')
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_pairs)


def save_new_json(path: Path, value) -> None:
    """Create immutable JSON; identical replay is permitted, replacement is refused."""
    body = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('xb') as stream:
            stream.write(body)
    except FileExistsError:
        if path.read_bytes() != body:
            raise ContractError(f'IMMUTABLE_OUTPUT_EXISTS:{path.name}')


def index_wikipedia(payload: bytes, expected_sha256: str, revision_id: str) -> dict:
    """Discovery index only. No Wikipedia passage becomes a scholarly claim."""
    if digest(payload) != expected_sha256:
        raise ContractError('SOURCE_DIGEST_MISMATCH')
    html = payload.decode('utf-8', errors='strict')
    if not re.search(r'"wgRevisionId"\s*:\s*' + re.escape(revision_id) + r'\b', html):
        raise ContractError('REVISION_MISMATCH')
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.select_one('.mw-parser-output')
    if body is None:
        raise ContractError('ARTICLE_BODY_MISSING')
    references = []
    groups = {}
    for ordinal, item in enumerate(body.select('ol.references > li'), 1):
        anchor = item.get('id')
        if not anchor:
            raise ContractError('REFERENCE_ANCHOR_MISSING')
        links = [a['href'] for a in item.select('a.external[href]')]
        dois = sorted({unquote(urlsplit(url).path).lstrip('/').lower() for url in links
                       if urlsplit(url).hostname == 'doi.org'})
        text = item.get_text(' ', strip=True)
        key = 'doi:' + dois[0] if dois else 'citation:' + digest(text.encode('utf-8'))
        group = groups.setdefault(key, f'WB-{len(groups)+1:03}')
        references.append({'reference_anchor': anchor, 'reference_ordinal': ordinal,
                           'proposed_work_group': group, 'doi_candidates': dois,
                           'citation_text': text, 'external_urls': links,
                           'identity_status': 'UNVERIFIED', 'rights_status': 'NOT_REVIEWED'})
    if not references:
        raise ContractError('REFERENCES_MISSING')
    return {'format_version': 'horisma.wikipedia-discovery.v1', 'purpose': 'DISCOVERY_ONLY',
            'source_sha256': expected_sha256, 'revision_id': revision_id,
            'reference_entries': references, 'proposed_work_groups': len(groups),
            'scientific_adjudication_performed': False}


SOURCE_HOSTS = frozenset({'garfield.library.upenn.edu', 'arxiv.org', 'www.nature.com',
                          'journals.sagepub.com', 'royalsocietypublishing.org'})


def admissible_source_url(url: str) -> bool:
    parts = urlsplit(url)
    return (parts.scheme == 'https' and parts.hostname in SOURCE_HOSTS
            and parts.port in (None, 443) and parts.username is None and parts.password is None)


class SourceRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not admissible_source_url(newurl):
            raise ContractError('REDIRECT_OUTSIDE_SOURCE_ALLOWLIST')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def acquire_source(root: Path, source_id: str, url: str, expected_media: str) -> dict:
    """One lawful acquisition attempt. No account access, paid API, or text mining."""
    if not re.fullmatch(r'[A-Z0-9_-]+', source_id) or expected_media not in {'pdf', 'html'}:
        raise ContractError('INVALID_ACQUISITION_SPEC')
    if not admissible_source_url(url):
        raise ContractError('SOURCE_URL_NOT_ALLOWLISTED')
    folder = owned_path(root, f'data/intake/literature/{source_id}')
    receipt_path = folder / 'acquisition.json'
    if receipt_path.exists():
        cached = load_json(receipt_path)
        if cached['requested_url'] != url or cached['expected_media'] != expected_media:
            raise ContractError('ACQUISITION_BINDING_CHANGED')
        if cached['access_status'] == 'LOCAL_AVAILABLE':
            body_path = owned_path(root, cached['relative_path'])
            if digest(body_path.read_bytes()) != cached['sha256']:
                raise ContractError('CACHED_SOURCE_CHANGED')
        return cached
    receipt = {'source_id': source_id, 'requested_url': url, 'expected_media': expected_media,
               'attempted_at': datetime.now(timezone.utc).isoformat(), 'attempt_limit': 1,
               'identity_status': 'UNVERIFIED', 'rights_status': 'NOT_REVIEWED',
               'processing_authorized': False, 'public_redistribution_authorized': False}
    try:
        opener = build_opener(SourceRedirects())
        with opener.open(Request(url, headers={'User-Agent': 'Horisma-P0/0.1 (research source intake)'}), timeout=25) as response:
            payload = response.read(16 * 1024 * 1024 + 1)
            receipt.update(http_status=response.status, resolved_url=response.geturl())
        if len(payload) > 16 * 1024 * 1024:
            raise ContractError('SOURCE_SIZE_LIMIT')
        if expected_media == 'pdf' and not payload.startswith(b'%PDF-'):
            raise ContractError('EXPECTED_PDF_NOT_RETURNED')
        if expected_media == 'html':
            text = payload.decode('utf-8', errors='strict').lower()
            if '<html' not in text or any(s in text for s in ['checking your browser', 'captcha', 'just a moment...']):
                raise ContractError('HTML_ACCESS_CHALLENGE')
        folder.mkdir(parents=True, exist_ok=True)
        relative = f'data/intake/literature/{source_id}/source.{expected_media}'
        with owned_path(root, relative).open('xb') as stream:
            stream.write(payload)
        receipt.update(access_status='LOCAL_AVAILABLE', relative_path=relative,
                       sha256=digest(payload), byte_count=len(payload), failure_kind=None)
    except (HTTPError, URLError, TimeoutError, ContractError, UnicodeError) as exc:
        status = exc.code if isinstance(exc, HTTPError) else None
        reason = ('ACCESS_DENIED' if status in {401, 403} else 'TRANSIENT_NETWORK'
                  if isinstance(exc, (URLError, TimeoutError)) else 'INVALID_DOCUMENT')
        receipt.update(access_status='WAITING_HUMAN_SOURCE', http_status=status,
                       failure_kind=reason, error_type=type(exc).__name__,
                       failure_detail=str(exc)[:300], resume_condition='Lawful source supplied; independently recheck identity, version and operation-specific rights.')
    save_new_json(receipt_path, receipt)
    return receipt


FROZEN_ARTIFACTS = frozenset({'spec/controlled_vocabularies.yaml','spec/logic_catalog.yaml','spec/operator_catalog.yaml',
    'docs/data-dictionary/Horisma_Project_Data_Dictionary_EN.md','spec/p0/candidate_ledger.schema.json',
    'spec/p0/protocol.json','spec/p0/operator_bindings.yaml','spec/p0/formal_obligations.yaml'})


def check_freeze(root: Path, manifest: dict) -> None:
    if manifest.get('kind') != 'ENGINEERING_CONTRACT_FREEZE_NOT_SCIENTIFIC_APPROVAL':
        raise ContractError('FREEZE_KIND_INVALID')
    if set(manifest.get('sha256',{})) != FROZEN_ARTIFACTS:
        raise ContractError('FREEZE_ARTIFACT_SET_MISMATCH')
    for relative, expected in manifest['sha256'].items():
        if digest(owned_path(root, relative).read_bytes()) != expected:
            raise ContractError(f'FROZEN_CONTRACT_CHANGED:{relative}')


def validate_ledger(root: Path, ledger: dict, schema: dict, freeze: dict) -> dict:
    """Validate this intake projection; never return a historical support label."""
    check_freeze(root, freeze)
    if schema != load_json(owned_path(root,'spec/p0/candidate_ledger.schema.json')):
        raise ContractError('SCHEMA_BINDING_MISMATCH')
    vocab=yaml.safe_load(owned_path(root,'spec/controlled_vocabularies.yaml').read_text(encoding='utf-8'))['vocabularies']
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(ledger), key=lambda e: str(e.path))
    if errors:
        raise ContractError('SCHEMA_INVALID:' + errors[0].message)
    sources = {s['source_id']: s for s in ledger['literature_sources']}
    if len(sources) != len(ledger['literature_sources']):
        raise ContractError('DUPLICATE_SOURCE_ID')
    for source in sources.values():
        if source['source_kind'] not in {'PRIMARY_DOCUMENT','RETROSPECTIVE_ACCOUNT','SCHOLARLY_SECONDARY'}:
            raise ContractError('NON_SCHOLARLY_CLAIM_SOURCE')
        actual = owned_path(root, source['relative_path']).read_bytes()
        if digest(actual) != source['sha256']:
            raise ContractError('LITERATURE_BYTES_CHANGED')
        acquisition = load_json(owned_path(root, source['acquisition_receipt']))
        if acquisition['sha256'] != source['sha256'] or acquisition['access_status'] != 'LOCAL_AVAILABLE':
            raise ContractError('ACQUISITION_RECEIPT_MISMATCH')
        if (acquisition.get('source_id') != source['source_id'] or acquisition.get('relative_path') != source['relative_path']
                or acquisition.get('expected_media') != source['media']):
            raise ContractError('ACQUISITION_RECEIPT_MISMATCH')
        if source['media']=='pdf' and len(PdfReader(owned_path(root,source['relative_path'])).pages) != source['page_count']:
            raise ContractError('PDF_PAGE_COUNT_MISMATCH')
    ids = set()
    predicates = ledger['predicate_registry']
    for claim in ledger['candidates']:
        if claim['candidate_id'] in ids:
            raise ContractError('DUPLICATE_CLAIM_ID')
        ids.add(claim['candidate_id'])
        source = sources.get(claim['source_id'])
        if source is None or source['source_kind'] == 'TERTIARY_ENCYCLOPEDIA':
            raise ContractError('NON_SCHOLARLY_CLAIM_SOURCE')
        draft=load_json(owned_path(root,claim['local_draft_receipt']))
        if draft.get('source_id') != source['source_id'] or draft.get('source_sha256') != source['sha256'] or draft.get('human_approval_granted') is not False:
            raise ContractError('DRAFT_RECEIPT_MISMATCH')
        locator = claim['locator']
        if locator['source_sha256'] != source['sha256']:
            raise ContractError('LOCATOR_SOURCE_MISMATCH')
        if locator['kind'] == 'PDF_PAGE_REGION':
            if source['media'] != 'pdf' or locator['pdf_page_index'] >= source['page_count']:
                raise ContractError('PDF_PAGE_OUT_OF_RANGE')
            x0, y0, x1, y1 = locator['region']
            if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
                raise ContractError('REGION_INVALID')
            derivative=load_json(owned_path(root, locator['derivative_receipt']))
            if derivative['source_sha256'] != source['sha256']:
                raise ContractError('DERIVATIVE_SOURCE_MISMATCH')
            page=' '.join(derivative['pages'][locator['pdf_page_index']]['raw_text'].split())
            if digest(page.encode()) != locator['normalized_page_sha256']:
                raise ContractError('TEXT_DERIVATIVE_CHANGED')
            start,end=locator['text_start'],locator['text_end']
            if not (0 <= start < end <= len(page)) or page[start:end] != locator['anchor_quote']:
                raise ContractError('TEXT_ANCHOR_MISMATCH')
            if not (0 <= locator['context_start'] <= start < end <= locator['context_end'] <= len(page)):
                raise ContractError('REVIEW_CONTEXT_INVALID')
        else:
            html = BeautifulSoup(owned_path(root, source['relative_path']).read_text(encoding='utf-8'), 'html.parser')
            matches = html.select(locator['css_selector'])
            if len(matches) != 1 or digest(matches[0].get_text(' ', strip=True).encode('utf-8')) != locator['block_sha256']:
                raise ContractError('HTML_LOCATOR_MISMATCH')
        predicate = predicates.get(claim['formalization']['predicate'])
        if predicate is None or len(claim['formalization']['arguments']) != predicate['arity']:
            raise ContractError('FORMAL_SIGNATURE_MISMATCH')
        if claim['formalization']['arguments'] != [claim['source_id'],claim['candidate_id']]:
            raise ContractError('FORMAL_ARGUMENT_BINDING_MISMATCH')
        if claim['contribution_role'] is None and claim['missing_reasons'].get('contribution_role') not in {'NOT_APPLICABLE','NOT_ASSESSED'}:
            raise ContractError('MISSING_REASON_INVALID')
        if claim['contribution_role'] is not None and claim['contribution_role'] not in vocab['contribution_role']['codes']:
            raise ContractError('CONTRIBUTION_ROLE_INVALID')
        if claim['assessment'] is not None or claim['review_status'] != 'PENDING':
            raise ContractError('INTAKE_CANNOT_GRANT_REVIEW')
    return {'execution_status': 'SUCCEEDED', 'scope': 'P0_INTAKE_PROJECTION_VALIDATED',
            'candidate_count': len(ids), 'academic_source_count': len(sources),
            'scientific_adjudication_performed': False, 'human_approval_granted': False,
            'formal_proof_performed': False}
