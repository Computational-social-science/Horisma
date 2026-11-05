"""Source-derived, explicitly normalized passage derivatives for chapter arguments."""
import re
import xml.etree.ElementTree as ET
import pymupdf


def materialize_passages(root,mapping,sources):
    from .research_slice import sha,encoded
    result={}
    for unit_id,spec in mapping.get('evidence_units',{}).items():
        source=sources[spec['source_id']];path=root/source['preserved_blob']['path']
        if 'page_index' in spec:
            with pymupdf.open(path) as doc:text=doc[spec['page_index']].get_text()
            derivative=' '.join(text.split())
            matches=list(re.finditer(re.escape(spec['anchor']),derivative,re.I))
            if len(matches)!=1:raise ValueError('UNIQUE_PASSAGE_ANCHOR_REQUIRED:'+unit_id)
            start=max(0,matches[0].start()-250);end=min(len(derivative),matches[0].end()+2000)
            locator={'pdf_page_index':spec['page_index'],'anchor':spec['anchor'],'anchor_matches':len(matches)}
        else:
            tree=ET.parse(path)
            sections=[s for s in tree.findall('./body/sec') if s.findtext('title')==spec['section']]
            if len(sections)!=1:raise ValueError('UNIQUE_JATS_SECTION_REQUIRED')
            derivative=' '.join(' '.join(sections[0].itertext()).split())
            start=0;end=len(derivative);locator={'jats_section':spec['section']}
        record={'unit_id':unit_id,'work_version_id':source['version_id'],'source_sha256':source['sha256'],
                'locator':locator,'derivative_sha256':sha(derivative.encode()),
                'normalization':'whitespace-collapse-only-0.1','start':start,'end':end,
                'offset_unit':'Unicode code points in exact normalized derivative',
                'text':derivative[start:end],'text_sha256':sha(derivative[start:end].encode()),
                'fidelity':'UNQUALIFIED','scientific_acceptance':False}
        record['passage_id']='horisma:passage:'+sha(encoded(record));result[unit_id]=record
    for paragraph in mapping['paragraphs']:
        if any(key not in result for key in paragraph.get('evidence_unit_refs',[])):raise ValueError('DANGLING_CHAPTER_PASSAGE')
    return result
