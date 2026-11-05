"""Explicit, on-demand P0 commands; never starts a background controller."""
import argparse
import json
from pathlib import Path

from .operators import ContractError, acquire_source, index_wikipedia, load_json, save_new_json, validate_ledger


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest='command', required=True)
    acquire = sub.add_parser('acquire')
    acquire.add_argument('source_id')
    acquire.add_argument('url')
    acquire.add_argument('--media', choices=['pdf', 'html'], default='pdf')
    sub.add_parser('index-wikipedia')
    sub.add_parser('validate')
    rebase=sub.add_parser('research-publication-rebase')
    rebase.add_argument('base',type=Path)
    sub.add_parser('research-passage-review')
    sub.add_parser('research-regional-audit')
    sub.add_parser('research-heldout-review')
    sub.add_parser('research-json-templates')
    json_validate=sub.add_parser('research-json-validate')
    json_validate.add_argument('record',type=Path)
    build=sub.add_parser('research-build')
    build.add_argument('--ocr-model-dir',type=Path)
    check=sub.add_parser('research-check')
    check.add_argument('slice',type=Path)
    ocr=sub.add_parser('research-ocr')
    ocr.add_argument('slice',type=Path)
    ocr.add_argument('--model-dir',type=Path,required=True)
    evaluate=sub.add_parser('research-evaluate')
    evaluate.add_argument('--candidate',choices=['gemma3:12b','qwen3.8:27b'],default='gemma3:12b')
    route=sub.add_parser('research-route')
    route.add_argument('slice',type=Path)
    route.add_argument('--screen',type=Path,required=True)
    sub.add_parser('research-eidos-check')
    parsers=sub.add_parser('research-parsers')
    parsers.add_argument('slice',type=Path)
    parse=sub.add_parser('research-parse')
    parse.add_argument('--backend',choices=['auto','anymd','docling','paddleocr'],default='auto')
    parse.add_argument('--source-id',choices=['1','2','3','4','5'],required=True)
    parse.add_argument('--ocr-model-dir',type=Path)
    audit=sub.add_parser('research-audit')
    audit.add_argument('slice',type=Path)
    audit.add_argument('--model-dir',type=Path,required=True)
    correct=sub.add_parser('research-correct')
    correct.add_argument('slice',type=Path)
    correction_input=correct.add_mutually_exclusive_group(required=True)
    correction_input.add_argument('--audit',type=Path)
    correction_input.add_argument('--replay',type=Path)
    visual=sub.add_parser('research-visual-screen')
    visual.add_argument('slice',type=Path)
    visual.add_argument('--audit',type=Path,required=True)
    crosscheck=sub.add_parser('research-crosscheck')
    crosscheck.add_argument('slice',type=Path)
    crosscheck.add_argument('--audit',type=Path,required=True)
    crosscheck.add_argument('--source-id',choices=['1','2','3','4','5'],required=True)
    entity_sources=sub.add_parser('research-entity-sources')
    entity_sources.add_argument('--refresh',action='store_true')
    entities=sub.add_parser('research-entities-build')
    entities.add_argument('slice',type=Path)
    entities.add_argument('--crosscheck',type=Path)
    entity_check=sub.add_parser('research-entities-check')
    entity_check.add_argument('dataset',type=Path)
    sub.add_parser('research-entities-evaluate')
    sub.add_parser('research-fidelity-freeze')
    fidelity=sub.add_parser('research-fidelity-run')
    fidelity.add_argument('manifest',type=Path)
    fidelity.add_argument('--backend',choices=['docling','paddleocr','mineru'],required=True)
    fidelity_report=sub.add_parser('research-fidelity-report')
    fidelity_report.add_argument('manifest',type=Path)
    fidelity_route=sub.add_parser('research-fidelity-route')
    fidelity_route.add_argument('report',type=Path)
    fidelity_route.add_argument('--source-id',choices=['1','2','3','4','5'],required=True)
    fidelity_route.add_argument('--dimension',required=True)
    document=sub.add_parser('research-document-build')
    document.add_argument('--source-id',required=True)
    full_ocr=sub.add_parser('research-document-ocr')
    full_ocr.add_argument('--source-id',choices=['3','4'],required=True)
    ingest=sub.add_parser('research-document-ingest')
    ingest.add_argument('pdf',type=Path)
    paper_package=sub.add_parser('research-paper-package')
    paper_package.add_argument('manifest',type=Path)
    cards=sub.add_parser('research-event-cards')
    cards.add_argument('case',type=Path)
    cards.add_argument('intake',type=Path)
    publication=sub.add_parser('research-card-export')
    publication.add_argument('cards',type=Path)
    case=sub.add_parser('research-case-build')
    case.add_argument('intake',type=Path)
    case_check=sub.add_parser('research-case-check')
    case_check.add_argument('case',type=Path)
    sub.add_parser('research-docs')
    maintenance=sub.add_parser('research-maintenance')
    maintenance.add_argument('--apply',action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command.startswith('research-'):
            from .research_slice import build_slice,check_slice,run_ocr
            if args.command=='research-json-templates':
                from .json_contracts import compile_contracts
                result=compile_contracts(root)
            elif args.command=='research-json-validate':
                from .json_contracts import validate_interchange
                result=validate_interchange(root,json.loads(args.record.read_bytes()))
            elif args.command=='research-heldout-review':
                from .regional_qualification import holdout_review
                result=holdout_review(root)
            elif args.command=='research-regional-audit':
                from .regional_qualification import regional_audit
                result=regional_audit(root)
            elif args.command=='research-passage-review':
                from .passage_review import review_passages
                result=review_passages(root)
            elif args.command=='research-publication-rebase':
                from .publication_rebase import rebuild_integrated
                result=rebuild_integrated(root,args.base)
            elif args.command=='research-card-export':
                from .card_publication import export_cards
                result=export_cards(root,args.cards)
            elif args.command=='research-event-cards':
                from .event_cards import build_event_cards
                result=build_event_cards(root,args.case,args.intake)
            elif args.command=='research-paper-package':
                from .paper_packages import package_reading
                result=package_reading(root,args.manifest)
            elif args.command=='research-document-ingest':
                from .source_registry import register_pdf
                from .document_reading import build_document
                intake=register_pdf(root,args.pdf)
                result={**intake,'reading':build_document(root,intake['source_id'])}
            elif args.command=='research-docs':
                from .maintenance import current_documents
                result=current_documents(root)
            elif args.command=='research-maintenance':
                from .maintenance import cleanup_plan,apply_cleanup
                plan=cleanup_plan(root)
                result=apply_cleanup(root,plan) if args.apply else plan
                from .research_slice import encoded,sha,write_new
                write_new(root/'outputs/maintenance'/sha(encoded(result))/'report.json',encoded(result))
            elif args.command=='research-document-ocr':
                from .document_ocr import build_ocr_document
                result=build_ocr_document(root,args.source_id)
            elif args.command=='research-document-build':
                from .document_reading import build_document
                result=build_document(root,args.source_id)
            elif args.command=='research-case-build':
                from .attribution_case import build_case
                result=build_case(root,args.intake)
            elif args.command=='research-case-check':
                from .attribution_case import check_case
                result=check_case(root,args.case)
            elif args.command=='research-parse':
                import subprocess
                import sys
                backend=args.backend;route_reason='EXPLICIT_BACKEND'
                if backend=='paddleocr':
                    from .paddle_candidate import run_paddle_candidate
                    result=run_paddle_candidate(root,args.source_id)
                    print(json.dumps(result,indent=2));return result['process_returncode']
                if backend=='auto':
                    from .parser_candidates import page_kind
                    head=json.loads((root/'ops/state/research-slice-head.json').read_bytes())
                    folder=(root/head['slice']).resolve()
                    if not check_slice(root,folder)['preview_eligible']:raise ValueError('STALE_SLICE')
                    payload=json.loads((folder/'slice.json').read_bytes())
                    source=payload['sources'][args.source_id]
                    kind=page_kind(root/source['preserved_blob']['path'],payload['regions'][args.source_id]['page_index'])
                    import yaml
                    parser_config=yaml.safe_load((root/'spec/extensions/document_parsers.yaml').read_text(encoding='utf-8'))
                    backend=parser_config['routing'][kind['kind']];route_reason=kind['kind']
                    if backend not in {'docling','anymd'}:raise ValueError('UNAPPROVED_PARSER_ROUTE')
                command=[sys.executable,str(root/'scripts'/(backend+'_region_probe.py')),'--source-id',args.source_id]
                if backend=='docling':
                    if args.ocr_model_dir is None:raise ValueError('EXPLICIT_LOCAL_OCR_MODELS_REQUIRED')
                    command+=['--ocr-model-dir',str(args.ocr_model_dir)]
                operation=subprocess.run(command,cwd=root,capture_output=True,timeout=150)
                result={'backend':backend,'route_reason':route_reason,'process_returncode':operation.returncode,
                        'stdout_tail':operation.stdout.decode('utf-8',errors='replace')[-2000:],
                        'stderr_tail':operation.stderr.decode('utf-8',errors='replace')[-1000:],
                        'scientific_acceptance':False}
                print(json.dumps(result,indent=2));return operation.returncode
            elif args.command=='research-eidos-check':
                import subprocess
                from .research_slice import read,sha
                pin=json.loads(read(root,'.eidos/runtime-pin.json'))
                if sha(Path(pin['wheel_path']).read_bytes())!=pin['expected_wheel_sha256']:raise ValueError('EIDOS_WHEEL_PIN_MISMATCH')
                operation=subprocess.run([pin['worker_python'],'-I','-m','framework.cli','check','--project',str(root),'--timeout','120','--json'],cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=130)
                result=json.loads(operation.stdout)
                result['adapter_process_returncode']=operation.returncode
            elif args.command=='research-build':
                folder=build_slice(root)
                result={'slice':str(folder),**check_slice(root,folder)}
                if args.ocr_model_dir:result['ocr_receipt']=str(run_ocr(root,folder,args.ocr_model_dir))
            elif args.command=='research-check':result=check_slice(root,args.slice)
            elif args.command=='research-ocr':result={'ocr_receipt':str(run_ocr(root,args.slice,args.model_dir))}
            elif args.command=='research-route':
                from .pipeline_routes import route_diagnostics
                result=route_diagnostics(root,args.slice,args.screen)
            elif args.command=='research-parsers':
                from .parser_candidates import parser_report
                result=parser_report(root,args.slice)
            elif args.command=='research-audit':
                from .layout_audit import run_layout_audit
                result=run_layout_audit(root,args.slice,args.model_dir)
            elif args.command=='research-correct':
                from .correction_workflow import run_correction_workflow,replay_correction_report
                result=replay_correction_report(root,args.slice,args.replay) if args.replay else run_correction_workflow(root,args.slice,args.audit)
            elif args.command=='research-visual-screen':
                from .visual_challenge import run_visual_challenge
                result=run_visual_challenge(root,args.slice,args.audit)
            elif args.command=='research-crosscheck':
                from .transcription_crosscheck import crosscheck_transcriptions
                result=crosscheck_transcriptions(root,args.slice,args.audit,args.source_id)
            elif args.command=='research-entity-sources':
                from .entity_sources import acquire_entity_sources
                result=acquire_entity_sources(root,args.refresh)
            elif args.command=='research-entities-build':
                from .entity_workflow import build_entity_dataset
                result=build_entity_dataset(root,args.slice,args.crosscheck)
            elif args.command=='research-entities-check':
                from .entity_workflow import check_entity_dataset
                result=check_entity_dataset(root,args.dataset)
            elif args.command=='research-entities-evaluate':
                from .entity_workflow import evaluate_entity_rules
                result=evaluate_entity_rules(root)
            elif args.command=='research-fidelity-freeze':
                from .fidelity_suite import freeze_fidelity_suite
                result=freeze_fidelity_suite(root)
            elif args.command=='research-fidelity-run':
                from .fidelity_campaign import run_backend
                result=run_backend(root,args.manifest,args.backend)
            elif args.command=='research-fidelity-report':
                from .fidelity_report import campaign_report
                result=campaign_report(root,args.manifest)
            elif args.command=='research-fidelity-route':
                from .fidelity_report import regional_route
                result=regional_route(root,args.report,args.source_id,args.dimension)
            else:
                from .model_screen import run_screen
                result=run_screen(root,args.candidate)
        elif args.command == 'acquire':
            result = acquire_source(root, args.source_id, args.url, args.media)
        elif args.command == 'index-wikipedia':
            folder = root / 'data/intake/wikipedia/matthew_effect'
            receipt = load_json(folder / 'source_receipt.json')
            result = index_wikipedia((folder / 'page.html').read_bytes(), receipt['sha256'], receipt['revision_id'])
            save_new_json(root / 'data/evidence/p0/matthew-effect-v1/wikipedia_bibliography.json', result)
            result = {'reference_entries': len(result['reference_entries']), 'proposed_work_groups': result['proposed_work_groups'], 'purpose': result['purpose']}
        else:
            result = validate_ledger(root, load_json(root/'data/evidence/p0/matthew-effect-v1/candidate_ledger.v2.json'),
                                     load_json(root/'spec/p0/candidate_ledger.schema.json'), load_json(root/'spec/p0/freeze_manifest.json'))
        print(json.dumps(result, indent=2))
        if 'adapter_process_returncode' in result:return result['adapter_process_returncode']
        if result.get('preview_eligible') is False:return 1
        return 0 if result.get('access_status') != 'WAITING_HUMAN_SOURCE' else 2
    except (ContractError, OSError, ValueError) as exc:
        print(json.dumps({'execution_status': 'TERMINAL_FAILURE', 'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
