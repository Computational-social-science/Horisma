"""Offline, sourced scientist/term catalogue and candidate mention/evidence projections."""
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time

import yaml

from .entity_mentions import annotate_mentions, script_codes
from .entity_sources import CATALOG, INDEX, load_authority, validate_authority_index
from .research_slice import check_slice, encoded, read, sha, write_new

FLAG_ROOT = 'Country-flags/flag-icons-main'
CODE_PATHS = ['src/horisma_p0/entity_workflow.py', 'src/horisma_p0/entity_mentions.py',
              'src/horisma_p0/entity_sources.py', 'spec/extensions/person_names.yaml',
              'spec/extensions/entity_catalog.yaml', 'spec/extensions/term_aliases.yaml',
              'docs/data-dictionary/Horisma_Scientist_Identity_and_Terminology_Extension_EN.md',
              'spec/examples/entity_mentions_challenge.json']
ATTRIBUTE_CODES = {'P569': 'BIRTH_TIME', 'P570': 'DEATH_TIME', 'P19': 'BIRTH_PLACE',
                   'P20': 'DEATH_PLACE', 'P27': 'CITIZENSHIP_AS_REPORTED',
                   'P21': 'SEX_OR_GENDER_AS_REPORTED_UNDISAMBIGUATED', 'P108': 'EMPLOYER',
                   'P69': 'EDUCATION', 'P166': 'AWARD', 'P106': 'OCCUPATION', 'P101': 'FIELD_OF_WORK'}


def stamp(record, id_field, prefix, identity):
    record[id_field] = prefix + sha(encoded(identity))
    record['revision'] = sha(encoded(record))
    return record


