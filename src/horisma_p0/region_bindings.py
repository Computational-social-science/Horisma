"""Private regional candidate credentials; rendering is not fidelity acceptance."""
import hashlib
import json
import re
import pymupdf
from .fidelity import locate_text_block
from .development_packets import ANCHORS


def digest(value):
    return hashlib.sha256(value).hexdigest()


def region_candidate(root, sid, source):
    path=(root/source['path']).resolve()
    if not path.is_relative_to(root.resolve()) or digest(path.read_bytes()) != source['sha256']:
        raise ValueError('STALE_OR_EXTERNAL_SOURCE')
    page_index=int(re.search(r'PDF index(\d+)',source['locator'])[1])
    anchors={
        '1':[ANCHORS[sid],'16 OCTOBER 1964'],
        '3':['The Matthew Effect in Science','Robert K. Merton','This paper develops'],
    }.get(sid,[ANCHORS[sid]])
    parts=[locate_text_block(path,page_index,anchor) for anchor in anchors]
    rect=[min(p[0] for p in parts),min(p[1] for p in parts),max(p[2] for p in parts),max(p[3] for p in parts)]
    with pymupdf.open(path) as doc:
        page=doc[page_index]; clip=pymupdf.Rect(rect)
        blocks=page.get_text('blocks')
        selected=[next(b for b in blocks if anchor in b[4])[4] for anchor in anchors]
        text='\n'.join(selected)
        png=page.get_pixmap(matrix=pymupdf.Matrix(2,2),clip=clip,alpha=False).tobytes('png')
    record={'type':'REGION_FIDELITY_CANDIDATE','source_id':sid,'source':source,
            'page_index':page_index,'region_pdf_points':rect,'coordinate_origin':'TOP_LEFT',
            'render_sha256':digest(png),'render_scale':2,'text':text,'text_sha256':digest(text.encode()),
            'extractor_version':pymupdf.VersionBind,'independent_ocr_receipt':None,
            'context_selection_version':'required-blocks-union-0.2.0','required_context_anchors':anchors,
            'selected_block_regions':parts,
            'selected_native_blocks':selected,'native_extraction_policy':'selected-blocks-in-declared-order-0.2.0',
            'fidelity_status':'UNQUALIFIED','scientific_acceptance':False,
            'missing':['INDEPENDENT_IMAGE_TEXT_COMPARISON','QUALIFIED_FIDELITY_REVIEW'],
            'redistribution_authorized':False}
    record['region_id']='horisma:region:'+digest(json.dumps(record,sort_keys=True).encode())
    return record


def bind_assertion(assertion, region):
    if assertion['source_id'] != region['source_id'] or assertion['source_binding'] != region['source']:
        raise ValueError('ASSERTION_REGION_SOURCE_MISMATCH')
    return {'assertion_id':assertion['assertion_id'],
            'assertion_sha256':digest(json.dumps(assertion,sort_keys=True).encode()),
            'proposition':assertion['proposition'],'role_proposed':assertion['role_proposed'],
            'region_id':region['region_id'],'region_text_sha256':region['text_sha256'],
            'relation':'CANDIDATE_SUPPORT','support_assessment':None,
            'scientific_acceptance':False,'missing':['QUALIFIED_FIDELITY','QUALIFIED_PASSAGE_SUPPORT']}


def bind_task(task, regions):
    for sid, source in task['sources'].items():
        if sid not in regions or not isinstance(source, dict) or source != regions[sid]['source']:
            raise ValueError('STALE_TASK_REGION_SOURCE')
    return [regions[sid]['region_id'] for sid in task['sources']]


def diagnostic_flags(*, byline_only, automatic_miscredit, citations, allowed_sources,
                     interview_present, denies_interview):
    """Typed development controls, not a natural-language judge."""
    flags=[]
    if byline_only and automatic_miscredit: flags.append('T07_BYLINE_TO_MISCREDIT')
    if not set(citations).issubset(set(allowed_sources)): flags.append('T06_CONTEXT_CONTAMINATION')
    if interview_present and denies_interview: flags.append('CONTRIBUTION_FALSE_ABSTENTION')
    return flags
