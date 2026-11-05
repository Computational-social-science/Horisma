import pytest
from horisma_p0.card_publication import anchors, render_views


def card(ident, targets=()):
    return {'card_id':ident,'title':'Synthetic event','proposition':'A reported event.',
            'support_scope':'Synthetic only','limitations':'Not historical gold','revision':'v1',
            'readiness':'UNQUALIFIED_EVIDENCE','evidence_node_refs':['syn:source'],
            'links':[{'card_ref':t,'relation':'EDITORIAL_REFERENCE'} for t in targets]}


def test_anchor_identity_survives_card_revision_and_backlinks_are_editorial():
    cards = [card('syn:a',['syn:b']),card('syn:b')]
    qmd, logseq, mapping = render_views(cards)
    cards[0]['revision'] = 'v2'
    assert render_views(cards)[2] == mapping
    assert qmd.count('[^'+anchors('syn:a')['footnote']+']:') == 1
    assert 'Referenced by: @'+anchors('syn:a')['quarto'] in qmd
    assert '(('+anchors('syn:b')['logseq_uuid']+'))' in logseq
    assert 'Original-source citations remain separate.' in qmd
    assert 'title: "The Secrets of Terms"' in qmd
    assert 'subtitle: "The Matthew Effect"' in qmd
    assert logseq.startswith('- The Secrets of Terms: The Matthew Effect')


def test_unknown_link_cannot_be_exported_as_a_broken_book_reference():
    with pytest.raises(ValueError, match='DANGLING'): render_views([card('syn:a',['missing'])])
