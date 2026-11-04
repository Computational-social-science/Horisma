"""Optional local byte-pattern observer. Never a PDF/OCR parser or truth judge."""
from __future__ import annotations

import math
import hashlib
import importlib.util
import json
from pathlib import Path
import time

from .operators import ContractError, digest

CODE_REVISION = '1e62eeb8ebbc3a314fa10d784fd8e1d56c72927f'
WEIGHTS_REVISION = '20de84b6a178af5c7824f823bd0058452db2b360'
WEIGHTS_SHA256 = '385b7b21cae8605dbc4fe0611b6a78576017260824011a0cbe402e3014061c0e'
CONFIG_SHA256 = '89512b28c6ea1ba0881de90fe60ed1a2c77ea3963f5b1b2942c6a605978ae5fb'
CODE_FINGERPRINT = 'c12c8cc00a4b68c02aac68941174b5a9ebe022a4352d94a6f2733dba9759a70c'


def _validated_bits(bits, expected_length):
    if hasattr(bits,'detach'):
        bits=bits.detach().cpu().tolist()
    values=list(bits)
    if len(values)!=expected_length or any(not isinstance(x,(int,float)) or not math.isfinite(x) or x<0 for x in values):
        raise ContractError('INVALID_BYTE_SCORE')
    return values


def load_local_pflm(model_directory: Path):
    """Use the installed audited code and local safetensors; never download at inference."""
    installed=importlib.util.find_spec('pflm1')
    if installed is None:raise ContractError('OPTIONAL_PFLM_UNAVAILABLE')
    code_folder=Path(installed.origin).parent
    code_files={p.name:digest(p.read_bytes().replace(b'\r\n',b'\n')) for p in sorted(code_folder.glob('*.py'))}
    if digest(json.dumps(code_files,sort_keys=True,separators=(',',':')).encode()) != CODE_FINGERPRINT:
        raise ContractError('PFLM_INSTALLED_CODE_MISMATCH')
    for name,expected in [('model.safetensors',WEIGHTS_SHA256),('config.json',CONFIG_SHA256)]:
        path=model_directory/name
        if not path.is_file():raise ContractError('LOCAL_PFLM_WEIGHTS_UNAVAILABLE')
        with path.open('rb') as stream:
            actual=hashlib.file_digest(stream,'sha256').hexdigest()
        if actual!=expected:raise ContractError('PFLM_WEIGHT_OR_CONFIG_MISMATCH')
    try:
        import pflm1  # registers the installed implementation, not remote model code
        import torch
        from transformers import AutoModelForCausalLM
    except ImportError as exc:
        raise ContractError('OPTIONAL_PFLM_UNAVAILABLE') from exc
    torch.set_num_threads(min(6,torch.get_num_threads()))
    model=AutoModelForCausalLM.from_pretrained(str(model_directory),local_files_only=True,
        trust_remote_code=False,use_safetensors=True,dtype=torch.float32)
    model=model.cpu().eval()
    model.horisma_pflm_provenance={'code_revision':CODE_REVISION,'weights_revision':WEIGHTS_REVISION,
        'weights_sha256':WEIGHTS_SHA256,'code_fingerprint':CODE_FINGERPRINT}
    return model