def build_entity_dataset(root, base_folder, crosscheck_path=None):
    root, base_folder = Path(root).resolve(), Path(base_folder).resolve()
    if not check_slice(root, base_folder)['preview_eligible']:
        raise ValueError('STALE_BASE_RESEARCH_SLICE')
    dependencies = {}

    def tracked(path):
        path = Path(path)
        relative = path.relative_to(root).as_posix() if path.is_absolute() else path.as_posix()
        raw = read(root, relative); dependencies[relative] = sha(raw)
        return raw

    base = json.loads(tracked(base_folder / 'slice.json'))
    config = yaml.safe_load(tracked(CATALOG))
    policy = yaml.safe_load(tracked('spec/extensions/term_aliases.yaml'))
    index = json.loads(tracked(INDEX))
    validate_authority_index(root, index, config)
    for path in CODE_PATHS:
        tracked(path)
    tracked(index['wikipedia_binding']['blob']['path'])
    authorities = {}
    for qid, record in index['entities'].items():
        tracked(record['blob']['path']); authorities[qid] = load_authority(root, record)
    flags = json.loads(tracked(FLAG_ROOT + '/country.json'))
    flag_package = json.loads(tracked(FLAG_ROOT + '/package.json'))
    flag_license = tracked(FLAG_ROOT + '/LICENSE')
    forms, profiles, attributes, assets = [], [], [], []

    def add_form(entry, value, language, kind, qid, pointer, basis=None, relation=None):
        if not isinstance(value, str) or not value.strip():
            return
        record = index['entities'][qid]
        form = {'entity_ref': entry['entity_ref'], 'entity_kind': entry['entity_kind'],
                'person_ref': entry['entity_ref'] if entry['entity_kind'] == 'PERSON' else None,
                'literal_form': value, 'form_kind': kind, 'language_tag': language,
                'surface_shape':'INITIALS_PRESENT' if re.search(r'\b[A-Z]\.',value) else 'SOURCE_FORM_UNEXPANDED',
                'script_code': script_codes(value), 'valid_time': None,
                'valid_time_missing_reason': 'NOT_ESTABLISHED_BY_NAME_LABEL',
                'source_version_ref': 'wikidata:' + qid + '@' + str(record['revision_id']) + ':' + record['blob']['sha256'],
                'source_blob': record['blob'], 'source_entity_id':qid,'passage_or_region_ref': '/entities/'+qid+pointer,
                'character_span': [0, len(value)], 'span_unit': 'UNICODE_CHARACTERS_IN_JSON_SCALAR',
                'evidence_status': 'CANDIDATE_SOURCE_FORM', 'identity_qualified': False,
                'observation_basis': basis or 'AUTHORITY_LABEL_OR_ALIAS_AS_REPORTED',
                'relation': relation, 'linkable': relation != 'RELATED_MECHANISM'}
        stamp(form, 'name_form_id', 'horisma:name-form:', [entry['entity_ref'], language, kind, qid, pointer, value])
        forms.append(form)

    for entry in config['entities']:
        qid = entry['wikidata_id']; entity = authorities[qid]
        for language in config['languages']:
            label = entity.get('labels', {}).get(language)
            if label:
                value = label['value']
                kind = 'INITIALLED' if re.search(r'\b[A-Z]\.', value) else 'LABEL_AS_ATTESTED'
                add_form(entry, value, language, kind, qid, '/labels/' + language + '/value', relation='CANDIDATE_LABEL')
            for i, alias in enumerate(entity.get('aliases', {}).get(language, [])):
                relation = 'CANDIDATE_SAME_CONCEPT' if entry['entity_kind'] == 'CONCEPT' else None
                if entry['entity_kind'] == 'CONCEPT' and alias['value'].casefold() in policy['related_mechanism_forms']:
                    relation = 'RELATED_MECHANISM'
                add_form(entry, alias['value'], language, 'ALIAS_AS_ATTESTED', qid,
                         '/aliases/' + language + '/' + str(i) + '/value', relation=relation)
        if entry['entity_kind'] == 'CONCEPT':
            for i, claim in enumerate(entity.get('claims', {}).get('P1813', [])):
                value = claim.get('mainsnak', {}).get('datavalue', {}).get('value')
                if isinstance(value, dict) and isinstance(value.get('text'), str):
                    add_form(entry,value['text'],value.get('language','und'),'ABBREVIATION_AS_ATTESTED',qid,
                             '/claims/P1813/'+str(i)+'/mainsnak/datavalue/value/text',relation='CANDIDATE_SAME_CONCEPT')
            continue
        for prop, kind in [('P735', 'GIVEN_ONLY'), ('P734', 'FAMILY_ONLY')]:
            for i, claim in enumerate(entity.get('claims', {}).get(prop, [])):
                if claim.get('rank') == 'deprecated':
                    continue
                part = claim.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id')
                if part not in authorities:
                    continue
                # Source-explicit name components; no automatic token-order decomposition.
                label = authorities[part].get('labels', {}).get('en')
                if label:
                    add_form(entry, label['value'], 'en', kind, part, '/labels/en/value',
                             basis={'kind': 'EXPLICIT_COMPONENT_PROPERTY', 'source_qid': qid,
                                    'source_version': index['entities'][qid]['blob']['sha256'],
                                    'claim_pointer': '/entities/'+qid+'/claims/' + prop + '/' + str(i), 'claim_id': claim['id']})
        # Birth/native/short names are literal values, not guessed expansions of initials.
        for prop in ('P1477', 'P1559', 'P1813'):
            for i, claim in enumerate(entity.get('claims', {}).get(prop, [])):
                value = claim.get('mainsnak', {}).get('datavalue', {}).get('value')
                if isinstance(value, dict) and isinstance(value.get('text'), str):
                    add_form(entry, value['text'], value.get('language', 'und'), 'ALIAS_AS_ATTESTED', qid,
                             '/claims/' + prop + '/' + str(i) + '/mainsnak/datavalue/value/text',
                             basis={'kind': 'SOURCE_NAME_PROPERTY', 'property': prop, 'rank': claim.get('rank')})
        refs = []
        for prop, attribute in ATTRIBUTE_CODES.items():
            for i, claim in enumerate(entity.get('claims', {}).get(prop, [])):
                assertion = {'person_ref': entry['entity_ref'], 'attribute_name': attribute,
                             'asserted_value': claim.get('mainsnak', {}).get('datavalue', {}).get('value'),
                             'snaktype': claim['mainsnak']['snaktype'], 'rank': claim.get('rank'),
                             'source_version_ref': 'wikidata:' + qid + '@' + str(index['entities'][qid]['revision_id']),
                             'source_blob': index['entities'][qid]['blob'],
                             'source_pointer': '/entities/'+qid+'/claims/' + prop + '/' + str(i), 'source_claim_id': claim['id'],
                             'valid_time_qualifiers': claim.get('qualifiers', {}),
                             'upstream_references': claim.get('references', []),
                             'assessment': None, 'status': 'CANDIDATE_NOT_ADJUDICATED',
                             'missing_reason':None if claim.get('mainsnak',{}).get('datavalue') is not None else 'SOURCE_'+claim['mainsnak']['snaktype'].upper(),
                             'disclosure': 'RESTRICTED_PENDING_RELEASE_REVIEW', 'scientific_acceptance': False}
                stamp(assertion, 'identity_assertion_id', 'horisma:identity-assertion:', [entry['entity_ref'], claim['id']])
                refs.append({'id': assertion['identity_assertion_id'], 'revision': assertion['revision']})
                attributes.append(assertion)
                if prop == 'P27' and claim.get('rank') != 'deprecated':
                    country = assertion['asserted_value'].get('id') if isinstance(assertion['asserted_value'], dict) else None
                    for j, iso_claim in enumerate(authorities.get(country, {}).get('claims', {}).get('P297', [])):
                        code = iso_claim.get('mainsnak', {}).get('datavalue', {}).get('value')
                        if iso_claim.get('rank') == 'deprecated' or not isinstance(code, str):
                            continue
                        flag = next((flag for flag in flags if flag['code'] == code.lower() and flag.get('iso') is True), None)
                        if flag is None:
                            continue
                        path = (root / FLAG_ROOT / flag['flag_4x3']).resolve()
                        if not path.is_relative_to((root / FLAG_ROOT).resolve()):
                            raise ValueError('EXTERNAL_FLAG_ASSET')
                        flag_raw = tracked(path)
                        assets.append({'person_ref': entry['entity_ref'], 'citizenship_assertion_ref': assertion['identity_assertion_id'],
                                       'country_entity': country, 'iso_alpha2': code.upper(),
                                       'iso_source_blob': index['entities'][country]['blob'],
                                       'iso_source_pointer': '/entities/'+country+'/claims/P297/' + str(j),
                                       'path': path.relative_to(root).as_posix(), 'sha256': sha(flag_raw),
                                       'library': flag_package['name'], 'library_version': flag_package['version'],
                                       'license_path': FLAG_ROOT + '/LICENSE', 'license_sha256': sha(flag_license),
                                       'license_as_declared':flag_package.get('license'),
                                       'valid_time': None, 'historical_appropriateness': 'NOT_ESTABLISHED',
                                       'display_eligible': False, 'purpose': 'CITIZENSHIP_DISPLAY_CANDIDATE_NOT_PERSON_IDENTITY'})
        person = next(person for person in base['people'] if person['person_id'] == entry['entity_ref'])
        profiles.append({'person_id': entry['entity_ref'], 'preferred_name': person['preferred_name'],
                         'profile': 'PARTIAL_SOURCE_REPORTED_CANDIDATE', 'identity_assertion_refs': refs,
                         'contribution_assertion_refs': person['assertion_refs'],
                         'nationality': None, 'nationality_missing_reason': 'NOT_COLLECTED_CITIZENSHIP_IS_SEPARATE',
                         'portrait_asset': None, 'portrait_missing_reason': 'NOT_COLLECTED',
                         'name_language_coverage':{language:('SOURCE_LABEL_AVAILABLE' if language in entity.get('labels',{}) else 'NOT_IN_SNAPSHOT') for language in config['languages']},
                         'identity_qualified': False})
    for person in profiles:
        person['name_form_refs']=[{'id':form['name_form_id'],'revision':form['revision']} for form in forms if form['entity_ref']==person['person_id']]
        person['citizenship_assertion_refs']=[{'id':attribute['identity_assertion_id'],'revision':attribute['revision']} for attribute in attributes
                                             if attribute['person_ref']==person['person_id'] and attribute['attribute_name']=='CITIZENSHIP_AS_REPORTED']
    for asset in assets:
        asset['flag_association_id']='horisma:flag-association:'+sha(encoded([asset['person_ref'],asset['citizenship_assertion_ref'],asset['iso_source_pointer'],asset['sha256']]))
    for person in profiles:
        person['flag_asset_refs']=[asset['flag_association_id'] for asset in assets if asset['person_ref']==person['person_id']]
        person['flag_projection_status']='CANDIDATE_UNQUALIFIED' if person['flag_asset_refs'] else ('MISSING_ISO_OR_ASSET' if person['citizenship_assertion_refs'] else 'NOT_COLLECTED')
    def bind_annotations(result,source_version,region_ref):
        for observation in result['mentions']+result['coreferences']:
            observation.update(source_version_ref=source_version,passage_or_region_ref=region_ref,text_sha256=result['text_sha256'])
            observation.pop('revision',None);observation['revision']=sha(encoded(observation))
    passages = []
    for source_id, region in base['regions'].items():
        raw = tracked(region['native_text_blob']['path'])
        if sha(raw) != region['native_text_blob']['sha256']:
            raise ValueError('REGIONAL_TEXT_CHANGED')
        namespace = base['sources'][source_id]['version_id'] + '/' + region['region_id'] + '/native'
        result = annotate_mentions(raw.decode('utf-8'), forms, namespace=namespace)
        result.update(source_id=source_id, source_version_ref=base['sources'][source_id]['version_id'],
                      region_ref=region['region_id'], channel='NATIVE_UNQUALIFIED', text_blob=region['native_text_blob'],
                      text_locator={'path':region['native_text_blob']['path'],'encoding':'utf-8'})
        bind_annotations(result,result['source_version_ref'],region['region_id'])
        passages.append(result)
    if crosscheck_path is not None:
        crosscheck_path=Path(crosscheck_path).resolve()
        if not crosscheck_path.is_relative_to(base_folder/'transcription-crosscheck'):
            raise ValueError('EXTERNAL_ENTITY_CROSSCHECK')
        cross_raw=tracked(crosscheck_path);cross=json.loads(cross_raw)
        if crosscheck_path.parent.name!=sha(cross_raw) or cross['slice_id']!=base_folder.name:
            raise ValueError('ENTITY_CROSSCHECK_CHANGED')
        source_ids=[sid for sid,source in base['sources'].items() if source['sha256']==cross['source_sha256']]
        if len(source_ids)!=1 or cross['page_index']!=base['regions'][source_ids[0]]['page_index']:
            raise ValueError('ENTITY_CROSSCHECK_SOURCE_MISMATCH')
        source_id=source_ids[0]
        for channel_index,channel in enumerate(cross['channels']):
            if sha(channel['text'].encode())!=channel['text_sha256']:
                raise ValueError('ENTITY_CROSSCHECK_TEXT_CHANGED')
            if channel['id']=='native':
                continue
            region_ref='horisma:cross-region:'+sha(encoded([cross['source_sha256'],cross['page_index'],channel['region_pdf_points']]))
            namespace=base['sources'][source_id]['version_id']+'/'+region_ref+'/'+channel['id']+'/'+sha(cross_raw)
            result=annotate_mentions(channel['text'],forms,namespace=namespace)
            result.update(source_id=source_id,source_version_ref=base['sources'][source_id]['version_id'],
                          region_ref=region_ref,channel=channel['id'],crosscheck_sha256=sha(cross_raw),
                          region_pdf_points=channel['region_pdf_points'],lineage=channel['lineage'])
            result['text_locator']={'path':crosscheck_path.relative_to(root).as_posix(),'json_pointer':'/channels/'+str(channel_index)+'/text'}
            bind_annotations(result,result['source_version_ref'],region_ref)
            passages.append(result)
    benchmark = []
    for task in base['tasks']:
        source_ids = set(task['sources'])
        benchmark.append({'task_id': task['task_id'], 'task_revision': task['revision'],
                          'concept_family_ref': config['concept_family_ref'], 'split': 'DEVELOPMENT_ONLY',
                          'mention_refs': [mention['mention_id'] for passage in passages if passage['source_id'] in source_ids for mention in passage['mentions']],
                          'coreference_refs': [mention['coreference_id'] for passage in passages if passage['source_id'] in source_ids for mention in passage['coreferences']],
                          'gold_answer': None, 'historical_accuracy': None, 'scientific_acceptance': False})
    edges = [{'kind': 'MENTION_CANDIDATE_ENTITY', 'mention_ref': mention['mention_id'], 'target_ref': entity,
              'source_version_ref': passage['source_version_ref'], 'region_ref': passage['region_ref'],
              'character_span': mention['character_span'], 'link_state': mention['link_state'], 'accepted': False}
             for passage in passages for mention in passage['mentions'] for entity in mention['candidate_entity_refs']]
    edges += [{'kind':'COREFERENCE_CANDIDATE_PERSON','mention_ref':mention['coreference_id'],'target_ref':entity,
               'antecedent_mention_refs':mention['antecedent_mention_refs'],'source_version_ref':passage['source_version_ref'],
               'region_ref':passage['region_ref'],'character_span':mention['character_span'],
               'link_state':mention['link_state'],'accepted':False}
              for passage in passages for mention in passage['coreferences'] for entity in mention['candidate_person_refs']]
    result = {'version': '0.1.0', 'base_slice_id': base_folder.name, 'base_slice_path': base_folder.relative_to(root).as_posix(),
              'dependencies': dependencies, 'forms': forms, 'scientists': profiles, 'identity_assertions': attributes,
              'flag_assets': assets, 'passages': passages, 'evidence_edges': edges, 'benchmark_projection': benchmark,
              'concepts':[{'concept_ref':entry['entity_ref'],'concept_family_ref':config['concept_family_ref'],
                           'name_form_refs':[{'id':form['name_form_id'],'revision':form['revision']} for form in forms if form['entity_ref']==entry['entity_ref']],
                           'equivalence_qualified':False} for entry in config['entities'] if entry['entity_kind']=='CONCEPT'],
              'concept_family_ref': config['concept_family_ref'], 'scientific_acceptance': False,
              'release_authorized': False, 'coverage_scope': 'TWO_SCIENTISTS_ONE_TARGET_CONCEPT_AND_DECLARED_AUTHORITY_SNAPSHOTS'}
    # Detect dependency mutation during a deterministic build.
    if (any(sha(read(root, path)) != digest for path, digest in dependencies.items())
            or not check_slice(root,base_folder)['preview_eligible']):
        raise ValueError('ENTITY_BUILD_INPUT_CHANGED')
    raw = encoded(result); output = root / 'outputs/entity-slices' / sha(raw)
    write_new(output / 'dataset.json', raw)
    head=root/'ops/state/entity-slice-head.json';head.parent.mkdir(parents=True,exist_ok=True)
    descriptor,temporary=tempfile.mkstemp(prefix='.entity-head-',dir=head.parent)
    try:
        with os.fdopen(descriptor,'wb') as stream:
            stream.write(encoded({'dataset':(output/'dataset.json').relative_to(root).as_posix(),'sha256':sha(raw)}))
        os.replace(temporary,head)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return {'dataset': str(output / 'dataset.json'), 'scientists': len(profiles), 'forms': len(forms),
            'attributes': len(attributes), 'flag_assets': len(assets),
            'mentions': sum(len(passage['mentions']) for passage in passages),
            'coreferences': sum(len(passage['coreferences']) for passage in passages),
            'benchmark_tasks': len(benchmark), 'scientific_acceptance': False}


