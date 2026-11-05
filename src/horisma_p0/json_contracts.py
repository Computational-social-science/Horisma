"""Compile existing dictionary fields to explicit JSON interchange scaffolds.

Structural schemas do not implement the dictionary's scientific proof obligations.
"""
import copy
import json
from pathlib import Path
import re

import yaml
from jsonschema import Draft202012Validator, FormatChecker, ValidationError
from referencing import Registry, Resource

from .research_slice import encoded,read,sha

BASE='https://horisma.invalid/contracts/intermediate/0.1.0/'
DIRECTORY='spec/intermediate-json/v0.1.0'
DICTIONARY='docs/data-dictionary/Horisma_Project_Data_Dictionary_EN.md'
VOCAB='spec/controlled_vocabularies.yaml'


def nullable(schema):
    return {'anyOf':[schema,{'type':'null'}]}


def strict(properties, required=None):
    return {'type':'object','additionalProperties':False,'properties':properties,
            'required':list(properties) if required is None else required}


def definitions(vocabs):
    ref={'type':'string','pattern':r'^record:[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'}
    text={'type':'string','minLength':1}
    defs={'RecordRef':ref,'sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'}}
    defs.update({'v_'+name:{'type':'string','enum':list(v['codes'])} for name,v in vocabs.items()})
    vref=lambda name:{'$ref':'#/$defs/v_'+name}
    defs['TemporalExtent']=strict({'original_text':text,'calendar_system':vref('calendar_system'),
        'precision':vref('temporal_precision'),'normalized_lower':nullable({'type':'string','format':'date'}),
        'normalized_upper':nullable({'type':'string','format':'date'}),'normalization_artifact_ref':nullable(ref)})
    defs['PassageLocator']=strict({'anchor_kind':vref('passage_anchor_kind'),'printed_page':nullable(text),
        'pdf_page_index':nullable({'type':'integer','minimum':0}),'derivative_artifact_ref':nullable(ref),
        'start_offset':nullable({'type':'integer','minimum':0}),'end_offset':nullable({'type':'integer','minimum':0}),
        'region':nullable({'type':'array','minItems':4,'maxItems':4,'items':{'type':'number','minimum':0,'maximum':1}})})
    defs['IdentifierList']={'type':'array','items':strict({'scheme':vref('identifier_scheme'),'value':text,'other_scheme_name':nullable(text)})}
    defs['RecordRefList']={'type':'array','items':ref}
    defs['LogicRefList']={'type':'array','items':{'type':'string','pattern':'^L[0-9]+$'}}
    defs['PublicationModeMap']={'type':'object','additionalProperties':vref('publication_mode')}
    defs['CreditAllocation']={'type':'array','items':strict({'actor_ref':ref,'share':{'type':'number','minimum':0,'maximum':1}})}
    defs['OperatorRef']=strict({'operator_id':text,'operator_version':text})
    defs['BoundRef']=strict({'record_id':text,'revision_sha256':{'$ref':'#/$defs/sha256'},
                            'binding_kind':{'enum':['RECORD_REVISION','SOURCE_BYTES']}})
    defs['ArtifactBinding']=strict({'path':text,'sha256':{'$ref':'#/$defs/sha256'}})
    defs['TextBinding']=strict({'artifact':{'$ref':'#/$defs/ArtifactBinding'},'unicode_start':{'type':'integer','minimum':0},
                               'unicode_end':{'type':'integer','minimum':1},'offset_unit':{'const':'UNICODE_CODE_POINTS_IN_EXACT_UTF8_TEXT'}})
    return defs


def common_fields():
    return {'entity_id':{'type':'string','pattern':r'^[a-z_]+:[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'},
        'record_id':{'$ref':'shared.schema.json#/$defs/RecordRef'},'record_version':{'type':'integer','minimum':1},
        'supersedes_record_id':nullable({'$ref':'shared.schema.json#/$defs/RecordRef'}),
        'dictionary_version':{'const':'0.1.0'},'vocabulary_version':{'type':'string','minLength':1},
        'record_status':{'$ref':'shared.schema.json#/$defs/v_record_status'},
        'created_at':{'type':'string','format':'date-time'},'created_by_actor_ref':{'$ref':'shared.schema.json#/$defs/RecordRef'},
        'disclosure_class':{'$ref':'shared.schema.json#/$defs/v_disclosure_class'},
        'missing_reasons':{'type':'object','additionalProperties':{'$ref':'shared.schema.json#/$defs/v_missing_reason'}},
        'provenance_artifact_refs':{'type':'array','items':{'$ref':'shared.schema.json#/$defs/RecordRef'}}}


