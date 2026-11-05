"""Build a standalone private JavaScript story from bound ledger records."""
import base64
from datetime import date
import json
from pathlib import Path
import sys
import re
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from horisma_p0.live_ledger import Ledger, encoded
from horisma_p0.operators import owned_path, digest, save_new_json
from horisma_p0.temporal import validate_event


def unique_anchor(text, anchor):
    return bool(anchor) and len(list(re.finditer('(?='+re.escape(anchor.casefold())+')',text.casefold())))==1


def quote_excerpt(text,anchor,max_words=45):
    words=list(re.finditer(r'\S+',text))
    if not words:return ''
    match=re.search(re.escape(anchor),text,re.IGNORECASE) if anchor else None
    found=match.start() if match else -1
    start=next((i for i,w in enumerate(words) if w.start()<=found<w.end()),0)
    end=min(len(words),start+max_words)
    return ('… ' if start else '')+text[words[start].start():words[end-1].end()]+(' …' if end<len(words) else '')


def build_story(root, view, guide):
    chapters = []
    for entry in guide['chapters']:
        record = view['table'][entry['record_id']]
        source = view['table'][entry['source_id']]
        if entry['source_id'] not in {d['entity_id'] for d in record['dependencies']}:
            raise ValueError('STORY_SOURCE_NOT_A_DECLARED_DEPENDENCY')
        for dependency in record['dependencies']:
            parent=view['table'][dependency['entity_id']]
            if dependency['revision'] != parent['revision']:
                raise ValueError('STORY_DEPENDENCY_REVISION_STALE')
        if any(state=='STALE' for row in [record,source] for state in row['effective_facets'].values()):
            raise ValueError('STORY_EFFECTIVE_STATE_STALE')
        comparison = record['payload']['source_comparison']
        raw = owned_path(root,comparison['source_path']).read_bytes()
        if digest(raw) != comparison['source_sha256'] or source['payload']['source_sha256'] != comparison['source_sha256']:
            raise ValueError('STORY_SOURCE_CHANGED')
        transcript = comparison['extracted_text']
        if not isinstance(transcript,str) or digest(transcript.encode()) != comparison['text_sha256']:
            raise ValueError('STORY_TRANSCRIPT_CHANGED')
        with pymupdf.open(stream=raw,filetype='pdf') as doc:
            index = comparison['pdf_page_index']
            if type(index) is not int or not 0 <= index < len(doc):
                raise ValueError('STORY_PAGE_INVALID')
            page=doc[index]
            if page.rect.width*page.rect.height*1.44 > 3000000:
                raise ValueError('STORY_RASTER_BUDGET_EXCEEDED')
            png=b''  # Current IP policy: no embedded page facsimiles.
            anchor=entry.get('highlight_anchor','')
            normalized=re.sub(r'\s+',' ',page.get_text()).strip()
            boxes=page.search_for(anchor) if unique_anchor(normalized,anchor) else []
            # Retain source-region coordinates without distributing page images.
            marked=b''
        event=validate_event(source['payload']['historical_event'])
        interval=event['interval']
        label=date.fromisoformat(interval['value']).strftime('%d %b %Y') if interval['precision']=='DAY' else interval['value'] or 'Date unresolved'
        chapters.append({**entry,'date':label,'source_event':event,
            'image':'',
            'located_image':'',
            'locator_status':'BOUND_EDITORIAL_LOCATOR' if boxes else 'UNRESOLVED_LOCATOR',
            'locator_boxes':[list(box) for box in boxes],
            'transcript':quote_excerpt(transcript,entry.get('highlight_anchor','')),'quote_policy':'Bound context excerpt; shortened to at most45words, not a license determination','full_passage_sha256':comparison['text_sha256'],'locator':comparison['locator'],
            'connections':[d['entity_id']+' → '+entry['record_id']+' · '+d['requires_facet']+' / '+d['affects_facet'] for d in record['dependencies']],
            'source_revision':source['revision'],'record_revision':record['revision'],
            'source_sha256':comparison['source_sha256'],'image_sha256':digest(png)})
    return {'snapshot':view['snapshot'],'recorded_at_utc':view['recorded_at_utc'],
            'guide_version':guide['version'],'chapters':chapters,'scientific_acceptance':False}


def render(story, template, style, script):
    data=json.dumps(story,ensure_ascii=False).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    for marker in ['__STYLE__','__DATA__','__SCRIPT__']:
        if template.count(marker) != 1:
            raise ValueError('UNIQUE_TEMPLATE_MARKERS_REQUIRED')
    return template.replace('__STYLE__',style,1).replace('__SCRIPT__',script,1).replace('__DATA__',data,1)


def story_changes(story, previous=None):
    old={c['record_id']:c for c in previous['chapters']} if previous else {}
    for chapter in story['chapters']:
        prior=old.get(chapter['record_id'])
        fields=['heading','body','distinction','revision','source_label','short','date','open_question',
                'transcript','locator','connections','source_event','source_sha256','image_sha256',
                'source_revision','record_revision','highlight_anchor','locator_status','locator_boxes']
        changes=[{'field':key,'before':prior.get(key),'after':chapter.get(key)} for key in fields if prior and prior.get(key)!=chapter.get(key)]
        chapter['edition_changes']=changes
        chapter['changes_text']='\n\n'.join(c['field']+':\nBefore: '+str(c['before'])+'\nNow: '+str(c['after']) for c in changes) if changes else ('No compared fields changed.' if prior else 'No matching prior chapter selected.')
    story['compared_snapshot']=previous.get('snapshot') if previous else None


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--previous-story');args=parser.parse_args()
    view=Ledger(ROOT).view()
    guide=json.loads((ROOT/'spec/examples/matthew_story_guide.json').read_text(encoding='utf-8'))
    story=build_story(ROOT,view,guide)
    previous=json.loads(owned_path(ROOT,args.previous_story).read_text(encoding='utf-8')) if args.previous_story else None
    story_changes(story,previous)
    ui=ROOT/'src/horisma_p0/story_ui'
    template,style,script=[(ui/name).read_text(encoding='utf-8') for name in ['index.html','style.css','story.js']]
    html=render(story,template,style,script)
    from horisma_p0.book_gate import development_export_metadata
    manifest={**development_export_metadata('story-html'),'snapshot':view['snapshot'],'guide_sha256':digest(encoded(guide)),
              'builder_sha256':digest(Path(__file__).read_bytes()),'pymupdf_version':pymupdf.VersionBind,
              'html_sha256':digest(html.encode()),'semantic_status':'PROVISIONAL'}
    output=ROOT/'outputs/story-timeline'/digest(encoded(manifest));output.mkdir(parents=True,exist_ok=True)
    save_new_json(output/'story.json',story);save_new_json(output/'manifest.json',manifest)
    path=output/'index.html'
    if path.exists():
        if path.read_text(encoding='utf-8') != html:
            raise ValueError('IMMUTABLE_STORY_CHANGED')
    else:
        path.write_text(html,encoding='utf-8')
    print(path)
