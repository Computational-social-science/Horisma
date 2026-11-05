"""Reversible correction proposals; no grammar polishing of source quotations."""
import hashlib
import re
import math
from difflib import SequenceMatcher

VIEWS={'diplomatic','normalized','editorial'}
KINDS={'OCR_REPAIR','TYPOGRAPHIC_NORMALIZATION','EDITORIAL_GRAMMAR'}
PROTECTED=set('no not never neither nor without cannot may might could must should can will would claimed claims alleged suggests suggest coined coin coining named naming published publish invented discovered developed authorship author contribution contributors interviews interview recognition credit first earliest only sole joint exclusively all some many each every both more less comparable'.split())
COMMON_CAPITALIZED={'The','This','That','It','Their','A','An','In','Of','For','As','But','And'}


def text_sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def signature(text):
    words=re.findall(r"[A-Za-z]+(?:['\u2019][A-Za-z]+)?",text)
    return {'numbers':re.findall(r'\d+',text),
            'numeric_expressions':[re.sub(r'\s+','',m) for m in re.findall(r'(?:(?:<=|>=|!=|==|[<>\u2264\u2265\u2260\u2248=])\s*)?(?:[+\-\u2212]\s*)?\d+(?:[.,]\d+)*(?:[eE]\s*[+\-]?\s*\d+)?\s*%?',text)],
            'numeric_ranges':[re.sub(r'\s+','',m) for m in re.findall(r'\d+\s*[-\u2013\u2014:/]\s*\d+',text)],
            'protected_words':[w.casefold() for w in words if w.casefold() in PROTECTED],
            'negative_contractions':[w.casefold().replace('\u2019',"'") for w in words if w.casefold().replace('\u2019',"'").endswith("n't")],
            'identities':[w for w in words if w[:1].isupper() and w not in COMMON_CAPITALIZED],
            'citation_marks':re.findall(r'[\[\]]',text),
            'quotation_marks':re.findall(r'["\u201c\u201d]',text)}


def assess_proposal(text,proposal,max_edit_fraction=.15):
    if type(max_edit_fraction) not in (int,float) or not math.isfinite(max_edit_fraction) or not 0<=max_edit_fraction<=1:raise ValueError('INVALID_EDIT_BUDGET')
    if proposal.get('input_sha256')!=text_sha(text):raise ValueError('STALE_CORRECTION_INPUT')
    view=proposal.get('view')
    if view not in VIEWS or not isinstance(proposal.get('edits'),list):raise ValueError('INVALID_CORRECTION_VIEW_OR_EDITS')
    edits=proposal['edits']
    previous=0;parts=[]
    for e in edits:
        if not isinstance(e,dict):raise ValueError('TYPED_EDIT_REQUIRED')
        if set(e)!={'start','end','original','replacement','kind','rationale'}:raise ValueError('TYPED_EDIT_FIELDS_REQUIRED')
        start,end=e['start'],e['end']
        if (type(start) is not int or type(end) is not int or not previous<=start<=end<=len(text)
                or not isinstance(e['replacement'],str) or not isinstance(e['rationale'],str)
                or not isinstance(e['kind'],str) or e['kind'] not in KINDS or text[start:end]!=e['original']):raise ValueError('INVALID_OR_OVERLAPPING_EDIT')
        parts.extend([text[previous:start],e['replacement']]);previous=end
    parts.append(text[previous:]);candidate=''.join(parts)
    before,after=signature(text),signature(candidate)
    protected=[key for key in before if before[key]!=after[key]]
    fraction=1-SequenceMatcher(None,text,candidate,autojunk=False).ratio()
    if not edits:status='NO_EDIT'
    elif protected:status='BLOCKED_CRITICAL_EDIT'
    elif view!='editorial' and any(e['kind']=='EDITORIAL_GRAMMAR' for e in edits):status='BLOCKED_GRAMMAR_OUTSIDE_EDITORIAL_VIEW'
    elif fraction>max_edit_fraction:status='BLOCKED_EXCESSIVE_REWRITE'
    elif view=='editorial':status='EDITORIAL_DERIVATIVE_ONLY'
    else:status='REQUIRES_QUALIFIED_IMAGE_AND_SEMANTIC_REVIEW'
    return {'input_sha256':text_sha(text),'original_text':text,'candidate_text':candidate,'view':view,
            'edits':edits,'candidate_sha256':text_sha(candidate),'protected_changes':protected,
            'edit_fraction':fraction,'gate_status':status,'transcription_accepted':False,
            'verbatim_quote_eligible':False,'scientific_acceptance':False,
            'limitation':'Heuristic overcorrection guard; unflagged changes are not proof of semantic equivalence.'}
