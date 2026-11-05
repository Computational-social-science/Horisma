"""Critical-token and cross-column diagnostics over source-bound parser units."""
import json
import re
from statistics import median
from pathlib import Path
import yaml
import pymupdf
from .research_slice import read,encoded,sha,write_new,preserve_blob,check_slice
from .parser_candidates import docling_geometry_candidates,validate_parser_attempt
from .probe_artifacts import load_attempt
from .fidelity import ocr_region,locate_text_block


def diagnostic_text(text):
    return ' '.join(re.sub(r'-\s*\n\s*','',text).split())


def critical_differences(texts):
    texts=[diagnostic_text(t) for t in texts]
    missing=any(not t for t in texts)
    texts=[t for t in texts if t]
    numbers=[re.findall(r'\d+',t) for t in texts]
    names=[re.findall(r'\b(?:Harriet|Harniet)(?: A\.)? Zuckerman\b|\bRobert K\. Merton\b',t) for t in texts]
    flags=['MISSING_TEXT_CHANNEL'] if missing else []
    if len({tuple(x) for x in numbers})>1:flags.append('CRITICAL_NUMBER_DISAGREEMENT')
    if len({tuple(x) for x in names})>1:flags.append('CRITICAL_NAME_DISAGREEMENT')
    return flags


def expand_region(rect,width,height,padding=8):
    return [max(0,rect[0]-padding),max(0,rect[1]-padding),min(width,rect[2]+padding),min(height,rect[3]+padding)]


def wide_column_risk(width,median_text_width,page_width,label):
    return label=='text' and median_text_width/page_width<.45 and width>median_text_width*1.6


def open_context_flags(text):
    flags=[]
    if text.count('(')>text.count(')'):flags.append('OPEN_PARENTHESIS_AT_UNIT_BOUNDARY')
    if text.count('"')%2 or text.count('\u201c')!=text.count('\u201d'):flags.append('OPEN_QUOTATION_AT_UNIT_BOUNDARY')
    return flags


