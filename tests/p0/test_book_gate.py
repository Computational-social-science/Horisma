import copy
import hashlib
import pytest
from horisma_p0.book_gate import development_export_metadata
from horisma_p0.book_gate import check_book


def sample(tmp_path):
    text = '# Chapter\n\nA bounded source reading. [1]\n\n## Sources\n\n1. Source'
    (tmp_path/'source').write_bytes(b'original')
    h = lambda b: hashlib.sha256(b).hexdigest()
    mapping = {'content_sha256': h(text.encode()), 'paragraphs': [
        {'id':'P01','text_sha256':h(b'A bounded source reading. [1]'),'sources':['1']}],
        'sources':{'1':{'path':'source','sha256':h(b'original'),'locator':'p1'}}}
    return text, mapping


def test_preview_never_authorizes_release(tmp_path):
    text,mapping=sample(tmp_path)
    result=check_book(tmp_path,text,mapping,mode='preview')
    assert result['release_authorized'] is False
    assert result['scientific_acceptance'] is False
    mapping['release_authorized']=True
    with pytest.raises(ValueError,match='BOOK_RELEASE_BLOCKED'):
        check_book(tmp_path,text,mapping,mode='release')


def test_export_medium_cannot_grant_release():
    for medium in ['html','story-html','scroll-html','pdf-epub']:
        meta=development_export_metadata(medium)
        assert not meta['release_authorized'] and not meta['scientific_acceptance']
        assert meta['series_title']=='The Secrets of Terms'
        assert meta['book_title']=='The Secrets of Terms'
        assert meta['subtitle']=='The Matthew Effect'


@pytest.mark.parametrize('mutation', ['text','source','paragraph','citation','missing'])
def test_stale_or_incomplete_bindings_block_preview(tmp_path,mutation):
    text,mapping=sample(tmp_path); mapping=copy.deepcopy(mapping)
    if mutation=='text':text+=' change'
    if mutation=='source':(tmp_path/'source').write_bytes(b'changed')
    if mutation=='paragraph':mapping['paragraphs'][0]['text_sha256']='stale'
    if mutation=='citation':mapping['paragraphs'][0]['sources']=[]
    if mutation=='missing':mapping['paragraphs']=[]
    with pytest.raises(ValueError):check_book(tmp_path,text,mapping,mode='preview')
