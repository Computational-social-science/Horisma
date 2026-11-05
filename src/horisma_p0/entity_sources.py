"""Bounded public-name authority acquisition; subsequent builds run offline."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

import yaml

from .research_slice import encoded, preserve_blob, read, sha, write_new

CATALOG = 'spec/extensions/entity_catalog.yaml'
INDEX = 'data/intake/derived/name-authorities/index.json'


class PublicAuthorityRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        before, after = urlsplit(request.full_url), urlsplit(newurl)
        if after.scheme != 'https' or after.hostname != before.hostname:
            raise ValueError('EXTERNAL_AUTHORITY_REDIRECT')
        return super().redirect_request(request, fp, code, message, headers, newurl)


def public_json(url):
    # Public metadata only: respect the host's existing proxy configuration.
    opener = build_opener(ProxyHandler(), PublicAuthorityRedirects())
    request = Request(url, headers={'User-Agent': 'HorismaResearch/0.2 (bounded public entity metadata)'})
    with opener.open(request, timeout=20) as response:
        raw = response.read(4 * 1024 * 1024 + 1)
    if len(raw) > 4 * 1024 * 1024:
        raise ValueError('AUTHORITY_SIZE_BUDGET_EXCEEDED')
    json.loads(raw)
    return raw


def load_authority(root, record):
    raw = read(Path(root), record['blob']['path'])
    if sha(raw) != record['blob']['sha256']:
        raise ValueError('AUTHORITY_BLOB_CHANGED')
    entity = json.loads(raw)['entities'][record['qid']]
    if entity['id'] != record['qid'] or entity['lastrevid'] != record['revision_id']:
        raise ValueError('AUTHORITY_IDENTITY_OR_REVISION_CHANGED')
    return entity


def validate_authority_index(root, index, config):
    binding = index['wikipedia_binding']['blob']
    raw = read(Path(root), binding['path'])
    if sha(raw) != binding['sha256']:
        raise ValueError('WIKIPEDIA_BINDING_CHANGED')
    pages = json.loads(raw)['query']['pages'].values()
    mapping = {page['title']: page.get('pageprops', {}).get('wikibase_item') for page in pages}
    if mapping != index['wikipedia_binding']['mapping']:
        raise ValueError('WIKIPEDIA_BINDING_MAPPING_CHANGED')
    for entry in config['entities']:
        if mapping.get(entry['wikipedia_title']) != entry['wikidata_id'] or entry['wikidata_id'] not in index['entities']:
            raise ValueError('CACHED_CATALOG_BINDING_MISMATCH')
    for qid, record in index['entities'].items():
        if qid != record['qid']:
            raise ValueError('AUTHORITY_INDEX_KEY_MISMATCH')
        load_authority(root, record)


def acquire_entity_sources(root, refresh=False):
    root = Path(root).resolve()
    if (root / INDEX).is_file() and not refresh:
        index = json.loads(read(root, INDEX))
        if index['catalog_sha256'] != sha(read(root, CATALOG)):
            raise ValueError('AUTHORITY_CATALOG_CHANGED_EXPLICIT_REFRESH_REQUIRED')
        validate_authority_index(root,index,yaml.safe_load(read(root,CATALOG)))
        return {'index': INDEX, 'entities': len(index['entities']), 'network_requests': 0, 'mode': 'LOCAL_CACHE'}
    config = yaml.safe_load(read(root, CATALOG))
    records = {}
    titles = '|'.join(row['wikipedia_title'] for row in config['entities'])
    binding_url = 'https://en.wikipedia.org/w/api.php?' + urlencode({
        'action': 'query', 'prop': 'pageprops', 'titles': titles, 'format': 'json'})
    binding_raw = public_json(binding_url)
    pages = json.loads(binding_raw)['query']['pages'].values()
    bindings = {row['title']: row.get('pageprops', {}).get('wikibase_item') for row in pages}
    for row in config['entities']:
        if bindings.get(row['wikipedia_title']) != row['wikidata_id']:
            raise ValueError('WIKIPEDIA_ENTITY_BINDING_MISMATCH')
    pending = {row['wikidata_id'] for row in config['entities']}
    primary = set(pending)
    while pending:
        qid = sorted(pending)[0]; pending.remove(qid)
        if not re.fullmatch(r'Q\d+', qid) or len(records) >= 24:
            raise ValueError('ENTITY_ACQUISITION_BUDGET')
        url = 'https://www.wikidata.org/wiki/Special:EntityData/' + quote(qid) + '.json'
        raw = public_json(url); entity = json.loads(raw)['entities'][qid]
        if entity.get('id') != qid or type(entity.get('lastrevid')) is not int:
            raise ValueError('ENTITY_REVISION_REQUIRED')
        record = {'qid': qid, 'revision_id': entity['lastrevid'], 'url': url,
                  'retrieved_at': datetime.now(timezone.utc).isoformat(),
                  'blob': preserve_blob(root, raw, 'PUBLIC_ENTITY_SNAPSHOT_PRIVATE_INTAKE'),
                  'scientific_acceptance': False}
        records[qid] = record
        if qid in primary:
            for prop in ('P735', 'P734', 'P27'):
                for claim in entity.get('claims', {}).get(prop, []):
                    value = claim.get('mainsnak', {}).get('datavalue', {}).get('value')
                    other = value.get('id') if isinstance(value, dict) else None
                    if other and other not in records:
                        pending.add(other)
    index = {'version': '0.1.0', 'catalog_sha256': sha(read(root, CATALOG)), 'entities': records,
             'wikipedia_binding': {'url': binding_url,
                                   'blob': preserve_blob(root, binding_raw, 'WIKIPEDIA_ENTITY_BINDING'),
                                   'mapping': bindings},
             'scientific_acceptance': False, 'release_authorized': False}
    raw = encoded(index)
    write_new(root / 'data/intake/derived/name-authorities/snapshots' / sha(raw) / 'index.json', raw)
    target = root / INDEX; target.parent.mkdir(parents=True, exist_ok=True)
    # Local operational pointer; immutable snapshots and bytes remain available.
    import os
    import tempfile
    descriptor, temporary = tempfile.mkstemp(dir=target.parent, prefix='.authority-')
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(raw)
        os.replace(temporary, target)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return {'index': INDEX, 'entities': len(records), 'network_requests': len(records) + 1,
            'mode': 'PUBLIC_METADATA_DOWNLOAD_ONLY', 'scientific_acceptance': False}