def run_layout_audit(root,folder,model_dir):
    root=Path(root).resolve();folder=Path(folder).resolve()
    if not check_slice(root,folder)['preview_eligible']:raise ValueError('STALE_SLICE')
    payload=json.loads((folder/'slice.json').read_bytes())
    config_data=read(root,'spec/extensions/historical_layout_checks.yaml');config=yaml.safe_load(config_data)
    parsed={};attempts={};rows=[]
    for sid in {t['source_id'] for t in config['targets']}:
        attempt,files=load_attempt(root/'outputs/parser-comparison/docling-2.140.0',sid)
        source=payload['sources'][sid];index=payload['regions'][sid]['page_index']
        validate_parser_attempt(files,'docling-2.140.0',sid,source['sha256'],index)
        document=json.loads(files['document.json']);units=[]
        for item in document['texts']:
            try:units.extend(docling_geometry_candidates({'pages':document['pages'],'texts':[item]},source['version_id']))
            except (ValueError,KeyError,TypeError):continue  # Invalid units remain excluded, never repaired here.
        parsed[sid]=units;attempts[sid]=attempt
    for target in config['targets']:
        sid=target['source_id'];source=payload['sources'][sid]
        anchor=diagnostic_text(target['anchor'])
        units=[u for u in parsed[sid] if (diagnostic_text(u['text'])==anchor if target.get('exact') else anchor in diagnostic_text(u['text']))]
        if len(units)!=1:
            rows.append({'id':target['id'],'source_id':sid,'status':'ABSTAINED_AMBIGUOUS_OR_MISSING_UNIT','matches':len(units),'scientific_acceptance':False});continue
        unit=units[0];path=root/source['preserved_blob']['path']
        with pymupdf.open(path) as doc:
            page=doc[unit['pdf_page_index']]
            blocks=page.get_text('blocks')
            widths=[b[2]-b[0] for b in blocks if len(b[4])>=80]
            typical=median(widths) if widths else page.rect.width
            actual_width,actual_height=page.rect.width,page.rect.height
        width=unit['region_pdf_points'][2]-unit['region_pdf_points'][0]
        flags=open_context_flags(unit['text'])
        if wide_column_risk(width,typical,unit['page_width_points'],unit['docling_label']):flags.append('POTENTIAL_CROSS_COLUMN_MERGE')
        record={'id':target['id'],'source_id':sid,'unit':unit,'median_native_text_block_width':typical,
                'flags':flags,'channel_independence':'Docling and repeated OCR share RapidOCR weights; not independent model corroboration.',
                'scientific_acceptance':False,'fidelity_qualified':False}
        try:
            comparison=ocr_region(path,unit['pdf_page_index'],unit['region_pdf_points'],model_dir)
            record['comparison_attempts']=[comparison]
            if not comparison['image_text'].strip():
                padded=expand_region(unit['region_pdf_points'],actual_width,actual_height)
                record['retry_reason']='EMPTY_IMAGE_TEXT_TIGHT_REGION_ONE_CONTEXT_EXPANSION'
                comparison=ocr_region(path,unit['pdf_page_index'],padded,model_dir)
                record['comparison_attempts'].append(comparison)
            record['comparison']=comparison
            record['flags']+=critical_differences([comparison['extracted_text'],comparison['image_text'],unit['text']])
            record['status']='COMPARISON_COMPLETED_UNQUALIFIED'
            record['comparison_blob']=preserve_blob(root,encoded(record['comparison_attempts']),'LAYOUT_CRITICAL_TOKEN_COMPARISON')
        except (OSError,ValueError,ImportError,RuntimeError) as exc:
            record.update(status='ABSTAINED_COMPARISON_FAILED',error=type(exc).__name__+': '+str(exc))
        rows.append(record)
        print(target['id'],record['status'],record['flags'],flush=True)
    by_id={r['id']:r for r in rows};links=[]
    for link in config['continuations']:
        a,b=by_id[link['from']],by_id[link['to']]
        links.append({**link,'from_passage':a.get('unit',{}).get('passage_id'),'to_passage':b.get('unit',{}).get('passage_id'),
                      'scientific_acceptance':False,'limitation':'Physical and textual adjacency is a candidate relation, not proven semantic continuity.'})
    for query in config['native_retrievals']:
        source=payload['sources'][query['source_id']];path=root/source['preserved_blob']['path'];index=payload['regions'][query['source_id']]['page_index']
        record={**query,'scientific_acceptance':False,'fidelity_qualified':False}
        try:
            rect=locate_text_block(path,index,query['anchor'])
            comparison=ocr_region(path,index,rect,model_dir)
            record.update(rect=rect,source_sha256=source['sha256'],page_index=index,comparison=comparison,
                          status='RETRIEVED_CONTINUATION_CANDIDATE',comparison_blob=preserve_blob(root,encoded(comparison),'CONTINUATION_RETRIEVAL_COMPARISON'))
        except (OSError,ValueError,ImportError,RuntimeError) as exc:record.update(status='ABSTAINED',error=str(exc))
        links.append(record)
    result={'slice_id':folder.name,'config_sha256':sha(config_data),'operator_sha256':sha(Path(__file__).read_bytes()),
            'parser_attempts':attempts,'checks':rows,'continuations':links,
            'scientific_acceptance':False,'fidelity_qualified':False,'release_authorized':False}
    assertion_checks={
        'DISPLAYED_AUTHOR':['merton-byline'],
        'RETROSPECTIVE_ACKNOWLEDGER':['merton-retrospective-footnote'],
        'ACKNOWLEDGED_JOINT_AUTHORSHIP_ENTITLEMENT':['merton-retrospective-footnote']}
    result['assertion_projections']=[]
    for assertion in payload['assertions']:
        role=assertion['role_proposed']
        if role not in {*assertion_checks,'EMPIRICAL_MATERIAL_CONTRIBUTOR'}:raise ValueError('UNMAPPED_ASSERTION_DIAGNOSTIC_ROLE')
        selected=assertion_checks.get(role,['aaas-preview-contribution'] if assertion['work_version_id']==payload['sources']['1']['version_id'] else ['merton-opening-interview-material'])
        result['assertion_projections'].append({'assertion_id':assertion['assertion_id'],'assertion_revision':assertion['revision'],
            'diagnostic_refs':selected,'scientific_acceptance':False,'assessment_unchanged':True})
    result['task_projections']=[{'task_id':t['task_id'],'task_revision':t['revision'],
        'diagnostic_refs':[r['id'] for r in rows if r['source_id'] in t['sources']],
        'missing_source_diagnostics':sorted(set(t['sources'])-{r['source_id'] for r in rows}),
        'gold_unchanged':True,'historical_score':None} for t in payload['tasks']]
    data=encoded(result);out=folder/'layout-audit'/sha(data)/'report.json';write_new(out,data)
    return {'output':str(out),'targets':len(rows),'comparisons_completed':sum(r['status']=='COMPARISON_COMPLETED_UNQUALIFIED' for r in rows),
            'continuations':len(links),'scientific_acceptance':False}
