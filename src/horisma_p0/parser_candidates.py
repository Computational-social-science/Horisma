"""Parser routing diagnostics, not transcript correctness or historical gold."""
import re
import pymupdf
import json


def page_kind(path,page_index):
    with pymupdf.open(path) as doc:
        page=doc[page_index];trace=page.get_texttrace()
        visible=sum(len(s['chars']) for s in trace if s.get('type') in {0,1,2})
        hidden=sum(len(s['chars']) for s in trace if s.get('type')==3)
        images=page.get_images();coverage=0.0
        for xref in {i[0] for i in images}:
            coverage+=sum((r & page.rect).get_area() for r in page.get_image_rects(xref))/page.rect.get_area()
    kind='SCAN_WITH_HIDDEN_TEXT' if coverage>=.6 and hidden>visible else ('BORN_DIGITAL' if coverage<.1 and hidden==0 else 'MIXED_OR_UNDETERMINED')
    return {'kind':kind,'visible_glyphs':visible,'hidden_glyphs':hidden,
            'image_area_fraction_capped':min(1.0,coverage),'heuristic_version':'scan-glyph-trace-0.1',
            'fidelity_qualified':False}


def coverage_diagnostic(text,required_terms):
    # Diagnostic dehyphenation never changes the retained parser output.
    normalized=' '.join(re.sub(r'-\s*\n\s*','',text).split()).casefold()
    found={term:term.casefold() in normalized for term in required_terms}
    return {'required_term_presence':found,'coverage_denominator':len(required_terms),
            'coverage_count':sum(found.values()),'complete_required_terms':bool(found) and all(found.values()),
            'scope':'RETRIEVAL_COVERAGE_NOT_FIDELITY_OR_SUPPORT'}


def docling_geometry_candidates(document,source_version_id):
    """Adapt Docling geometry explicitly; do not equate its labels with evidence."""
    from .research_slice import normalize_region,sha,encoded
    units=[]
    for item in document.get('texts',[]):
        for prov in item.get('prov',[]):
            number=prov['page_no'];page=document['pages'][str(number)];size=page['size']
            width,height=size['width'],size['height'];bbox=prov['bbox']
            if bbox['coord_origin']=='BOTTOMLEFT':
                rect=[bbox['l'],height-bbox['t'],bbox['r'],height-bbox['b']]
            elif bbox['coord_origin']=='TOPLEFT':rect=[bbox['l'],bbox['t'],bbox['r'],bbox['b']]
            else:raise ValueError('UNKNOWN_DOCLING_COORDINATE_ORIGIN')
            # Reject genuine geometry errors; allow floating-point edge noise only.
            if any(v < -1e-3 for v in rect) or rect[2]>width+1e-3 or rect[3]>height+1e-3:
                raise ValueError('DOCLING_REGION_OUT_OF_BOUNDS')
            rect=[max(0,rect[0]),max(0,rect[1]),min(width,rect[2]),min(height,rect[3])]
            text=item['text'];start,end=prov['charspan']
            if not 0<=start<end<=len(text):raise ValueError('DOCLING_CHARSPAN_INVALID')
            record={'work_version_id':source_version_id,'pdf_page_index':number-1,'docling_label':item.get('label'),
                    'item_ref':item['self_ref'],'region_pdf_points':rect,'normalized_region':normalize_region(rect,width,height),
                    'page_width_points':width,'page_height_points':height,'text':text[start:end],
                    'text_sha256':sha(text[start:end].encode()),'source_charspan':[start,end],
                    'fidelity_qualified':False,'support_assessment':None}
            record['passage_id']='horisma:parser-passage:'+sha(encoded(record));units.append(record)
    return units


