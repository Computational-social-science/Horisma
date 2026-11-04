"""Deterministic candidate retrieval and citation linkage, without support judgments."""
import re

from .operators import ContractError,digest

ATTRIBUTION_CUES=re.compile(r'\b(?:coin(?:ed|ing)?|nam(?:ed|ing)|introduc(?:ed|tion)|attribut(?:ed|ion)|originat(?:ed|or)|authorship)\b',re.IGNORECASE)


def retrieve_attribution_candidates(paragraphs: list[dict], aliases: list[str], source_sha256: str) -> list[dict]:
    """Recall-oriented literal retrieval; returns candidates and never discards originals."""
    if not aliases or any(not name.strip() for name in aliases):raise ContractError('TARGET_ALIASES_REQUIRED')
    if not re.fullmatch(r'[0-9a-f]{64}',source_sha256):raise ContractError('SOURCE_DIGEST_INVALID')
    terms=re.compile('|'.join(re.escape(name) for name in sorted(aliases,key=len,reverse=True)),re.IGNORECASE)
    hits=[]
    for paragraph in paragraphs:
        text=paragraph['text']
        if terms.search(text) and ATTRIBUTION_CUES.search(text):
            hits.append({'paragraph_id':paragraph['paragraph_id'],'source_sha256':source_sha256,
                'paragraph_text_sha256':digest(text.encode('utf-8')),'selection':'LEXICAL_CANDIDATE_NOT_EVIDENCE',
                'original_retained':True,'review_status':'PENDING','support_assessment':None})
    return hits


def link_numeric_citations(paragraph: str, bibliography: dict[str,dict], source_sha256: str) -> list[dict]:
    """Resolve explicit numeric markers only; CITES never implies SUPPORTS."""
    if not re.fullmatch(r'[0-9a-f]{64}',source_sha256):raise ContractError('SOURCE_DIGEST_INVALID')
    links=[]
    for match in re.finditer(r'\[(\d+(?:\s*[,;]\s*\d+)*)\]',paragraph):
        for marker in re.split(r'\s*[,;]\s*',match.group(1)):
            target=bibliography.get(marker)
            if target is not None and target.get('source_sha256') != source_sha256:
                raise ContractError('CITATION_DOCUMENT_MISMATCH')
            linked=target is not None and isinstance(target.get('reference_id'),str) and bool(target['reference_id'].strip())
            links.append({'citation_marker':marker,'character_start':match.start(),'character_end':match.end(),
                'source_sha256':source_sha256,'paragraph_text_sha256':digest(paragraph.encode('utf-8')),
                'target_reference_id':target['reference_id'] if linked else None,
                'link_status':'LINKED_NOT_VERIFIED' if linked else 'UNRESOLVED',
                'relation':'CITES_CANDIDATE','support_assessment':None})
    return links
