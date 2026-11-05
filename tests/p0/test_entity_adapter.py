import importlib.util
import json
from pathlib import Path

import pytest

from horisma_p0.research_slice import encoded, sha


@pytest.mark.parametrize('current,base_id',[(True,'base'),(False,'base'),(True,'other-base')])
def test_base_scientific_success_cannot_bypass_unqualified_names(tmp_path,monkeypatch,current,base_id):
    path=Path(__file__).resolve().parents[2]/'.eidos/validate_horisma.py'
    if not path.exists():pytest.skip('Private installed-worker adapter absent in public checkout')
    spec=importlib.util.spec_from_file_location('entity_adapter_test',path)
    adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    monkeypatch.setattr(adapter,'ROOT',tmp_path)
    state=tmp_path/'ops/state';state.mkdir(parents=True)
    (tmp_path/'.eidos').mkdir()
    (tmp_path/'base').mkdir();(tmp_path/'base/slice.json').write_bytes(b'{}')
    (tmp_path/'entity.json').write_bytes(b'{}')
    (state/'research-slice-head.json').write_bytes(encoded({'slice':'base','sha256':sha(b'{}')}))
    (state/'entity-slice-head.json').write_bytes(encoded({'dataset':'entity.json','sha256':sha(b'{}')}))
    (state/'fidelity-campaign-head.json').write_bytes(encoded({'report':'report.json','sha256':sha(b'{}'),'suite_id':'suite'}))
    (tmp_path/'report.json').write_bytes(b'{}')
    (tmp_path/'suite.json').write_bytes(encoded({'base_slice_path':'base'}))
    monkeypatch.setattr(adapter,'load_campaign_report',lambda *_:{'suite_manifest':'suite.json','suite_id':'suite','historical_accuracy':None,'scientific_acceptance':False,'release_authorized':False})
    monkeypatch.setattr(adapter,'check_slice',lambda *_:{'preview_eligible':True,'scientific_eligible':True,'release_eligible':True,'blockers':[]})
    monkeypatch.setattr(adapter,'check_entity_dataset',lambda *_:{'base_slice_id':base_id,'preview_eligible':current,'scientific_eligible':False,'release_eligible':False})
    assert adapter.main()==4
    result=json.loads((tmp_path/'.eidos/horisma-check.json').read_bytes())
    if base_id!='base':
        assert result['execution_health']=='ERROR' and result['error']=='ENTITY_BASE_SLICE_MISMATCH'
    else:
        assert not result['scientific_eligible'] and not result['release_eligible']
        assert result['execution_health']==('PASS' if current else 'STALE')
