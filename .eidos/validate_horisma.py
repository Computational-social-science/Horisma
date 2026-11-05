"""Horisma domain adapter: reuse EIDOS receipts without granting scientific PASS."""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from horisma_p0.research_slice import check_slice,read,sha,encoded
from horisma_p0.entity_workflow import check_entity_dataset
from horisma_p0.fidelity_report import load_campaign_report
from horisma_p0.attribution_case import check_case


def main():
    try:
        head=json.loads(read(ROOT,'ops/state/research-slice-head.json'))
        folder=(ROOT/head['slice']).resolve()
        if sha(read(ROOT,head['slice']+'/slice.json'))!=head['sha256']:raise ValueError('HEAD_DIGEST_MISMATCH')
        result=check_slice(ROOT,folder)
        entity_head=json.loads(read(ROOT,'ops/state/entity-slice-head.json'))
        entity_path=ROOT/entity_head['dataset']
        if sha(read(ROOT,entity_head['dataset']))!=entity_head['sha256']:raise ValueError('ENTITY_HEAD_DIGEST_MISMATCH')
        result['entity_projection']=check_entity_dataset(ROOT,entity_path)
        if result['entity_projection']['base_slice_id']!=folder.name:raise ValueError('ENTITY_BASE_SLICE_MISMATCH')
        result['preview_eligible']=result['preview_eligible'] and result['entity_projection']['preview_eligible']
        result['scientific_eligible']=result['scientific_eligible'] and result['entity_projection']['scientific_eligible']
        result['release_eligible']=result['release_eligible'] and result['entity_projection']['release_eligible']
        if not result['entity_projection']['scientific_eligible']:result['blockers'].append('entity_identity_qualification')
        if not result['entity_projection']['preview_eligible']:result['blockers'].append('entity_integrity')
        fidelity_head=json.loads(read(ROOT,'ops/state/fidelity-campaign-head.json'))
        if sha(read(ROOT,fidelity_head['report']))!=fidelity_head['sha256']:raise ValueError('FIDELITY_HEAD_DIGEST_MISMATCH')
        campaign=load_campaign_report(ROOT,ROOT/fidelity_head['report'])
        suite=json.loads(read(ROOT,campaign['suite_manifest']))
        if campaign['effective_base_slice_path'].split('/')[-1]!=folder.name:raise ValueError('FIDELITY_BASE_SLICE_MISMATCH')
        if campaign['suite_id']!=fidelity_head['suite_id']:raise ValueError('FIDELITY_SUITE_MISMATCH')
        result['fidelity_campaign']={'suite_id':campaign['suite_id'],'report_sha256':fidelity_head['sha256'],
            'historical_accuracy':campaign['historical_accuracy'],'scientific_acceptance':campaign['scientific_acceptance'],
            'release_authorized':campaign['release_authorized']}
        result['scientific_eligible']=result['scientific_eligible'] and campaign['scientific_acceptance']
        result['release_eligible']=result['release_eligible'] and campaign['release_authorized']
        if not campaign['scientific_acceptance']:result['blockers'].append('regional_fidelity_unqualified')
        case_head_path=ROOT/'ops/state/attribution-case-head.json'
        if case_head_path.exists():
            case_head=json.loads(case_head_path.read_bytes())
            if sha(read(ROOT,case_head['case']))!=case_head['sha256']:raise ValueError('CASE_HEAD_DIGEST_MISMATCH')
            case_result=check_case(ROOT,ROOT/case_head['case'])
            if case_result['base_slice_ref']!=head['slice']:raise ValueError('CASE_BASE_SLICE_MISMATCH')
            result['case_projection']=case_result
            from horisma_p0.publication_rebase import check_publication_chain
            result['publication_projection']=check_publication_chain(ROOT,ROOT/case_head['case'])
            if (ROOT/'ops/state/passage-review-head.json').exists():
                from horisma_p0.passage_review import check_review
                result['passage_review']=check_review(ROOT)
            result['preview_eligible']=result['preview_eligible'] and case_result['preview_eligible']
            result['scientific_eligible']=result['scientific_eligible'] and case_result['scientific_eligible']
            result['release_eligible']=result['release_eligible'] and case_result['release_eligible']
            if not case_result['scientific_eligible']:result['blockers'].append('attribution_case_unqualified')
        else:
            result['scientific_eligible']=False;result['release_eligible']=False
            result['blockers'].append('attribution_case_not_built')
        result['execution_health']='PASS' if result['preview_eligible'] else 'STALE'
        result['scientific_status']='ELIGIBLE_FOR_ADDITIONAL_EIDOS_CHECKS' if result['scientific_eligible'] else 'REFUSED'
    except (OSError,ValueError,KeyError,TypeError) as exc:
        result={'execution_health':'ERROR','scientific_status':'REFUSED','error':str(exc)}
    target=ROOT/'.eidos/horisma-check.json'
    fd,temp=tempfile.mkstemp(prefix='.check-',dir=target.parent)
    with os.fdopen(fd,'wb') as stream:stream.write(encoded(result))
    os.replace(temp,target)
    print(json.dumps(result,indent=2))
    return 0 if result.get('scientific_eligible') else 4


if __name__=='__main__':raise SystemExit(main())
