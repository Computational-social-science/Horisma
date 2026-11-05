"""Shared private research slice; deterministic artifacts and explicit eligibility."""
import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path
import yaml
from .region_bindings import region_candidate, bind_assertion, bind_task

MAP = 'spec/examples/matthew_chapter_one_map.json'
PEOPLE = 'data/intake/derived/scientist-profiles-v0.1/records.jsonl'
TASKS = 'data/benchmarks/development/matthew-role-provenance-v0.1/tasks.jsonl'
CHAPTER = 'docs/research/book/MATTHEW_CHAPTER_ONE_EN.md'
CONFIG = 'spec/extensions/research_slice.yaml'


def encoded(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False,indent=2).encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(root,path):
    resolved=(root/path).resolve()
    if not resolved.is_relative_to(root.resolve()):raise ValueError('EXTERNAL_ASSET')
    return resolved.read_bytes()


def write_new(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_bytes()!=data:raise ValueError('IMMUTABLE_ARTIFACT_CONFLICT')
        return
    descriptor,name=tempfile.mkstemp(prefix='.pending-',dir=path.parent)
    temp=Path(name)
    try:
        with os.fdopen(descriptor,'wb') as stream:
            stream.write(data);stream.flush();os.fsync(stream.fileno())
        try:
            if os.name=='nt':os.rename(temp,path)  # Windows rename refuses an existing target; exFAT has no hard links.
            else:os.link(temp,path)
        except FileExistsError:
            if path.read_bytes()!=data:raise ValueError('IMMUTABLE_ARTIFACT_CONFLICT')
    finally:temp.unlink(missing_ok=True)


def normalize_region(rect,width,height):
    if len(rect)!=4 or any(type(x) not in (int,float) or not math.isfinite(x) for x in [*rect,width,height]):
        raise ValueError('INVALID_COORDINATES')
    x0,y0,x1,y1=rect
    if not (width>0 and height>0 and 0<=x0<x1<=width and 0<=y0<y1<=height):raise ValueError('REGION_OUT_OF_BOUNDS')
    return [x0/width,y0/height,x1/width,y1/height]


def role_projection(role):
    if role=='DISPLAYED_AUTHOR':return {'record_kind':'CONTRIBUTION','contribution_role':'AUTHORSHIP'}
    if role=='EMPIRICAL_MATERIAL_CONTRIBUTOR':return {'record_kind':'CONTRIBUTION','contribution_role':'EMPIRICAL_BASIS'}
    if role in {'RETROSPECTIVE_ACKNOWLEDGER','ACKNOWLEDGED_JOINT_AUTHORSHIP_ENTITLEMENT'}:
        return {'record_kind':'AUTHORSHIP_ACKNOWLEDGMENT','contribution_role':None}
    raise ValueError('UNMAPPED_ROLE')


def preserve_blob(root,data,kind):
    digest=sha(data)
    relative=Path('data/intake/derived/evidence-vault/sha256')/digest[:2]/digest
    write_new(Path(root)/relative,data)
    return {'path':relative.as_posix(),'sha256':digest,'bytes':len(data),'kind':kind,
            'disclosure':'PRIVATE','redistribution_authorized':False}


def eligibility(checks):
    required={'integrity','fidelity','support','reviewer','rights','editorial','formats'}
    if set(checks)!=required or any(type(v) is not bool for v in checks.values()):raise ValueError('EXPLICIT_ELIGIBILITY_CHECKS_REQUIRED')
    science=all(checks[k] for k in ['integrity','fidelity','support','reviewer'])
    return {'preview_eligible':checks['integrity'],'scientific_eligible':science,
            'release_eligible':science and all(checks[k] for k in ['rights','editorial','formats']),
            'blockers':[k for k in sorted(required) if not checks[k]]}


def inputs(root):
    mapping=json.loads(read(root,MAP));config=yaml.safe_load(read(root,CONFIG))
    people=[json.loads(s) for s in read(root,PEOPLE).decode().splitlines()]
    tasks=[json.loads(s) for s in read(root,TASKS).decode().splitlines()]
    return mapping,config,people,tasks


def build_slice(root):
    root=Path(root).resolve()
    base_paths=[MAP,PEOPLE,TASKS,CHAPTER,CONFIG,'spec/controlled_vocabularies.yaml',
                'src/horisma_p0/research_slice.py','src/horisma_p0/region_bindings.py','src/horisma_p0/fidelity.py',
                'src/horisma_p0/research_passages.py','src/horisma_p0/book_gate.py']
    initial_dependencies={p:sha(read(root,p)) for p in base_paths}
    mapping,config,people,tasks=inputs(root)
    import pymupdf
    chapter_text=(root/CHAPTER).read_text(encoding='utf-8')
    if sha(chapter_text.encode())!=mapping['content_sha256']:raise ValueError('STALE_CHAPTER_MAP')
    from .book_gate import check_book
    check_book(root,chapter_text,mapping,mode='preview')
    sources={};regions={}
    for alias,source in mapping['sources'].items():
        work_id=config['source_aliases'][alias]
        original=read(root,source['path'])
        if sha(original)!=source['sha256']:raise ValueError('STALE_SOURCE:'+alias)
        sources[alias]={'work_id':work_id,'version_id':work_id+'@'+source['sha256'],**source}
        sources[alias]['preserved_blob']=preserve_blob(root,original,'SOURCE_VERSION')
        if alias not in {'1','2','3','4','5'}:continue
        immutable_source={**source,'path':sources[alias]['preserved_blob']['path']}
        region=region_candidate(root,alias,immutable_source)
        region['source']=source
        with pymupdf.open(root/immutable_source['path']) as doc:
            page=doc[region['page_index']]
            width,height=page.rect.width,page.rect.height
            png=page.get_pixmap(matrix=pymupdf.Matrix(2,2),clip=pymupdf.Rect(region['region_pdf_points']),alpha=False).tobytes('png')
        if sha(png)!=region['render_sha256']:raise ValueError('RENDER_REPLAY_MISMATCH')
        region['render_blob']=preserve_blob(root,png,'PRIVATE_REGION_RENDER')
        region['native_text_blob']=preserve_blob(root,region['text'].encode(),'NATIVE_TEXT_UNQUALIFIED')
        region.update(page_width_points=width,page_height_points=height,
                      normalized_region=normalize_region(region['region_pdf_points'],width,height),
                      coordinate_conversion=config['coordinate_conversion'])
        region['work_version_id']=sources[alias]['version_id']
        # Preserve exact text ranges in this derivative, not silently corrected OCR.
        region['sentences']=[{'start':m.start(),'end':m.end(),'text':m.group(),
                              'text_sha256':sha(m.group().encode()),'context_status':'CANDIDATE_UNQUALIFIED'}
                             for m in re.finditer(r'[^.!?]+(?:[.!?]+|$)',region['text']) if m.group().strip()]
        region['region_id']='horisma:region:'+sha(encoded({k:v for k,v in region.items() if k!='region_id'}))
        regions[alias]=region
    projected_people=[];assertions=[]
    for person in people:
        if person['concept_family_id']!=config['concept_family_id']:raise ValueError('PERSON_FAMILY_MISMATCH')
        person=dict(person);person['assertion_refs']=[]
        for a in person.pop('contributions'):
            binding=bind_assertion(a,regions[a['source_id']])
            binding.update(person_id=person['person_id'],**role_projection(a['role_proposed']))
            binding['work_version_id']=sources[a['source_id']]['version_id']
            binding['passage_spans']=regions[a['source_id']]['sentences']
            binding['span_review']='CANDIDATE_SENTENCE_SET_NOT_MINIMAL_ENTAILMENT'
            binding['revision']=sha(encoded(binding))
            person['assertion_refs'].append({'id':a['assertion_id'],'revision':binding['revision']})
            assertions.append(binding)
        person['profile']='PARTIAL_DEVELOPMENT_PERSON_0.2'
        person['revision']=sha(encoded(person));projected_people.append(person)
    projected_tasks=[]
    for task in tasks:
        if task['split']!='DEVELOPMENT_ONLY' or task['concept_family_id']!=config['concept_family_id']:
            raise ValueError('TASK_FAMILY_SPLIT_INVALID')
        if task['gold_answer'] is not None or task['score'] is not None:raise ValueError('UNQUALIFIED_GOLD')
        t=dict(task);t['region_refs']=bind_task(task,regions)
        t['work_version_refs']=[sources[sid]['version_id'] for sid in task['sources']]
        t['revision']=sha(encoded(t));projected_tasks.append(t)
    ids=[p['person_id'] for p in projected_people]+[a['assertion_id'] for a in assertions]+[t['task_id'] for t in projected_tasks]
    if len(ids)!=len(set(ids)):raise ValueError('DUPLICATE_ASSET_ID')
    dependencies={**initial_dependencies,**{s['path']:s['sha256'] for s in mapping['sources'].values()}}
    if any(sha(read(root,p))!=h for p,h in dependencies.items()):raise ValueError('INPUTS_CHANGED_DURING_BUILD')
    from .research_passages import materialize_passages
    passages=materialize_passages(root,mapping,sources)
    result={'version':'0.2.1','profile':'PRIVATE_DEVELOPMENT_SLICE','config':config,'sources':sources,
            'regions':regions,'people':projected_people,'assertions':assertions,'tasks':projected_tasks,
            'chapter_passages':passages,
            'chapter':{'path':CHAPTER,'text_sha256':mapping['content_sha256'],
                       'normalization':'universal-newline-read-text-0.1','paragraphs':mapping['paragraphs']},
            'dependencies':dependencies,'release_authorized':False}
    data=encoded(result);folder=root/'outputs/research-slices'/sha(data)
    write_new(folder/'slice.json',data)
    head=root/'ops/state/research-slice-head.json';head.parent.mkdir(parents=True,exist_ok=True)
    descriptor,temp=tempfile.mkstemp(prefix='.head-',dir=head.parent)
    with os.fdopen(descriptor,'wb') as stream:
        stream.write(encoded({'slice':folder.relative_to(root).as_posix(),'sha256':sha(data)}));stream.flush();os.fsync(stream.fileno())
    os.replace(temp,head)
    return folder


def check_slice(root,folder):
    root=Path(root).resolve();folder=Path(folder).resolve()
    if not folder.is_relative_to(root/'outputs/research-slices'):raise ValueError('EXTERNAL_SLICE')
    data=(folder/'slice.json').read_bytes();payload=json.loads(data)
    if folder.name!=sha(data):raise ValueError('CORRUPT_SLICE')
    changed=[p for p,h in payload['dependencies'].items() if not (root/p).is_file() or sha(read(root,p))!=h]
    for source in payload['sources'].values():
        blob=source.get('preserved_blob')
        if blob is None:
            changed.append('MISSING_PRESERVED_SOURCE:'+source['work_id']);continue
        if not (root/blob['path']).is_file() or sha(read(root,blob['path']))!=blob['sha256']:changed.append(blob['path'])
    for region in payload['regions'].values():
        for key in ['render_blob','native_text_blob']:
            blob=region.get(key)
            if blob is None:
                changed.append('MISSING_REGION_BLOB:'+key);continue
            if not (root/blob['path']).is_file() or sha(read(root,blob['path']))!=blob['sha256']:changed.append(blob['path'])
    checks,receipt_errors=qualified_receipts(root,folder,payload)
    checks['integrity']=not changed
    return {'slice_id':folder.name,'changed_dependencies':changed,
            'affected_projections':['people','tasks','chapter'] if changed else [],
            'checks':checks,'receipt_errors':receipt_errors,**eligibility(checks)}


def qualified_receipts(root,folder,payload):
    """Trust only enrolled, task-qualified producers and context-bound artifacts."""
    checks=dict.fromkeys(['integrity','fidelity','support','reviewer','rights','editorial','formats'],False)
    errors={};registry=yaml.safe_load(read(root,'spec/extensions/research_producers.yaml'))
    bundle_path=Path(folder)/'review-bundle.json'
    if not bundle_path.exists():return checks,{'bundle':'MISSING_REVIEW_BUNDLE'}
    bundle=json.loads(bundle_path.read_bytes())
    context={'slice_id':Path(folder).name,'dependencies_sha256':sha(encoded(payload['dependencies']))}
    for gate in set(checks)-{'integrity'}:
        try:
            receipt=bundle[gate]
            producer=registry['producers'][receipt['producer']]
            if receipt['context']!=context or receipt['gate']!=gate or receipt['status']!='SATISFIED':raise ValueError('STALE_OR_UNSATISFIED_RECEIPT')
            if gate not in producer['qualified_gates']:raise ValueError('PRODUCER_NOT_QUALIFIED_FOR_GATE')
            if sha(read(root,producer['code_path']))!=producer['code_sha256']:raise ValueError('PRODUCER_CODE_CHANGED')
            qualification=producer['qualification']
            qualification_data=read(root,qualification['path'])
            if sha(qualification_data)!=qualification['sha256']:raise ValueError('QUALIFICATION_CHANGED')
            qualified=json.loads(qualification_data)
            if qualified.get('status')!='QUALIFIED' or qualified.get('profile')!=payload['profile'] or gate not in qualified.get('qualified_gates',[]):
                raise ValueError('QUALIFICATION_SCOPE_MISMATCH')
            if qualified.get('producer_code_sha256')!=producer['code_sha256']:raise ValueError('QUALIFICATION_CODE_MISMATCH')
            if not receipt['artifacts']:raise ValueError('EVIDENCE_ARTIFACTS_REQUIRED')
            for artifact in receipt['artifacts']:
                if sha(read(root,artifact['path']))!=artifact['sha256']:raise ValueError('EVIDENCE_ARTIFACT_CHANGED')
            checks[gate]=True
        except (KeyError,ValueError,TypeError,OSError) as exc:errors[gate]=str(exc)
    return checks,errors


def run_ocr(root,folder,model_dir):
    from .fidelity import ocr_region
    from difflib import unified_diff
    if not check_slice(root,folder)['preview_eligible']:raise ValueError('STALE_SLICE')
    payload=json.loads((Path(folder)/'slice.json').read_bytes());receipts={}
    for sid,region in payload['regions'].items():
        try:
            source=payload['sources'][sid]
            parts=[ocr_region(Path(root)/source['preserved_blob']['path'],region['page_index'],rect,model_dir)
                   for rect in region['selected_block_regions']]
            from .fidelity import compare_text
            image_text='\n'.join(part['image_text'] for part in parts)
            receipt={'source_sha256':source['sha256'],'parts':parts,'extracted_text':region['text'],
                     'image_text':image_text,'comparison':compare_text(region['text'],image_text),
                     'comparison_policy':'selected-block-order-not-union-reading-order-0.2.0'}
            receipt['execution_status']='SUCCEEDED'
            receipt['diff']=list(unified_diff(receipt['extracted_text'].splitlines(),receipt['image_text'].splitlines(),fromfile='embedded',tofile='image_ocr'))
        except (ValueError,OSError,ImportError,RuntimeError) as exc:
            receipt={'execution_status':'FAILED','error':type(exc).__name__+': '+str(exc)}
        receipt.update(region_id=region['region_id'],slice_id=Path(folder).name,qualified_for_acceptance=False)
        receipt['preserved_blob']=preserve_blob(root,encoded(receipt),'OCR_COMPARISON_UNQUALIFIED')
        receipts[sid]=receipt
    output=encoded({'slice_id':Path(folder).name,'receipts':receipts,'qualification':'UNQUALIFIED'})
    path=Path(folder)/'ocr'/sha(output)/'receipts.json';write_new(path,output)
    return path
