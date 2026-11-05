"""Frozen literal-preservation screen for a different existing local visual backend."""
import json
import time
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import build_opener,ProxyHandler
import pymupdf
from PIL import ImageFont
from .local_documents import NoModelRedirects
from .model_screen import request_json
from .correction_workflow import visual_transcript,save_report
from .research_slice import read,sha,check_slice
from .literal_controls import render_control,screen_passed


def run_visual_challenge(root,folder,audit_path):
    root=Path(root).resolve();folder=Path(folder).resolve();audit_path=Path(audit_path).resolve()
    if not check_slice(root,folder)['preview_eligible']:raise ValueError('STALE_SLICE')
    if not audit_path.is_relative_to(folder/'layout-audit'):raise ValueError('EXTERNAL_AUDIT')
    audit_raw=audit_path.read_bytes();audit=json.loads(audit_raw)
    if audit_path.parent.name!=sha(audit_raw) or audit['slice_id']!=folder.name:raise ValueError('AUDIT_BINDING_MISMATCH')
    raw=read(root,'spec/examples/visual_literal_challenge.json');config=json.loads(raw)
    cases=config['cases']
    if len({c['id'] for c in cases})!=len(cases) or not all(c.get('synthetic') for c in cases):raise ValueError('INVALID_CONTROL_CORPUS')
    if len(cases)!=config['policy']['required_matches'] or not cases:raise ValueError('INVALID_CONTROL_COUNT')
    # The shared transcriber currently enforces a 45-second request budget.
    if config['policy']['request_timeout_seconds']!=45 or config['policy']['retries']!=0 or config['policy']['stop_on_first_failure'] is not True:raise ValueError('UNSUPPORTED_SCREEN_POLICY')
    font_path=Path(config['font']);font=ImageFont.truetype(str(font_path),config['font_size'])
    images=[render_control(c,config,font) for c in cases]  # Validate every fixture before inference.
    out=folder/'visual-challenges'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');out.mkdir(parents=True,exist_ok=False)
    report={'slice_id':folder.name,'audit_sha256':sha(audit_raw),'corpus_sha256':sha(raw),
            'operator_sha256':sha(Path(__file__).read_bytes()),'transcriber_sha256':sha(read(root,'src/horisma_p0/correction_workflow.py')),
            'control_helper_sha256':sha(read(root,'src/horisma_p0/literal_controls.py')),
            'font_sha256':sha(font_path.read_bytes()),'policy':config['policy'],'controls':[],
            'real_regions':[],'historical_qualification':False,'transcription_accepted':False,'release_authorized':False,
            'phase':'MODEL_DISCOVERY','events':[]}
    opener=build_opener(ProxyHandler({}),NoModelRedirects());base='http://127.0.0.1:11434';model='qwen3.8:27b'
    lock=root/'ops/state/research-model-screen.lock';lock.parent.mkdir(parents=True,exist_ok=True)
    lease=lock.open('x');owned=False
    try:
        lease.write(str(out));lease.flush()
        if json.loads(request_json(opener,base+'/api/ps')).get('models'):raise ValueError('OTHER_MODEL_ACTIVE_NO_PREEMPTION')
        show=json.loads(request_json(opener,base+'/api/show',{'model':model}))
        if 'vision' not in show.get('capabilities',[]) or not show.get('license'):raise ValueError('VISION_OR_LICENSE_METADATA_MISSING')
        tags=json.loads(request_json(opener,base+'/api/tags'))['models']
        identity=next(t for t in tags if t['name']==model)
        report['model_identity']={'tag':model,'digest':identity['digest'],'details':show.get('details'),
                                  'license_sha256':sha(show['license'].encode()),'identity_scope':'SERVER_DECLARED; model tag is not lineage proof'}
        report['phase']='MODEL_WARMUP';save_report(out,report);owned=True
        started=time.monotonic()
        try:
            request_json(opener,base+'/api/generate',{'model':model,'prompt':'','stream':False,'keep_alive':'5m'},config['policy']['warmup_timeout_seconds'])
        finally:
            report['events'].append({'phase':'MODEL_WARMUP','elapsed_seconds':time.monotonic()-started})
        report['phase']='SYNTHETIC_CONTROLS'
        for case,png in zip(cases,images):
            row=visual_transcript(opener,model,png,root)
            row.update(id=case['id'],synthetic=True,expected=case['text'])
            row['literal_match']=isinstance(row.get('transcript'),str) and ' '.join(row['transcript'].split())==case['text']
            report['controls'].append(row);save_report(out,report)
            print(case['id'],row['literal_match'],flush=True)
            if not row['literal_match']:break
        passed=screen_passed(report['controls'],config['policy']['required_matches'])
        report['screen_status']='PASSED_DIAGNOSTIC_ONLY' if passed else 'FAILED_OR_INCOMPLETE'
        report['unrun_controls']=[c['id'] for c in cases[len(report['controls']):]]
        if passed:
            report['phase']='HISTORICAL_REGION_DIAGNOSTIC'
            target=next((r for r in audit['checks'] if r['id']=='merton-retrospective-footnote'),None)
            if not target or not target.get('unit'):report['real_region_status']='ABSTAINED_MISSING_FOOTNOTE'
            else:
                payload=json.loads((folder/'slice.json').read_bytes());source=payload['sources'][target['source_id']];unit=target['unit']
                with pymupdf.open(root/source['preserved_blob']['path']) as doc:
                    png=doc[unit['pdf_page_index']].get_pixmap(matrix=pymupdf.Matrix(2,2),clip=pymupdf.Rect(unit['region_pdf_points']),alpha=False).tobytes('png')
                row=visual_transcript(opener,model,png,root)
                row.update(source_sha256=source['sha256'],page_index=unit['pdf_page_index'],region=unit['region_pdf_points'],fidelity_qualified=False)
                report['real_regions'].append(row)
        else:report['real_region_status']='ABSTAINED_FAILED_CONTROL'
    except (OSError,ValueError,KeyError,StopIteration) as exc:
        report.update(screen_status='UNAVAILABLE_OR_FAILED',failed_phase=report['phase'],error=type(exc).__name__+': '+str(exc))
        report['unrun_controls']=[c['id'] for c in cases[len(report['controls']):]]
    finally:
        if owned:
            try:request_json(opener,base+'/api/generate',{'model':model,'prompt':'','stream':False,'keep_alive':0})
            except (OSError,ValueError) as exc:report['cleanup_error']=type(exc).__name__+': '+str(exc)
        lease.close();lock.unlink(missing_ok=True)
    report['phase']='FINISHED'
    save_report(out,report)
    return {'output':str(out/'report.json'),'screen_status':report['screen_status'],
            'attempted':len(report['controls']),'planned':len(cases),'unrun':len(report['unrun_controls']),
            'real_regions':len(report['real_regions']),'transcription_accepted':False}