def score_text_bytes(model, text: bytes, *, chunk: int = 256, max_bytes: int = 16384) -> dict:
    if chunk<1 or max_bytes<1 or len(text)>max_bytes:
        raise ContractError('BYTE_RESOURCE_LIMIT')
    if text.startswith(b'%PDF-'):
        raise ContractError('PFLM_REQUIRES_EXTRACTED_TEXT')
    try:text.decode('utf-8',errors='strict')
    except UnicodeError as exc:raise ContractError('INVALID_UTF8_TEXT') from exc
    started=time.monotonic()
    provenance=getattr(model,'horisma_pflm_provenance',{})
    verified=isinstance(provenance,dict) and all(provenance.get(k)==v for k,v in
        {'code_revision':CODE_REVISION,'weights_revision':WEIGHTS_REVISION,
         'weights_sha256':WEIGHTS_SHA256,'code_fingerprint':CODE_FINGERPRINT}.items())
    if not verified:provenance={}
    values=_validated_bits(model.bits_per_byte(text,chunk=chunk),len(text)) if text else []
    return {'operator_id':'HEX-PFLM-BYTE-PATTERN','input_sha256':digest(text),'byte_count':len(text),
        'measurement_status':'DEFINED' if values else 'NOT_DEFINED',
        'mean_bits_per_byte':math.fsum(values)/len(values) if values else None,
        'missing_reasons':{} if values else {'mean_bits_per_byte':'NOT_DEFINED'},
        'bits_per_byte':values,'chunk_bytes':chunk,'elapsed_seconds':time.monotonic()-started,
        'first_byte_policy':'UNIFORM_8_BITS','score_kind':'BYTE_PREDICTION_COST_NOT_FACT_CONFIDENCE',
        'source_modified':False,'scientific_approval_granted':False,'model_binding_verified':verified,
        'code_revision':provenance.get('code_revision'),'weights_revision':provenance.get('weights_revision')}


def rank_pattern_labels(model, context: bytes, labels: tuple[bytes,...]) -> dict:
    """Experimental ICL verbalizer comparison; requires an independent recall study."""
    if not context or len(context)>8192 or len(labels)<2 or len(set(labels))!=len(labels):
        raise ContractError('INVALID_PATTERN_TASK')
    if any(not label or len(label)>32 for label in labels):raise ContractError('INVALID_PATTERN_LABEL')
    if len({len(label) for label in labels})!=1:raise ContractError('PATTERN_LABEL_LENGTH_MISMATCH')
    if context.startswith(b'%PDF-'):raise ContractError('PFLM_REQUIRES_EXTRACTED_TEXT')
    context.decode('utf-8',errors='strict')
    costs=[]
    prefix_evaluations=0
    shared=None
    if len(labels[0])==1:
        shared=model.stream(chunk=256)
        if hasattr(shared,'next_byte_logits'):
            shared.feed(context)
            prefix_evaluations=1
        else:shared=None
    logits=shared.next_byte_logits() if shared is not None and hasattr(shared,'next_byte_logits') else None
    if logits is not None:
        if hasattr(logits,'tolist'):logits=logits.tolist()
        if len(logits)!=256 or any(not isinstance(x,(float,int)) or not math.isfinite(x) for x in logits):
            raise ContractError('INVALID_BYTE_LOGITS')
        pivot=max(range(256),key=lambda i:logits[i])
        maximum=logits[pivot]
        correction=math.log1p(math.fsum(math.exp(x-maximum) for i,x in enumerate(logits) if i!=pivot))
        for label in labels:
            bits=(maximum-logits[label[0]]+correction)/math.log(2)
            _validated_bits([bits],1)
            costs.append({'label':label.decode('utf-8'),'conditional_total_bits':bits,'label_bytes':1})
    for label in labels:
        if logits is not None:break
        label.decode('utf-8',errors='strict')
        stream=model.stream(chunk=256)
        stream.feed(context)
        prefix_evaluations+=1
        bits=_validated_bits(stream.feed(label),len(label))
        costs.append({'label':label.decode('utf-8'),'conditional_total_bits':math.fsum(bits),'label_bytes':len(label)})
    ordered=sorted(costs,key=lambda x:x['conditional_total_bits'])
    tied=abs(ordered[0]['conditional_total_bits']-ordered[1]['conditional_total_bits'])<1e-6
    return {'operator_id':'HEX-PFLM-ICL-RANK','context_sha256':digest(context),'label_costs':costs,
        'preferred_label':None if tied else ordered[0]['label'],'top_labels_tied':tied,
        'prefix_evaluations':prefix_evaluations,'label_scoring':'float64_log1p_shifted_logits' if logits is not None else 'stream_continuation_bits',
        'calibrated_probability':None,'automatic_exclusion_authorized':False,
        'evidence_support_decision':None,'qualification':'SYNTHETIC_OR_EXPLORATORY_ONLY'}
