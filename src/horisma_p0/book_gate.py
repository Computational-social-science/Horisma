"""Draft integrity checks; fail closed until authenticated release review exists."""
import hashlib
import re


def development_export_metadata(medium):
    return {'series_title':'The Secrets of Terms','book_title':'The Secrets of Terms',
            'subtitle':'The Matthew Effect',
            'medium':medium,'intended_use':'DEVELOPMENT_PREVIEW_ONLY',
            'scientific_acceptance':False,'release_authorized':False}


def check_book(root, content, mapping, *, mode):
    if mode not in {'preview', 'release'}:
        raise ValueError('UNKNOWN_BOOK_MODE')
    if mode == 'release':
        raise ValueError('BOOK_RELEASE_BLOCKED: authenticated scientific/editorial/rights/format authorization is not implemented')
    if mapping['content_sha256'] != hashlib.sha256(content.encode()).hexdigest():
        raise ValueError('STALE_BOOK_MAP')
    paragraphs = [b for b in re.split(r'\n\s*\n', content.split('## Sources')[0].strip()) if not b.startswith('#')]
    rows = mapping['paragraphs']
    if len(rows) != len(paragraphs) or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('INCOMPLETE_PARAGRAPH_MAP')
    for paragraph, row in zip(paragraphs, rows):
        if row['text_sha256'] != hashlib.sha256(paragraph.encode()).hexdigest():
            raise ValueError('STALE_PARAGRAPH')
        refs = [n.strip() for group in re.findall(r'\[(\d+(?:,\s*\d+)*)(?:,\s*p{1,2}\.[^\]]+)?\]', paragraph) for n in group.split(',')]
        if row['sources'] != refs:
            raise ValueError('CITATION_MAP_MISMATCH')
        for source_id in refs:
            source = mapping['sources'][source_id]
            path = (root / source['path']).resolve()
            if not path.is_relative_to(root.resolve()) or not source['locator']:
                raise ValueError('INVALID_SOURCE_BINDING')
            if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
                raise ValueError('STALE_SOURCE')
    return {'mode': 'preview', 'scientific_acceptance': False,
            'release_authorized': False, 'status': 'UNREVIEWED_DEVELOPMENT_DRAFT',
            'paragraph_count': len(rows), 'content_sha256': mapping['content_sha256']}