def parser_report(root,folder):
    from pathlib import Path
    from .research_slice import encoded,write_new,sha,check_slice,preserve_blob
    root=Path(root).resolve();folder=Path(folder).resolve()
    if not check_slice(root,folder)['preview_eligible']:raise ValueError('STALE_SLICE')
    payload=json.loads((folder/'slice.json').read_bytes());rows=[];adapted={}
    terms={'1':['Merton','Zuckerman','Matthew'],'2':['Merton','Zuckerman','Matthew'],
           '3':['Merton','Zuckerman','interviews'],'4':['joint authorship','Zuckerman','1973'],
           '5':['Merton','Zuckerman','1968']}
    for sid in terms:
        source=payload['sources'][sid];index=payload['regions'][sid]['page_index']
        row={'source_id':sid,'page_kind':page_kind(root/source['preserved_blob']['path'],index),'parsers':{}}
        for tool in ['anymd-8.5.9','docling-2.140.0']:
            directory=root/'outputs/parser-comparison'/tool
            from .probe_artifacts import load_attempt
            try:
                attempt_id,files=load_attempt(directory,sid)
                receipt=validate_parser_attempt(files,tool,sid,source['sha256'],index)
            except (OSError,ValueError,KeyError,TypeError) as exc:
                row['parsers'][tool]={'status':'QUARANTINED_OR_UNAVAILABLE','reason':str(exc)};continue
            raw=files['document.md'];text=raw.decode('utf-8')
            result={**coverage_diagnostic(text,terms[sid]),'markdown_sha256':sha(raw),
                    'attempt_id':attempt_id,
                    'preserved_output':preserve_blob(root,raw,'PARSER_MARKDOWN_UNQUALIFIED')}
            result['preserved_operation']=preserve_blob(root,files['receipt.json'],'PARSER_OPERATION_RECORD')
            if tool.startswith('docling'):
                structured=files['document.json']
                document=json.loads(structured);units=[];quarantined=[]
                for item in document.get('texts',[]):
                    try:
                        if not item.get('prov'):raise ValueError('PROVENANCE_MISSING')
                        units.extend(docling_geometry_candidates({'pages':document['pages'],'texts':[item]},source['version_id']))
                    except (ValueError,KeyError,TypeError) as exc:
                        quarantined.append({'item_ref':item.get('self_ref'),'reason':str(exc),'disposition':'QUARANTINED_NOT_REPAIRED'})
                adapted[sid]=units;result['geometry_units']=len(units);result['quarantined_items']=quarantined
                result['preserved_structure']=preserve_blob(root,structured,'DOCLING_STRUCTURE_UNQUALIFIED')
            row['parsers'][tool]=result
        row['proposed_route']='LAYOUT_PLUS_IMAGE_OCR_CANDIDATE' if row['page_kind']['kind']=='SCAN_WITH_HIDDEN_TEXT' else 'NATIVE_LAYOUT_CANDIDATE_WITH_COVERAGE_CHECK'
        row['automatic_acceptance']=False;rows.append(row)
    report={'slice_id':folder.name,'rows':rows,'docling_passage_candidates':adapted,
            'comparison_scope':'FIVE_PURPOSEFULLY_SELECTED_PAGES_NOT_ACCURACY_BENCHMARK',
            'release_authorized':False,'scientific_acceptance':False}
    data=encoded(report);out=root/'outputs/parser-comparison'/('comparison-'+sha(data))/'report.json'
    write_new(out,data)
    return {'output':str(out),'pages':len(rows),'scientific_acceptance':False}


def validate_parser_attempt(files,tool,sid,source_sha256,page_index):
    from .research_slice import sha
    receipt=json.loads(files['receipt.json'])
    if (receipt.get('source_id')!=sid or receipt.get('source_sha256')!=source_sha256
            or receipt.get('pdf_page_index')!=page_index):raise ValueError('STALE_PARSER_SOURCE_OR_PAGE')
    name,version=tool.split('-',1)
    if receipt.get('tool')!=name or receipt.get('version')!=version:raise ValueError('WRONG_PARSER_VERSION')
    if name=='anymd':
        if receipt.get('exit_code')!=0 or receipt.get('output_sha256')!=sha(files['document.md']):raise ValueError('FAILED_OR_CHANGED_ANYMD_OUTPUT')
    else:
        if (receipt.get('status')!='success' or receipt.get('markdown_sha256')!=sha(files['document.md'])
                or receipt.get('structure_sha256')!=sha(files['document.json'])):raise ValueError('FAILED_OR_CHANGED_DOCLING_OUTPUT')
    return receipt
