"""Standalone private scrollytelling ebook using the bound story and shared master."""
from pathlib import Path
import json
import runpy
import sys
from html import escape

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from horisma_p0.live_ledger import Ledger,encoded
from horisma_p0.operators import digest,save_new_json
from horisma_p0.publication_master import make_master
from horisma_p0.claim_edges import validate_claim_edge,edge_markup
from horisma_p0.edge_review import review_edge


if __name__=='__main__':
    ns=runpy.run_path(str(ROOT/'scripts/export_story_timeline.py'))
    guide=json.loads((ROOT/'spec/examples/matthew_story_guide.json').read_text(encoding='utf-8'))
    view=Ledger(ROOT).view()
    story=ns['build_story'](ROOT,view,guide)
    claim_texts=['The1964 preview describes a Merton paper based on Zuckerman interviews.','The programme schedules a Merton presentation on the Matthew effect.','The1968 paper displays Merton as its author.','Merton retrospectively acknowledges joint-authorship entitlement for the original paper.','Perc reports that Merton coined the term Matthew effect.','Brainard reports joint coining by Merton and Zuckerman in1968.']
    claim_texts=dict(zip(['HAC1-001','HAC1-002','HAC1-003','HAC1-005','HAC1-006','HAC1-007'],claim_texts))
    edges=[];reviews=[]
    for i,c in enumerate(story['chapters']):
        record=view['table'][c['record_id']];comparison=record['payload']['source_comparison'];text=claim_texts[c['record_id']]
        edge={'id':'HCE-'+c['record_id'],'relation':'REPORTS','claim':{'id':'HC-'+c['record_id'],'text':text,'sha256':digest(text.encode())},'source':{'id':c['source_id'],'revision':c['source_revision'],'sha256':c['source_sha256']},'passage':{'record_id':c['record_id'],'record_revision':c['record_revision'],'text':comparison['extracted_text'],'sha256':comparison['text_sha256'],'locator':c['locator']},'rationale':'Proposed source-reporting interpretation from the bounded passage; not independently established historical truth.','limitations':[c['distinction'],c['open_question']],'qualification':{'status':'UNQUALIFIED','reason':'Source identity, fidelity and qualified semantic review remain incomplete.','policy':'horisma-auto-review-0.1.0'}}
        validate_claim_edge(edge,view);edges.append(edge);reviews.append(review_edge(ROOT,edge,view))
    story['paths']={'all':[c['record_id'] for c in story['chapters']],
                    'credit':['HAC1-001','HAC1-003','HAC1-005','HAC1-007'],
                    'dates':['HAC1-001','HAC1-002','HAC1-006','HAC1-007']}
    bibliography=json.loads((ROOT/'spec/examples/matthew_bibliography.json').read_text(encoding='utf-8'))
    master=make_master(story,bibliography)
    sections=[]
    for i,c in enumerate(master['chapters']):
        h=escape
        chapter=story['chapters'][i]
        evidence_link='<details class="argument"><summary>Inspect assertion → source → limits</summary><p><strong>Assertion under review</strong></p><p>'+h(c['body'])+'</p><p><strong>Bound source</strong></p><p>'+h(chapter['source_label'])+' · '+h(chapter['locator'])+'</p><p class="caption">Source SHA256: '+h(chapter['source_sha256'])+'</p><p><strong>Limiting condition</strong></p><p>'+h(c['distinction'])+'</p><p><strong>Unresolved dependency</strong></p><p>'+h(c['open_question'])+'</p><p class="caption">Relations are proposed, not qualified entailment. Bibliographic linkage does not prove reading or causality.</p><button class="inspect-source" data-record="'+h(c['record_id'])+'">Show this source and transcription</button></details>'
        sections.append(f'<section class="chapter" id="{h(c["chapter_id"])}" data-record="{h(c["record_id"])}" data-index="{i}"><p class="eyebrow">CHAPTER {i+1:02} / {h(c["date"])}</p><h2>{h(c["heading"])}</h2><p>{h(c["body"])} <a class="noteref" href="#{h(c["citation_id"])}">[{h(c["citation_id"])}]</a></p>{evidence_link}{edge_markup(edges[i])}<p class="caption">Receipt review: {h(reviews[i]["workflow_status"])} / {h(reviews[i]["reason"])}</p><h3>THE DISTINCTION</h3><p class="distinction">{h(c["distinction"])}</p><details><summary>Manuscript implication & open question</summary><p>{h(c["revision"])}</p><p>{h(c["open_question"])}</p></details><p class="caption">Provisional interpretation · evidence {h(c["evidence_id"])}</p></section>')
    refs=[]
    for item in bibliography['entries'].values():
        text='; '.join(item['authors'])+'. ' if item['authors'] else ''
        text+=item['title']+'. '+item['container_title']+' '+str(item['volume'] or '')+(', '+item['pages'] if item['pages'] else '')+' ('+item['date']+').'
        refs.append('<li id="'+escape(item['citation_id'])+'">'+escape(text)+' <small>Metadata provisional.</small></li>')
    ui=ROOT/'src/horisma_p0/story_ui'
    template=(ui/'scroll.html').read_text(encoding='utf-8')
    for key,value in [('__CHAPTERS__',''.join(sections)),('__BIBLIOGRAPHY__','<ol>'+''.join(refs)+'</ol>')]:
        template=template.replace(key,value,1)
    style=(ui/'scroll.css').read_text(encoding='utf-8');script=(ui/'scroll.js').read_text(encoding='utf-8')
    html=ns['render'](story,template,style,script)
    from horisma_p0.book_gate import development_export_metadata
    manifest={**development_export_metadata('scroll-html'),'snapshot':story['snapshot'],'master_sha256':digest(encoded(master)),
              'edge_reviews_sha256':digest(encoded(reviews)),'claim_edges_sha256':digest(encoded(edges)),
              'builder_sha256':digest(Path(__file__).read_bytes()),'html_sha256':digest(html.encode()),
              'release_authorized':False,'three_dimensional_asset':None}
    out=ROOT/'outputs/scroll-ebook'/digest(encoded(manifest));out.mkdir(parents=True,exist_ok=True)
    save_new_json(out/'edge-reviews.json',reviews);save_new_json(out/'claim-edges.json',edges);save_new_json(out/'content-master.json',master);save_new_json(out/'manifest.json',manifest)
    path=out/'index.html'
    if path.exists():
        if path.read_text(encoding='utf-8')!=html:raise ValueError('IMMUTABLE_EBOOK_CHANGED')
    else:path.write_text(html,encoding='utf-8')
    print(path)
