"""Stable research-card anchors and format views; editorial links are not evidence."""
import json
from pathlib import Path
import re
import uuid

from .research_slice import encoded, read, sha, write_new
from .book_gate import development_export_metadata


def anchors(card_id):
    digest = sha(card_id.encode())[:24]
    return {'quarto': 'sec-card-'+digest, 'footnote': 'card-'+digest,
            'logseq_uuid': str(uuid.uuid5(uuid.NAMESPACE_URL, 'https://horisma.invalid/card/'+card_id))}


def literal(text):
    return re.sub(r'([\\`*_{}\[\]<>#@])', r'\\\1', str(text)).replace('\n', ' ')


def render_views(cards):
    ids = [c['card_id'] for c in cards]
    if len(ids) != len(set(ids)): raise ValueError('DUPLICATE_PUBLICATION_CARD_ID')
    mapping = {ident: anchors(ident) for ident in ids}
    if any(link['card_ref'] not in mapping for c in cards for link in c['links']):
        raise ValueError('DANGLING_PUBLICATION_CARD_LINK')
    metadata = development_export_metadata('card-apparatus')
    qmd = ['---', 'title: '+json.dumps(metadata['book_title']),
           'subtitle: '+json.dumps(metadata['subtitle']),
           'series-title: '+json.dumps(metadata['series_title']),
           'format: html', 'number-sections: true', 'execute:', '  enabled: false', '---', '',
           'Private development preview: these are unreviewed evidence-event records. Cross-links organize the account; they do not establish support.', '']
    logseq = ['- '+metadata['book_title']+': '+metadata['subtitle']+' — evidence-event cards (private, unreviewed)']
    for c in cards:
        ident = c['card_id']; a = mapping[ident]
        qmd += ['## '+literal(c['title'])+' {#'+a['quarto']+'}', '', literal(c['proposition'])+'[^'+a['footnote']+']',
                '', '**Support scope:** '+literal(c['support_scope']), '', '**Limits:** '+literal(c['limitations']), '']
        targets = [link['card_ref'] for link in c['links']]
        backlinks = [other['card_id'] for other in cards if any(link['card_ref'] == ident for link in other['links'])]
        if targets: qmd += ['Related records: '+', '.join('@'+mapping[t]['quarto'] for t in targets)+'.', '']
        if backlinks: qmd += ['Referenced by: '+', '.join('@'+mapping[t]['quarto'] for t in backlinks)+'.', '']
        qmd += ['[^'+a['footnote']+']: Event ID '+literal(ident)+'; revision '+c['revision'][:12]+
                '. Evidence units: '+', '.join(literal(ref) for ref in c['evidence_node_refs'])+
                '. Status: '+literal(c['readiness'])+'. Original-source citations remain separate.', '']
        logseq += ['  - '+literal(c['title']), '    id:: '+a['logseq_uuid'], '    event-id:: '+ident,
                   '    card-revision:: '+c['revision'], '    - '+literal(c['proposition']),
                   '    - Limits: '+literal(c['limitations'])]
        if targets: logseq += ['    - Related: '+', '.join('(('+mapping[t]['logseq_uuid']+'))' for t in targets)]
    return '\n'.join(qmd)+'\n', '\n'.join(logseq)+'\n', mapping


def export_cards(root, cards_path):
    root, path = Path(root).resolve(), Path(cards_path).resolve()
    if not path.is_relative_to(root/'outputs/event-cards'): raise ValueError('EXTERNAL_CARD_SNAPSHOT')
    raw = read(root, path.relative_to(root)); payload = json.loads(raw)
    if path.parent.name != sha(raw): raise ValueError('CARD_SNAPSHOT_CHANGED')
    if any(sha(read(root, p)) != digest for p, digest in payload['dependencies'].items()):
        raise ValueError('STALE_PUBLICATION_CARDS')
    qmd, logseq, mapping = render_views(payload['cards'])
    metadata = development_export_metadata('card-apparatus')
    recipe = {'cards_sha256': sha(raw), 'renderer_sha256': sha(Path(__file__).read_bytes()),
              'publication_metadata': metadata}
    folder = root/'outputs/card-publication'/sha(encoded(recipe))
    for name, body in [('cards.qmd', qmd.encode()), ('logseq.md', logseq.encode()), ('anchors.json', encoded(mapping)),
                       ('manifest.json', encoded({**recipe, 'scientific_acceptance': False, 'release_authorized': False}))]:
        write_new(folder/name, body)
    return {'quarto_source': str(folder/'cards.qmd'), 'logseq_source': str(folder/'logseq.md'),
            'anchors': str(folder/'anchors.json'), 'cards': len(payload['cards']),
            'scientific_acceptance': False, 'release_authorized': False}
