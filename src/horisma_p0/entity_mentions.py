"""Local surface-form matching and bounded coreference annotations, never edits."""
from difflib import SequenceMatcher
import re
import unicodedata

from .research_slice import encoded, sha

SHORT_FORMS = {'GIVEN_ONLY', 'FAMILY_ONLY'}
FIRST_PERSON = {'i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours'}
PRONOUNS = re.compile(r'\b(?:I|me|my|mine|we|us|our|ours|he|him|his|she|her|hers|they|them|their|theirs)\b', re.I)


def script_codes(text):
    scripts = set()
    for character in text:
        if not character.isalpha():
            continue
        name = unicodedata.name(character, '')
        for prefix, code in [('LATIN', 'Latn'), ('CYRILLIC', 'Cyrl'), ('ARABIC', 'Arab'),
                             ('CJK', 'Hani'), ('HIRAGANA', 'Hira'), ('KATAKANA', 'Kana'),
                             ('HEBREW', 'Hebr'), ('GREEK', 'Grek'), ('HANGUL', 'Hang')]:
            if name.startswith(prefix):
                scripts.add(code); break
        else:
            scripts.add('Zzzz')
    return sorted(scripts) or ['Zyyy']


def surface_pattern(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError('NONEMPTY_NAME_FORM_REQUIRED')
    pattern = r'\s+'.join(re.escape(part) for part in text.split())
    # Han words need not have spaces; do not infer segmentation within a name.
    han_start = 'Hani' in script_codes(text[:1])
    han_end = 'Hani' in script_codes(text[-1:])
    return ('' if han_start else r'(?<!\w)') + pattern + ('' if han_end else r'(?!\w)')


def paragraph_scopes(text):
    ranges=[];start=0
    for boundary in re.finditer(r'\n[^\S\n]*\n',text):
        ranges.append((start,boundary.start()));start=boundary.end()
    ranges.append((start,len(text)))
    scopes=[]
    for left,right in ranges:
        fragment=text[left:right]
        if not fragment.strip():
            continue
        trimmed_left=left+len(fragment)-len(fragment.lstrip())
        trimmed_right=right-(len(fragment)-len(fragment.rstrip()))
        scopes.append({'context_id':'paragraph:'+str(len(scopes)),'start':trimmed_left,'end':trimmed_right,
                       'speaker_person_refs':[]})
    return scopes


def quoted_at(text, offset, start):
    prefix = text[start:offset]
    # Treat common single-quoted speech conservatively while ignoring word-internal apostrophes.
    cleaned=re.sub(r"(?<=\w)['\u2019](?=\w)",'',prefix)
    return (cleaned.count('"') % 2 == 1 or cleaned.count("'") % 2 == 1
            or cleaned.count('\u201c') != cleaned.count('\u201d')
            or cleaned.count('\u2018') != cleaned.count('\u2019')
            or cleaned.count('\u00ab') != cleaned.count('\u00bb'))


def annotate_mentions(text, forms, contexts=None, namespace=None):
    """Candidates are observations of unchanged text, not validated identities."""
    if not isinstance(text, str):
        raise ValueError('TEXT_REQUIRED')
    if len({form['name_form_id'] for form in forms}) != len(forms):
        raise ValueError('DUPLICATE_NAME_FORM_ID')
    scopes = paragraph_scopes(text) if contexts is None else contexts
    namespace = namespace or 'synthetic-or-unscoped:' + sha(text.encode())
    people = {form['entity_ref'] for form in forms if form['entity_kind'] == 'PERSON'}
    previous = 0
    for scope in scopes:
        if (type(scope['start']) is not int or type(scope['end']) is not int
                or not previous <= scope['start'] < scope['end'] <= len(text)):
            raise ValueError('NONOVERLAPPING_CONTEXT_RANGES_REQUIRED')
        previous = scope['end']
        if (set(scope.get('speaker_person_refs', [])) - people
                or (scope.get('speaker_person_refs') and not scope.get('speaker_evidence_refs'))):
            raise ValueError('SOURCE_BOUND_KNOWN_SPEAKER_REQUIRED')
    scopes=[{**scope,'input_context_id':scope['context_id'],
             'context_id':'horisma:context:'+sha(encoded([namespace,scope['context_id'],scope['start'],scope['end']]))}
            for scope in scopes]
    form_by_id = {form['name_form_id']: form for form in forms}
    matches = {}
    for form in forms:
        if form.get('linkable') is False or form['form_kind'] == 'RELATED_CONCEPT_AS_REPORTED':
            continue
        for match in re.finditer(surface_pattern(form['literal_form']), text, re.I):
            matches.setdefault((match.start(), match.end()), []).append(form['name_form_id'])
    spans = []
    for (start, end), refs in sorted(matches.items(), key=lambda item: (-(item[0][1] - item[0][0]), item[0][0])):
        if any(start < right and end > left for left, right, _ in spans):
            continue
        spans.append((start, end, refs))
    spans.sort()
    rows = []
    for start, end, refs in spans:
        selected = [form_by_id[ref] for ref in refs]
        kinds = {form['entity_kind'] for form in selected}
        candidates = sorted({form['entity_ref'] for form in selected})
        basis = 'EXACT_ATTESTED_FORM'
        short = all(form['form_kind'] in SHORT_FORMS for form in selected)
        # A near-match before a known surname is only a corruption/unlisted-name hypothesis.
        if short and all(form['form_kind'] == 'FAMILY_ONLY' for form in selected):
            preceding = re.search(r"[^\W\d_][\w'’\-]+\s+$", text[:start])
            if preceding:
                token = preceding.group().strip()
                if token[:1].isupper() and token.casefold() not in {'the', 'this', 'that', 'dr', 'professor', 'and', 'by'}:
                    longer = text[preceding.start():end]
                    near = [form for form in forms if form['entity_ref'] in candidates
                            and form['form_kind'] not in SHORT_FORMS
                            and form['entity_kind'] == 'PERSON'
                            and SequenceMatcher(None, longer.casefold(), form['literal_form'].casefold()).ratio() >= .82]
                    if near:
                        start = preceding.start(); refs = sorted({form['name_form_id'] for form in near})
                        basis = 'CORRUPTION_HYPOTHESIS'; short = False
        scope = next((scope for scope in scopes if scope['start'] <= start and end <= scope['end']), None)
        row = {'literal_text': text[start:end], 'character_span': [start, end],
               'candidate_person_refs': candidates if kinds == {'PERSON'} else [],
               'candidate_entity_refs': candidates, 'candidate_name_form_refs': sorted(refs),
               'matched_name_form_refs': sorted(refs),
               'entity_kinds': sorted(kinds), 'linking_basis': basis, '_short': short,
               'context_refs': [scope['context_id']] if scope else [],
               'link_state': 'AMBIGUOUS' if len(candidates) > 1 else 'CANDIDATE',
               'identity_qualified': False, 'transcription_accepted': False}
        if 'CONCEPT' in kinds:
            row.update(concept_sense_assessment=None,sense_status='UNASSESSED_LEXICAL_MATCH')
        row['mention_id'] = 'horisma:mention:' + sha(encoded({'namespace': namespace, 'span': [start, end], 'literal': text[start:end]}))
        rows.append(row)
    # Corruption expansion may overlap an earlier short-name observation.
    selected_rows=[]
    for row in sorted(rows,key=lambda row: (-(row['character_span'][1]-row['character_span'][0]),row['character_span'][0])):
        left,right=row['character_span']
        if not any(left<other['character_span'][1] and right>other['character_span'][0] for other in selected_rows):
            selected_rows.append(row)
    rows=sorted(selected_rows,key=lambda row:row['character_span'][0])
    unknown_spans=[]
    for match in re.finditer(r'(?<!\w)[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}(?!\w)',text):
        if not any(match.start()<row['character_span'][1] and match.end()>row['character_span'][0] for row in rows):
            unknown_spans.append({'literal_text':match.group(),'character_span':[match.start(),match.end()],
                                  'status':'UNCLASSIFIED_CAPITALIZED_SPAN_NOT_ASSERTED_PERSON'})
    for row in rows:
        if not row.pop('_short'):
            row['revision'] = sha(encoded(row))
            continue
        anchors = {entity for other in rows
                   if other is not row and other['context_refs'] == row['context_refs'] and row['context_refs']
                   and other['linking_basis'] == 'EXACT_ATTESTED_FORM'
                   and any(form_by_id[ref]['form_kind'] not in SHORT_FORMS for ref in other['candidate_name_form_refs'])
                   for entity in other['candidate_entity_refs']}
        narrowed = sorted(set(row['candidate_entity_refs']) & anchors)
        row['linking_basis'] = 'CONTEXTUAL_SHORT_FORM'
        if narrowed:
            row['candidate_entity_refs'] = narrowed
            row['candidate_person_refs'] = narrowed if row['entity_kinds'] == ['PERSON'] else []
            row['candidate_name_form_refs']=[ref for ref in row['candidate_name_form_refs'] if form_by_id[ref]['entity_ref'] in narrowed]
            row['link_state'] = 'CANDIDATE' if len(narrowed) == 1 else 'AMBIGUOUS'
        else:
            row['link_state'] = 'AMBIGUOUS' if len(row['candidate_entity_refs']) > 1 else 'ABSTAINED'
            row['reason'] = 'NO_UNIQUE_FULL_FORM_ANCHOR_IN_CONTEXT'
        row['revision'] = sha(encoded(row))
    coreferences = []
    for match in PRONOUNS.finditer(text):
        start, end = match.span()
        if any(start < row['character_span'][1] and end > row['character_span'][0] for row in rows):
            continue
        scope = next((scope for scope in scopes if scope['start'] <= start and end <= scope['end']), None)
        speakers = scope.get('speaker_person_refs', []) if scope else []
        quoted = quoted_at(text, start, scope['start']) if scope else True
        antecedents = []
        if match.group().casefold() in FIRST_PERSON:
            allowed_speakers = speakers if not quoted or (scope and scope.get('quote_speaker_owned') is True) else []
            candidates = sorted(set(allowed_speakers)); basis = 'EXPLICIT_SPEAKER_SCOPE' if allowed_speakers else 'SPEAKER_UNESTABLISHED'
        elif scope and not quoted:
            antecedents = [row for row in rows if row['candidate_person_refs'] and row['link_state'] in {'CANDIDATE', 'AMBIGUOUS', 'ABSTAINED'}
                           and row['character_span'][1] <= start and row['context_refs'] == [scope['context_id']]]
            candidates = sorted({entity for row in antecedents for entity in row['candidate_person_refs']})
            basis = 'UNIQUE_PRIOR_PERSON_IN_CONTEXT_NOT_GENDER_INFERENCE'
        else:
            candidates = []; basis = 'QUOTE_OR_CONTEXT_SCOPE_UNESTABLISHED'
        state = 'CANDIDATE' if len(candidates) == 1 else ('AMBIGUOUS' if candidates else 'ABSTAINED')
        unresolved=[span for span in unknown_spans if scope and scope['start']<=span['character_span'][0]
                    and span['character_span'][1]<=start]
        if unresolved and match.group().casefold() not in FIRST_PERSON:
            state='ABSTAINED';basis='UNCATALOGUED_SPAN_PREVENTS_UNIQUENESS'
        row = {'literal_text': text[start:end], 'character_span': [start, end],
               'candidate_person_refs': candidates, 'antecedent_mention_refs': [row['mention_id'] for row in antecedents],
               'context_refs': [scope['context_id']] if scope else [], 'linking_basis': basis,
               'unresolved_antecedent_spans':unresolved,
               'link_state': state, 'identity_qualified': False, 'transcription_accepted': False}
        row['coreference_id'] = 'horisma:coreference:' + sha(encoded({'namespace': namespace, 'span': [start, end], 'literal': text[start:end]}))
        row['revision'] = sha(encoded(row))
        coreferences.append(row)
    return {'text_sha256': sha(text.encode()), 'mentions': rows, 'coreferences': coreferences,
            'contexts':scopes,
            'unclassified_capitalized_spans':unknown_spans,
            'original_text_unchanged': True, 'qualified_links_produced': False,
            'coreference_scope': 'ENGLISH_CONSERVATIVE_CANDIDATE_RULES', 'scientific_acceptance': False}
