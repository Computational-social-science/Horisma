"""Lossless quotation annotations; syntactic balance never establishes OCR fidelity."""
import re

from .research_slice import encoded, sha


def quote_structure(text, namespace='content-variant'):
    if not isinstance(text, str):
        raise ValueError('TEXT_REQUIRED')
    digest = sha(text.encode())
    pairs = {'‘': '’', '“': '”', '«': '»', '‹': '›', '"': '"', "'": "'"}
    stack, quotes, problems, delimiters = [], [], [], []
    for offset, char in enumerate(text):
        if char not in set(pairs) | set(pairs.values()):
            continue
        # Internal apostrophes are lexical characters, not quotation boundaries.
        if char in {"'", '’', '‘'} and 0 < offset < len(text)-1 and text[offset-1].isalnum() and text[offset+1].isalnum():
            continue
        delimiters.append({'offset': offset, 'character': char})
        if stack and char == stack[-1]['closer']:
            item = stack.pop()
            item.update(end=offset+1, literal_text=text[item['start']:offset+1], state='CLOSED')
        elif char in pairs:
            item = {'quote_id': 'quote:' + sha(encoded([namespace, digest, offset])), 'start': offset, 'end': None,
                    'depth': len(stack)+1, 'parent_id': stack[-1]['quote_id'] if stack else None,
                    'opener': char, 'closer': pairs[char], 'speaker_ref': None,
                    'speaker_status': 'UNRESOLVED_REQUIRES_SOURCE_BOUND_CONTEXT', 'state': 'OPEN'}
            quotes.append(item)
            stack.append(item)
        else:
            problems.append({'offset': offset, 'character': char, 'reason': 'UNMATCHED_CLOSER'})
    for item in stack:
        problems.append({'offset': item['start'], 'character': item['opener'], 'reason': 'UNCLOSED_OPENER'})
    markers = [{'start': m.start(), 'end': m.end(), 'literal_text': m.group(),
                'interpretation': 'BRACKETED_TEXT_NOT_VERIFIED_AS_ORIGINAL_OR_EDITORIAL'}
               for m in re.finditer(r'\[[^\[\]\n]{1,80}\]', text)]
    bracket_stack, bracket_problems = [], []
    for offset, char in enumerate(text):
        if char == '[': bracket_stack.append(offset)
        elif char == ']':
            if bracket_stack: bracket_stack.pop()
            else: bracket_problems.append({'offset': offset, 'reason': 'UNMATCHED_BRACKET_CLOSER'})
    bracket_problems.extend({'offset': offset, 'reason': 'UNCLOSED_BRACKET'} for offset in bracket_stack)
    return {'text_sha256': digest, 'namespace': namespace, 'status': 'NO_TEXT' if not text.strip() else
            ('UNRESOLVED_DELIMITERS' if problems else 'BALANCED_SYNTAX_ONLY'),
            'quotes': quotes, 'delimiters': delimiters, 'problems': problems, 'editorial_markers': markers,
            'bracket_status': 'UNRESOLVED_BRACKETS' if bracket_problems else 'BALANCED_BRACKETS_ONLY',
            'bracket_problems': bracket_problems,
            'maximum_depth': max((q['depth'] for q in quotes), default=0),
            'limitation': 'Same-delimiter nesting, possessives and historical conventions can remain ambiguous; no speaker or transcription authority follows.',
            'fidelity_qualified': False, 'scientific_acceptance': False}


def compare_quote_structure(reference_variant, observed_variant):
    reference, observed = quote_structure(reference_variant), quote_structure(observed_variant)
    sequence = lambda result: [item['character'] for item in result['delimiters']]
    return {'reference_variant': reference, 'observed': observed,
            'reference_status': 'VARIANT_NOT_AUTOMATICALLY_GROUND_TRUTH',
            'delimiter_sequence_changed': sequence(reference) != sequence(observed),
            'maximum_depth_changed': reference['maximum_depth'] != observed['maximum_depth'],
            'literal_text_changed': reference_variant != observed_variant,
            'fidelity_qualified': False, 'scientific_acceptance': False}
