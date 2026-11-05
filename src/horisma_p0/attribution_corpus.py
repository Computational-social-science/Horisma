"""Locatable attribution windows, not automated historical or omission labels."""
import re
from .operators import digest


def statement_window(text, anchor, *, page_index, source_sha256, radius=400):
    if not isinstance(anchor, str) or not anchor.strip() or type(radius) is not int or radius < 0:
        raise ValueError('INVALID_ANCHOR_OR_RADIUS')
    if type(page_index) is not int or page_index < 0:
        raise ValueError('INVALID_PAGE')
    normalized = re.sub(r'\s+', ' ', text).strip()
    matches = list(re.finditer('(?=' + re.escape(anchor) + ')', normalized))
    if len(matches) != 1:
        raise ValueError('UNIQUE_ANCHOR_REQUIRED')
    m = matches[0]
    anchor_end = m.start() + len(anchor)
    start, end = max(0, m.start()-radius), min(len(normalized), anchor_end+radius)
    return {'pdf_page_index': page_index, 'source_sha256': source_sha256,
            'normalized_page_sha256': digest(normalized.encode()),
            'start': start, 'end': end, 'text': normalized[start:end],
            'offset_unit': 'UNICODE_CODEPOINT_NORMALIZED_WHITESPACE',
            'anchor_start': m.start(), 'anchor_end': anchor_end,
            'contribution_assessment': None, 'omission_assessment': None,
            'workflow_status': 'ABSTAINED_PENDING_QUALIFIED_RECEIPTS'}