def field_schema(type_name, values, required, defs):
    if type_name=='enum':
        key='v_'+values
        if key not in defs:raise ValueError('UNKNOWN_VOCABULARY:'+values)
        result={'$ref':'shared.schema.json#/$defs/'+key}
    elif type_name.startswith('ref:'):
        result={'$ref':'shared.schema.json#/$defs/RecordRef','x-target-type':type_name[4:]}
    elif type_name.startswith('refs:'):
        result={'type':'array','minItems':1 if required else 0,'items':{'$ref':'shared.schema.json#/$defs/RecordRef'},'x-target-type':type_name[5:]}
    elif type_name in defs:
        result={'$ref':'shared.schema.json#/$defs/'+type_name}
        if type_name.endswith('List') and required:result['minItems']=1
    elif type_name in {'text','language','path'}:result={'type':'string','minLength':1}
    elif type_name=='uri':result={'type':'string','format':'uri','minLength':1}
    elif type_name=='datetime':result={'type':'string','format':'date-time'}
    elif type_name=='fraction':result={'type':'number','minimum':0,'maximum':1}
    elif type_name in {'integer','number','boolean'}:result={'type':type_name}
    else:raise ValueError('UNMAPPED_DICTIONARY_TYPE:'+type_name)
    return result if required else nullable(result)


