"""Typed claim/passage edges; integrity never grants semantic qualification."""
from jsonschema import Draft202012Validator
from .operators import digest
from html import escape

SCHEMA = {'type':'object','additionalProperties':False,
 'required':['id','relation','claim','source','passage','rationale','limitations','qualification'],
 'properties':{
  'id':{'type':'string','minLength':1},
  'relation':{'enum':['REPORTS','SUPPORTS','CONTRADICTS','LIMITS']},
  'claim':{'type':'object','additionalProperties':False,'required':['id','text','sha256'],
   'properties':{'id':{'type':'string','minLength':1},'text':{'type':'string','minLength':1},'sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'}}},
  'source':{'type':'object','additionalProperties':False,'required':['id','revision','sha256'],
   'properties':{k:{'type':'string','minLength':1} for k in ['id','revision','sha256']}},
  'passage':{'type':'object','additionalProperties':False,'required':['record_id','record_revision','text','sha256','locator'],
   'properties':{k:{'type':'string','minLength':1} for k in ['record_id','record_revision','text','sha256','locator']}},
  'rationale':{'type':'string','minLength':1},
  'limitations':{'type':'array','minItems':1,'items':{'type':'string','minLength':1}},
  'qualification':{'type':'object','additionalProperties':False,'required':['status','reason','policy'],
   'properties':{'status':{'const':'UNQUALIFIED'},'reason':{'type':'string','minLength':1},'policy':{'const':'horisma-auto-review-0.1.0'}}}}}


def validate_claim_edge(edge, view):
    if list(Draft202012Validator(SCHEMA).iter_errors(edge)):
        raise ValueError('INVALID_TYPED_CLAIM_EDGE')
    if digest(edge['claim']['text'].encode())!=edge['claim']['sha256'] or digest(edge['passage']['text'].encode())!=edge['passage']['sha256']:
        raise ValueError('CLAIM_OR_PASSAGE_CHANGED')
    source=view['table'][edge['source']['id']]
    record=view['table'][edge['passage']['record_id']]
    if source['revision']!=edge['source']['revision'] or record['revision']!=edge['passage']['record_revision']:
        raise ValueError('STALE_EDGE_REVISION')
    comparison=record['payload']['source_comparison']
    if comparison['source_sha256']!=edge['source']['sha256'] or source['payload']['source_sha256']!=edge['source']['sha256'] or comparison['extracted_text']!=edge['passage']['text'] or comparison['locator']!=edge['passage']['locator']:
        raise ValueError('EDGE_NOT_BOUND_TO_PASSAGE')
    if not any(d['entity_id']==edge['source']['id'] and d['revision']==edge['source']['revision'] for d in record['dependencies']):
        raise ValueError('EDGE_SOURCE_DEPENDENCY_MISSING')
    return {'integrity':'BOUND','semantic_status':'UNQUALIFIED','scientific_acceptance':False}


def edge_markup(edge):
    h=escape
    return '<figure class="claim-graph"><figcaption>'+h(edge['id'])+' · '+h(edge['relation'])+' · UNQUALIFIED</figcaption><div class="edge-node"><strong>Source version</strong><br>'+h(edge['source']['id'])+'<br><small>'+h(edge['passage']['locator'])+'</small></div><p class="edge-arrow" aria-label="proposed reporting connection">↓ '+h(edge['relation'])+' / proposed</p><div class="edge-node"><strong>Atomic claim candidate</strong><p>'+h(edge['claim']['text'])+'</p></div><details><summary>Reason, limitations & qualification</summary><p>'+h(edge['rationale'])+'</p><ul>'+''.join('<li>'+h(x)+'</li>' for x in edge['limitations'])+'</ul><p>'+h(edge['qualification']['reason'])+'</p></details></figure>'
