"""Shared semantic master; rendering does not qualify historical assertions."""
import re
def make_master(story, bibliography):
    ids=[entry['citation_id'] for entry in bibliography['entries'].values()]
    if len(ids)!=len(set(ids)):
        raise ValueError('DUPLICATE_BIBLIOGRAPHIC_CITATION_ID')
    chapters=[]
    for order,chapter in enumerate(story['chapters'],1):
        source=chapter['source_id']
        if source not in bibliography['entries']:
            raise ValueError('BIBLIOGRAPHIC_ENTRY_REQUIRED')
        if any(not isinstance(value,str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]*',value) for value in [chapter['record_id'],bibliography['entries'][source]['citation_id']]):
            raise ValueError('STABLE_XML_SAFE_IDS_REQUIRED')
        chapters.append({key:chapter[key] for key in ['record_id','source_id','heading','body','distinction','revision','open_question','date','locator','source_sha256']})
        chapters[-1].update(order=order,chapter_id='chapter-'+chapter['record_id'],
            evidence_id='evidence-'+chapter['record_id'],citation_id=bibliography['entries'][source]['citation_id'])
    if len({c['record_id'] for c in chapters})!=len(chapters):
        raise ValueError('DUPLICATE_PUBLICATION_CHAPTER')
    return {'version':'0.1.0','snapshot':story['snapshot'],'guide_version':story['guide_version'],
            'chapters':chapters,'bibliography':bibliography,'release_authorized':False}