def compile_contracts(root):
    root=Path(root).resolve();doc=read(root,DICTIONARY).decode();raw_vocab=read(root,VOCAB)
    freeze=json.loads(read(root,'spec/p0/freeze_manifest.json'))['sha256']
    if sha(read(root,DICTIONARY))!=freeze[DICTIONARY] or sha(raw_vocab)!=freeze[VOCAB]:
        raise ValueError('FROZEN_AUTHORITY_CHANGED')
    catalog=yaml.safe_load(raw_vocab);vocabs=catalog['vocabularies'];defs=definitions(vocabs)
    shared={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':BASE+'shared.schema.json','$defs':defs}
    files={'shared.schema.json':shared};entries=[]
    sections=re.findall(r'^### `([^`]+)`(.*?)(?=^### |^## |\Z)',doc,re.S|re.M)
    for name,body in sections:
        stage=re.search(r'Stage: `([^`]+)`',body).group(1)
        fields={};contracts={};conditional=[]
        for line in body.splitlines():
            if not line.startswith('| `'):continue
            cols=[x.strip() for x in line.strip('|').split('|')]
            if len(cols)!=8:raise ValueError('UNPARSED_DICTIONARY_ROW:'+name)
            key=cols[0].strip('`');type_name=re.match(r'`([^`]+)`',cols[2]).group(1)
            required=cols[2].endswith('; R')
            fields[key]=field_schema(type_name,cols[3],required,defs)
            fields[key]['description']=cols[1]
            fields[key]['x-logical-type']=type_name
            contracts[key]={'definition':cols[1],'type_cardinality_obligation':cols[2],'values_units':cols[3],
                            'missing_disclosure':cols[4],'provenance_derivation_review':cols[5],'examples':cols[6],'logic':cols[7]}
            if '; C:' in cols[2]:conditional.append({'field':key,'condition':cols[2].split('; C:',1)[1],
                                                   'implementation':'SEMANTIC_CONDITION_NOT_CERTIFIED_BY_STRUCTURAL_SCHEMA'})
        properties={**common_fields(),**fields}
        properties['vocabulary_version']={'const':catalog['catalog_version']}
        properties['entity_id']['pattern']=properties['entity_id']['pattern'].replace('^[a-z_]+:', '^'+name+':')
        required=[k for k in common_fields() if k!='supersedes_record_id']+[k for k in fields if contracts[k]['type_cardinality_obligation'].endswith('; R')]
        record=strict(properties,required)
        conditions=[]
        for condition in conditional:
            field=condition['field'];expression=condition['condition']
            match=re.fullmatch(r'([a-z_]+)=([A-Z_]+)',expression)
            nonnull=re.fullmatch(r'([a-z_]+) is non-null',expression)
            if match and match[1] in properties:
                conditions.append({'if':{'properties':{match[1]:{'const':match[2]}},'required':[match[1]]},
                                   'then':{'required':[field],'properties':{field:{'not':{'type':'null'}}}}})
                condition['implementation']='JSON_SCHEMA_CONDITION'
            elif nonnull and nonnull[1] in properties:
                conditions.append({'if':{'required':[nonnull[1]],'properties':{nonnull[1]:{'not':{'type':'null'}}}},
                                   'then':{'required':[field],'properties':{field:{'not':{'type':'null'}}}}})
                condition['implementation']='JSON_SCHEMA_CONDITION'
        if conditions:record['allOf']=conditions
        schema={'$schema':shared['$schema'],'$id':BASE+name+'.schema.json',
                'description':'Structural interchange for dictionary entity '+name+'. Conformance does not certify review, truth, rights or implementation.',
                **strict({'schema_profile':{'const':'horisma-dictionary-structural-0.1.0'},'record_type':{'const':name},
                          'definition_stage':{'const':stage},'record':record}),
                'x-semantic-conditions':conditional,'x-dictionary-sha256':sha(doc.encode()),'x-vocabulary-sha256':sha(raw_vocab)}
        blank={k:None for k in properties};blank['missing_reasons']={'/'+k:'NOT_COLLECTED' for k in properties if k!='missing_reasons'}
        template={'template_only':True,'schema_ref':name+'.schema.json','record_type':name,'definition_stage':stage,
                  'authority':DICTIONARY,'required_unresolved_fields':required,'field_contracts':contracts,
                  'record_skeleton':blank,'warning':'Not an observation or valid record; fill required fields and verify references before interchange.'}
        files[name+'.schema.json']=schema;files[name+'.template.json']=template
        entries.append({'record_type':name,'definition_stage':stage,'schema':name+'.schema.json','template':name+'.template.json','field_count':len(properties)})
    if len(entries)!=55:raise ValueError('DICTIONARY_COVERAGE_CHANGED_REVIEW_REQUIRED')
    citation=citation_schema(shared['$schema']);files['citation_object.schema.json']=citation
    files['citation_object.template.json']={'template_only':True,'schema_ref':'citation_object.schema.json',
        'record_type':'citation_object','record_skeleton':{k:None for k in citation['properties']},
        'warning':'Witness and referenced earlier work are distinct. Never fill unknown identity, confidence or original text from model memory.'}
    entries.append({'record_type':'citation_object','definition_stage':'EXTENSION_CANDIDATE_PROFILE','schema':'citation_object.schema.json','template':'citation_object.template.json'})
    for name,properties in extension_fields().items():
        schema={'$schema':shared['$schema'],'$id':BASE+name+'.schema.json',
                **strict({'schema_profile':{'const':'horisma-'+name.replace('_','-')+'-0.1.0'},**properties})}
        files[name+'.schema.json']=schema
        files[name+'.template.json']={'template_only':True,'schema_ref':name+'.schema.json','record_type':name,
            'record_skeleton':{k:None for k in schema['properties']},'warning':'Blank structural scaffold, not observed or approved data.'}
        entries.append({'record_type':name,'definition_stage':'EXTENSION_STRUCTURE_DEFINED_ADAPTER_REQUIRED','schema':name+'.schema.json','template':name+'.template.json'})
    files['index.json']={'profile':'STRUCTURAL_CONTRACTS_NOT_SCIENTIFIC_ACCEPTANCE','dictionary_sha256':sha(doc.encode()),
        'vocabulary_sha256':sha(raw_vocab),'core_entities':55,'extension_entities':6,'entries':entries,
        'semantic_validation':'Partial; explicit conditions and research obligations remain in the authoritative dictionary/current plan.',
        'operational_policy':'Current local automated-or-abstain policy supersedes historical mandatory-human prose; schema conformance never grants review authority.'}
    stages={
        'INGEST':['work','document_version','source_file','acquisition_attempt','human_source_request'],
        'PARSE':['parse_unit','passage','artifact'],
        'ENTITY':['concept','lexical_form','sense','concept_family','taxonomy_assignment','contributor','identity_assertion','entity_mention','contribution_assertion'],
        'CITATION':['citation_object'],
        'EVIDENCE':['atomic_claim','search_scope','attribution_assertion','evidence_link','search_observation'],
        'REVIEW':['annotation','adjudication_policy','adjudication','discrepancy_finding','review_decision'],
        'EVENT':['event_card'],
        'BOOK':['manuscript_unit','book_edition','localization','correction','rights_decision'],
        'BENCHMARK':['dataset_version','split_assignment','benchmark_task','model_configuration','model_response','metric_definition','metric_observation','evaluation_context'],
        'STUDY':['project_protocol','research_question','hypothesis','sampling_frame','study_protocol','vignette_actor','vignette','participant','condition_assignment','behavioral_response'],
        'OPERATIONS':['actor','operator_run','task_lease','resource_observation','cost_audit','recovery_event','logical_statement','proof_record','pipeline_packet']}
    if {n for values in stages.values() for n in values}!={e['record_type'] for e in entries}:
        raise ValueError('UNMAPPED_INTERMEDIATE_LAYER')
    files['stage_interfaces.json']={'schema_profile':'horisma-stage-map-0.1.0','stages':{
        stage:{'record_schemas':[n+'.schema.json' for n in names],
               'transport_schema':'pipeline_packet.schema.json','migration_status':'STRUCTURES_DEFINED_EXISTING_ADAPTERS_NOT_FULLY_MIGRATED'}
        for stage,names in stages.items()},'current_live_projection':'Eight private Matthew citation objects conform structurally and bind exact reading bytes; this does not certify historical truth.'}
    out=root/DIRECTORY;out.mkdir(parents=True,exist_ok=True)
    for name,value in files.items():
        if name.endswith('.schema.json'):Draft202012Validator.check_schema(value)
        (out/name).write_bytes(encoded(value))
    return {'directory':str(out),'core_entities':55,'extension_entities':6,'files':len(files)}


def extension_fields():
    r=lambda name:{'$ref':'shared.schema.json#/$defs/'+name}
    text={'type':'string','minLength':1};refs={'type':'array','items':r('BoundRef')}
    geometry={'type':'array','minItems':4,'maxItems':4,'items':{'type':'number','minimum':0,'maximum':1}}
    return {
        'parse_unit':{'unit_id':text,'revision_sha256':r('sha256'),'unit_kind':{'enum':['PAGE','BLOCK','LINE']},
            'source_version_ref':r('BoundRef'),'parent_ref':nullable(r('BoundRef')),'text_binding':r('TextBinding'),
            'original_text':text,'pdf_page_index':{'type':'integer','minimum':0},'printed_page':nullable(text),
            'normalized_region':geometry,'page_dimensions_pdf_points':{'type':'array','minItems':2,'maxItems':2,'items':{'type':'number','exclusiveMinimum':0}},
            'extraction_mode':{'enum':['NATIVE','OCR','STRUCTURED_SOURCE']},'operator_run_ref':r('BoundRef'),'missing_reasons':{'type':'object','additionalProperties':r('v_missing_reason')}},
        'entity_mention':{'mention_id':text,'revision_sha256':r('sha256'),'text_binding':r('TextBinding'),'surface_text':text,
            'mention_kind':{'enum':['FULL_NAME','ALIAS','INITIALS','SURNAME','GIVEN_NAME','PRONOUN','TERM']},
            'candidate_entity_refs':refs,'antecedent_refs':refs,'resolution_status':{'enum':['UNRESOLVED','AMBIGUOUS','RESOLVED_CANDIDATE']},
            'context_binding':r('TextBinding'),'decision_artifact':nullable(r('ArtifactBinding')),'missing_reasons':{'type':'object','additionalProperties':r('v_missing_reason')}},
        'event_card':{'event_id':text,'revision_sha256':r('sha256'),'event_kind':r('v_historical_event_kind'),
            'event_time':r('TemporalExtent'),'account_time':r('TemporalExtent'),'system_recorded_at':{'type':'string','format':'date-time'},
            'event_proposition':text,'citation_refs':{'type':'array','minItems':1,'items':r('BoundRef')},'related_event_refs':refs,
            'qualification_ref':nullable(r('BoundRef')),'missing_reasons':{'type':'object','additionalProperties':r('v_missing_reason')}},
        'manuscript_unit':{'unit_id':text,'revision_sha256':r('sha256'),'edition_ref':r('BoundRef'),
            'unit_kind':{'enum':['PARAGRAPH','FIGURE','TABLE','CAPTION','EVIDENCE_NOTE']},'reader_text':text,'publication_mode':r('v_publication_mode'),
            'text_binding':r('TextBinding'),
            'claim_refs':refs,'citation_refs':refs,'material_uncertainties':{'type':'array','items':strict({'issue':text,'affected_claim_refs':refs,'impact_statement':text})},
            'review_ref':nullable(r('BoundRef')),'missing_reasons':{'type':'object','additionalProperties':r('v_missing_reason')}},
        'pipeline_packet':{'packet_id':text,'revision_sha256':r('sha256'),'stage':{'enum':['INGEST','PARSE','ENTITY','CITATION','EVIDENCE','REVIEW','EVENT','BOOK','BENCHMARK','STUDY','OPERATIONS']},
            'input_records':refs,'output_records':refs,'artifacts':{'type':'array','items':r('ArtifactBinding')},
            'operator_run_ref':nullable(r('BoundRef')),'execution_status':r('v_execution_status'),
            'scientific_review_ref':nullable(r('BoundRef')),'missing_reasons':{'type':'object','additionalProperties':r('v_missing_reason')}}}


def citation_schema(dialect):
    ref=lambda name:{'$ref':'shared.schema.json#/$defs/'+name}
    text={'type':'string','minLength':1}
    return {'$schema':dialect,'$id':BASE+'citation_object.schema.json',
        **strict({'schema_profile':{'const':'horisma-citation-object-0.1.0'},'citation_id':text,'revision_sha256':ref('sha256'),
            'witness_work_ref':ref('BoundRef'),'witness_version_ref':ref('BoundRef'),
            'authors':nullable({'type':'array','items':strict({'person_ref':ref('BoundRef'),'source_display_name':text})}),
            'author_list_complete':{'type':'boolean'},'source_kind':ref('v_source_kind'),
            'source_locator':strict({'pdf_page_index':{'type':'integer','minimum':0},'printed_page':nullable(text),
                'normalized_region':nullable({'type':'array','minItems':4,'maxItems':4,'items':{'type':'number','minimum':0,'maximum':1}})}),
            'reading_binding':ref('TextBinding'),'reading_text':text,'diplomatic_text':nullable(text),
            'reading_entry_status':{'enum':['PAPER2SKILL_BOUND','FROZEN_FRAGMENT_EXCEPTION']},
            'related_passage_refs':{'type':'array','items':ref('BoundRef')},
            'normalization_operations':{'type':'array','items':strict({'operation_id':text,'description':text,'verification_state':{'enum':['DECLARED','UNVERIFIED','VERIFIED_TRANSFORMATION']}})},
            'abbreviations':nullable({'type':'array','items':strict({'surface':text,'expansion':nullable(text),'evidence_ref':nullable(ref('BoundRef'))})}),
            'citation_mode':{'enum':['DIRECT_SOURCE_TEXT','INDIRECT_QUOTATION','PARAPHRASE']},
            'referenced_work_ref':nullable(ref('BoundRef')),'referenced_original_inspected':{'type':'boolean'},
            'evidence_group_ref':text,'source_identity_status':ref('v_source_identity_status'),
            'confidence':{'const':None},'confidence_missing_reason':{'const':'NOT_ASSESSED'},
            'support_scope':text,'missing_reasons':{'type':'object','additionalProperties':ref('v_missing_reason')},
            'scientific_acceptance':{'const':False},'publication_authorized':{'const':False}}),
        'allOf':[{'if':{'properties':{'citation_mode':{'const':'INDIRECT_QUOTATION'}}},
                  'then':{'properties':{'referenced_work_ref':ref('BoundRef'),'referenced_original_inspected':{'const':False}}}},
                 {'if':{'properties':{'citation_mode':{'const':'DIRECT_SOURCE_TEXT'}}},
                  'then':{'properties':{'referenced_work_ref':{'type':'null'},'referenced_original_inspected':{'const':False}}}}]}


def validate_interchange(root, document):
    if not isinstance(document,dict):raise ValueError('JSON_RECORD_OBJECT_REQUIRED')
    encoded(document)  # Reject NaN/Infinity even if a JSON decoder admitted them.
    root=Path(root).resolve();directory=root/DIRECTORY
    profile=document.get('schema_profile','')
    extension_names=['citation_object',*extension_fields()]
    name=next((n for n in extension_names if profile=='horisma-'+n.replace('_','-')+'-0.1.0'),document.get('record_type',''))
    if not isinstance(name,str) or not re.fullmatch('[a-z_]+',name):raise ValueError('UNKNOWN_JSON_RECORD_TYPE')
    resources=[]
    for path in directory.glob('*.schema.json'):
        value=json.loads(path.read_bytes());resources.append((value['$id'],Resource.from_contents(value)))
    registry=Registry().with_resources(resources)
    schema=json.loads((directory/(name+'.schema.json')).read_bytes())
    try:
        Draft202012Validator(schema,registry=registry,format_checker=FormatChecker()).validate(document)
    except ValidationError as exc:
        raise ValueError('INVALID_JSON_RECORD at /'+'/'.join(map(str,exc.absolute_path))+': '+exc.message) from exc
    record=document if name in extension_names else document['record']
    missing=record.get('missing_reasons',{})
    allowed=schema['properties'] if name in extension_names else schema['properties']['record']['properties']
    for pointer in missing:
        if not pointer.startswith('/') or re.search(r'~(?![01])',pointer):raise ValueError('INVALID_MISSING_POINTER:'+pointer)
        parts=[p.replace('~1','/').replace('~0','~') for p in pointer[1:].split('/')]
        if parts[0] not in allowed or 'missing_reasons' in parts:raise ValueError('UNRELATED_MISSING_REASON:'+pointer)
        parent=record
        for part in parts[:-1]:
            if isinstance(parent,dict) and part in parent:parent=parent[part]
            elif isinstance(parent,list) and re.fullmatch(r'0|[1-9][0-9]*',part) and int(part)<len(parent):parent=parent[int(part)]
            else:raise ValueError('ABSENT_MISSING_PARENT:'+pointer)
        last=parts[-1]
        if isinstance(parent,dict):
            if last not in parent:
                if len(parts)!=1:raise ValueError('UNDECLARED_NESTED_MISSING_FIELD:'+pointer)
            elif parent[last] is not None:raise ValueError('KNOWN_VALUE_HAS_MISSING_REASON:'+pointer)
        elif isinstance(parent,list) and re.fullmatch(r'0|[1-9][0-9]*',last) and int(last)<len(parent):
            if parent[int(last)] is not None:raise ValueError('KNOWN_VALUE_HAS_MISSING_REASON:'+pointer)
        else:raise ValueError('ABSENT_MISSING_TARGET:'+pointer)
    def missing_values(value,path=''):
        if value is None:
            if path not in missing:raise ValueError('NULL_REQUIRES_MISSING_REASON:'+path)
        elif isinstance(value,dict):
            for key,item in value.items():
                if key!='missing_reasons':missing_values(item,path+'/'+key.replace('~','~0').replace('/','~1'))
        elif isinstance(value,list):
            for i,item in enumerate(value):missing_values(item,path+'/'+str(i))
    missing_values(record)
    if name not in extension_names:
        from datetime import datetime,timedelta
        created=datetime.fromisoformat(record['created_at'].replace('Z','+00:00'))
        if 'T' not in record['created_at'] or created.utcoffset()!=timedelta(0):raise ValueError('CREATED_AT_REQUIRES_UTC_DATETIME')
        for key in schema['properties']['record']['properties']:
            if key not in record and '/'+key not in missing:raise ValueError('OMITTED_FIELD_REQUIRES_MISSING_REASON:'+key)
        for key,field in schema['properties']['record']['properties'].items():
            value=record.get(key)
            if value is None:continue
            if field.get('x-logical-type')=='CreditAllocation':
                if len({i['actor_ref'] for i in value})!=len(value) or abs(sum(i['share'] for i in value)-1)>1e-6:
                    raise ValueError('INVALID_CREDIT_ALLOCATION')
            if field.get('x-logical-type')=='TemporalExtent':
                if value['normalized_lower'] and value['normalized_upper'] and value['normalized_lower']>value['normalized_upper']:
                    raise ValueError('INVERTED_TEMPORAL_EXTENT')
            if field.get('x-logical-type')=='PassageLocator':
                if value['region'] is not None:
                    from .research_slice import normalize_region
                    normalize_region(value['region'],1,1)
                if value['anchor_kind']=='IMAGE_REGION' and (value['region'] is None or value['pdf_page_index'] is None):
                    raise ValueError('IMAGE_LOCATOR_REQUIRES_REGION_AND_PAGE')
                if value['anchor_kind']=='TEXT_OFFSETS' and (value['derivative_artifact_ref'] is None
                        or value['start_offset'] is None or value['end_offset'] is None
                        or value['start_offset']>=value['end_offset']):raise ValueError('INVALID_TEXT_LOCATOR')
        if name=='metric_observation':
            if record['measurement_status']!='DEFINED' and record.get('value') is not None:raise ValueError('UNDEFINED_METRIC_HAS_VALUE')
            if record.get('denominator')==0 and record['measurement_status']=='DEFINED':raise ValueError('ZERO_DENOMINATOR_NOT_DEFINED')
            if any(record.get(k) is not None and record[k]<0 for k in ['numerator','denominator']):raise ValueError('NEGATIVE_METRIC_COUNT')
    if name=='citation_object':
        if record['source_locator']['normalized_region'] is not None:
            from .research_slice import normalize_region
            normalize_region(record['source_locator']['normalized_region'],1,1)
        if bound_text(root,record['reading_binding'])!=record['reading_text']:raise ValueError('CITATION_SPAN_MISMATCH')
    if name in {'parse_unit','entity_mention','manuscript_unit'}:
        field={'parse_unit':'original_text','entity_mention':'surface_text','manuscript_unit':'reader_text'}[name]
        if bound_text(root,record['text_binding'])!=record[field]:raise ValueError('TEXT_BINDING_MISMATCH')
        if name=='entity_mention':bound_text(root,record['context_binding'])
    if name in extension_names and 'revision_sha256' in record:
        content=copy.deepcopy(record);content.pop('revision_sha256')
        if sha(encoded(content))!=record['revision_sha256']:raise ValueError('INTERCHANGE_REVISION_CHANGED')
    return {'structurally_valid':True,'record_type':name,'scientific_acceptance':False,
            'reference_resolution':'NOT_CHECKED','scope':'STRUCTURE_AND_BOUND_BYTES_NOT_RESEARCH_ADJUDICATION'}


def bound_text(root,binding):
    raw=read(root,binding['artifact']['path'])
    if sha(raw)!=binding['artifact']['sha256']:raise ValueError('TEXT_ARTIFACT_CHANGED')
    start,end=binding['unicode_start'],binding['unicode_end']
    if type(start) is not int or type(end) is not int:raise ValueError('TEXT_OFFSETS_REQUIRE_INTEGERS')
    text=raw.decode('utf-8')
    if not 0<=start<end<=len(text):raise ValueError('INVALID_TEXT_SPAN')
    return text[start:end]
