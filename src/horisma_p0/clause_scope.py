"""Offset-preserving sentence candidates and conservative quotation/negation cues."""
import re
from .role_context import role_proposal

ABBREVIATIONS = {'st', 'dr', 'prof', 'mr', 'mrs', 'ms', 'fig', 'pp', 'vol', 'vs', 'etc'}


def quotation_spans(text):
    spans, opened, ambiguous = [], None, False
    for i, char in enumerate(text):
        if opened is None and char in {'“', '"'}:
            opened = (i, '”' if char == '“' else '"')
        elif opened is None and char == '”':
            ambiguous = True
        elif opened is not None and char == '“':
            ambiguous = True
        elif opened is not None and char == opened[1]:
            spans.append((opened[0], i+1))
            opened = None
    if opened is not None:
        spans.append((opened[0], len(text)))
    return spans, opened is not None or ambiguous, ambiguous


def segment(text, *, base_offset=0):
    if not isinstance(text, str) or type(base_offset) is not int or base_offset < 0:
        raise ValueError('INVALID_TEXT_OR_BASE_OFFSET')
    quotes, unmatched, ambiguous = quotation_spans(text)
    boundaries = [0]
    for m in re.finditer(r'[.!?;][”"]*(?=\s+|$)', text):
        i = m.start()
        if text[i] == '.':
            token = re.search(r'([A-Za-z]+)$', text[:i])
            if token and (len(token[1]) == 1 or token[1].lower() in ABBREVIATIONS):
                continue
        # A semicolon inside quotation is not a reliable boundary.
        if text[i] == ';' and any(a < i < b for a,b in quotes):
            continue
        boundaries.append(m.end())
    boundaries.append(len(text))
    records = []
    for lo, hi in zip(boundaries, boundaries[1:]):
        while lo < hi and text[lo].isspace():
            lo += 1
        while hi > lo and text[hi-1].isspace():
            hi -= 1
        if lo == hi:
            continue
        fragment = text[lo:hi]
        cues = []
        for match in re.finditer(r"\b(?:not|never|no|neither|without|cannot)\b|\b\w+n['’]t\b", fragment, re.I):
            start, end = lo+match.start(), lo+match.end()
            cues.append({'start': base_offset+start, 'end': base_offset+end,
                         'text': match[0], 'inside_quote': None if ambiguous else any(a <= start < b for a,b in quotes)})
        records.append({'start': base_offset+lo, 'end': base_offset+hi, 'text': fragment,
            'role_proposal': role_proposal(fragment), 'negation_cues': cues,
            'quote_intersections': [{'start':base_offset+max(lo,a),'end':base_offset+min(hi,b)} for a,b in quotes if a < hi and b > lo],
            'reporting_cue': bool(re.search(r'\b(says?|said|reports?|according to|states?)\b', fragment, re.I)),
            'unmatched_quote_in_input': unmatched,
            'ambiguous_quotation_structure': ambiguous,
            'boundary_status': 'CANDIDATE_NOT_ATOMIC_OR_GRAMMATICALLY_QUALIFIED',
            'negation_scope_resolved': False, 'speaker_resolved': False,
            'historical_assessment': None})
    return records