def check_entity_dataset(root, dataset):
    root, dataset = Path(root).resolve(), Path(dataset).resolve()
    if not dataset.is_relative_to(root / 'outputs/entity-slices'):
        raise ValueError('EXTERNAL_ENTITY_DATASET')
    raw = dataset.read_bytes()
    if dataset.parent.name != sha(raw):
        raise ValueError('ENTITY_DATASET_CHANGED')
    payload = json.loads(raw)
    changed = [path for path, digest in payload['dependencies'].items()
               if not (root / path).is_file() or sha(read(root, path)) != digest]
    base = check_slice(root, root / payload['base_slice_path'])
    return {'dataset_id': dataset.parent.name, 'base_slice_id':payload['base_slice_id'], 'preview_eligible': not changed and base['preview_eligible'],
            'changed_dependencies': changed, 'scientific_eligible': False, 'release_eligible': False,
            'affected_projections': ['scientist_profiles', 'entity_mentions', 'evidence_edges', 'benchmark'] if changed or not base['preview_eligible'] else []}


def evaluate_entity_rules(root):
    root=Path(root).resolve()
    corpus_raw=read(root,'spec/examples/entity_mentions_challenge.json');corpus=json.loads(corpus_raw)
    if corpus.get('synthetic') is not True or corpus.get('split')!='DEVELOPMENT_ONLY':
        raise ValueError('CONSTRUCTED_DEVELOPMENT_CORPUS_REQUIRED')
    rows=[];started=time.monotonic()
    for case in corpus['cases']:
        scopes=None
        if case.get('speaker_person_refs'):
            scopes=[{'context_id':'synthetic-speaker','start':0,'end':len(case['text']),
                     'speaker_person_refs':case['speaker_person_refs'],'speaker_evidence_refs':['synthetic:speaker']}]
        result=annotate_mentions(case['text'],corpus['forms'],scopes,namespace='synthetic:'+case['id'])
        checks={}
        if 'mentions' in case:
            checks['mentions']=[[row['literal_text'],row['link_state'],row['candidate_entity_refs']] for row in result['mentions']]==case['mentions']
        if 'corefs' in case:
            checks['coreferences']=[[row['literal_text'],row['link_state'],row['candidate_person_refs']] for row in result['coreferences']]==case['corefs']
        if 'basis' in case:
            checks['basis']=bool(result['mentions']) and result['mentions'][0]['linking_basis']==case['basis']
        checks['offsets']=all(case['text'][row['character_span'][0]:row['character_span'][1]]==row['literal_text']
                             for row in result['mentions']+result['coreferences'])
        rows.append({'case_id':case['id'],'synthetic':True,'checks':checks,'passed':all(checks.values()),'response':result})
    report={'version':'0.1.0','corpus_sha256':sha(corpus_raw),
            'operator_sha256':sha(read(root,'src/horisma_p0/entity_mentions.py')),
            'evaluator_sha256':sha(Path(__file__).read_bytes()),'python_version':sys.version,
            'scope':'CONSTRUCTED_RULE_REGRESSION_NOT_MODEL_PERFORMANCE_OR_HISTORICAL_GOLD',
            'split':'DEVELOPMENT_ONLY','rows':rows,'correct':sum(row['passed'] for row in rows),'denominator':len(rows),
            'historical_accuracy':None,'model_calls':0,'scientific_acceptance':False,'release_authorized':False}
    raw=encoded(report);output=root/'outputs/entity-evaluations'/sha(raw)/'report.json';write_new(output,raw)
    return {'report':str(output),'correct':report['correct'],'denominator':report['denominator'],
            'elapsed_seconds':time.monotonic()-started,'model_calls':0,'scientific_acceptance':False}
