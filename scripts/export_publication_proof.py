"""Private print/EPUB design proofs from the same story; no facsimile redistribution."""
from pathlib import Path
import json
import sys
from html import escape
import zipfile
import hashlib
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from horisma_p0.publication_master import make_master
from horisma_p0.book_gate import development_export_metadata


def publication(story):
    h=lambda value:escape(str(value))
    chapters=[];notes=[]
    for i,c in enumerate(story['chapters'],1):
        chapter_id='chapter-'+c['record_id'];note_id='evidence-'+c['record_id'];cite_id='cite-'+c['record_id']
        chapters.append(f'<section class="chapter" id="{h(chapter_id)}"><p class="eyebrow">FIELD NOTE {i:02} / {h(c["date"])}</p><h2>{h(c["heading"])}</h2><p>{h(c["body"])} <a id="{h(cite_id)}" href="#{h(note_id)}" epub:type="noteref">[{i}]</a></p><h3>Interpretive distinction</h3><p>{h(c["distinction"])}</p><h3>Manuscript implication</h3><p>{h(c["revision"])}</p><aside><h3>Open question</h3><p>{h(c["open_question"])}</p></aside><p class="caption">Historical interpretation: provisional. Original page images are omitted from this publication proof.</p></section>')
        notes.append(f'<li id="{h(note_id)}" epub:type="footnote"><p>{h(c["source_label"])}. {h(c["locator"])} Source revision: <span class="digest">{h(c["source_sha256"][:16])}</span>. <a href="#{h(cite_id)}" aria-label="Return to citation {i}">Return to [{i}]</a></p></li>')
    cover=f'<section class="cover"><p class="eyebrow">HORISMA / RESEARCH NOTES</p><h1>The Matthew<br/>Effect</h1><p class="subtitle">Tracing the Matthew effect through six source records</p><p>Print and reflowable ebook design proof / 0.1.0</p><p>All historical readings remain provisional. This is not a release-approved book or a certified print-production file.</p><p>Source snapshot <span class="digest">{h(story["snapshot"])}</span><br/>Narrative guide {h(story["guide_version"])}</p></section>'
    return cover+''.join(chapters)+'<section class="notes" id="notes"><h2>Evidence notes</h2><p>Source references are not historical approval. Existing source annotations and image rights are not inherited by this proof.</p><ol>'+''.join(notes)+'</ol></section>'


if __name__=='__main__':
    story_path=max((ROOT/'outputs/story-timeline').glob('*/story.json'),key=lambda p:p.stat().st_mtime)
    story=json.loads(story_path.read_text(encoding='utf-8'))
    bibliography=json.loads((ROOT/'spec/examples/matthew_bibliography.json').read_text(encoding='utf-8'))
    master=make_master(story,bibliography)
    for chapter in story['chapters']:
        entry=bibliography['entries'][chapter['source_id']]
        authors='; '.join(entry['authors'])+'. ' if entry['authors'] else ''
        chapter['source_label']=entry['citation_id']+' / '+authors+entry['title']+'. '+entry['container_title']+' '+str(entry['volume'] or '')+(', '+entry['pages'] if entry['pages'] else '')+' ('+entry['date']+'); metadata provisional'
    content=publication(story)
    generated=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    builder_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    style='body{font:1em/1.6 Georgia,serif;color:#202620;margin:1.4em;max-width:40em}h1{font-size:3.4em;line-height:1.05;font-weight:normal}h2{font-size:2em;line-height:1.12;font-weight:normal}h3{font: bold .8em/1.4 Arial,sans-serif;letter-spacing:.03em;margin-top:1.8em}p{orphans:3;widows:3}.eyebrow,.caption{font:.75em/1.6 Arial,sans-serif}.digest{overflow-wrap:anywhere;font-size:.75em}aside{border-left:1px solid;padding-left:1em}a{color:inherit;text-decoration:underline}.chapter{break-before:page}.notes{break-before:page}.cover{break-after:page}.notes li{break-inside:avoid;margin-bottom:1em}'
    proofstyle='@page{size:156mm 234mm;margin:20mm 19mm 20mm 21mm}body{max-width:none;margin:0;font-size:11pt}h1{margin-top:30mm}h2{margin-top:10mm}a{text-decoration:none}.caption{margin-top:2em}.chapter{page-break-before:always}.notes{page-break-before:always}'
    out=ROOT/'outputs/publication-proof'/hashlib.sha256((story['snapshot']+story['guide_version']+content+style+proofstyle+generated+builder_hash).encode()).hexdigest();out.mkdir(parents=True,exist_ok=False)
    (out/'content-master.json').write_text(json.dumps(master,indent=2,ensure_ascii=False),encoding='utf-8')
    (out/'print.html').write_text('<!doctype html><html lang="en" xmlns:epub="http://www.idpf.org/2007/ops"><meta charset="utf-8"><title>Horisma publication design proof</title><style>'+style+proofstyle+'</style><body>'+content+'</body></html>',encoding='utf-8')
    xhtml='<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en"><head><title>A name, a byline, a record</title><link rel="stylesheet" href="book.css"/></head><body>'+content+'</body></html>'
    nav='<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><head><title>Contents</title></head><body><nav epub:type="toc"><h1>Contents</h1><ol>'+''.join(f'<li><a href="book.xhtml#chapter-{escape(c['record_id'])}">{escape(c["heading"])}</a></li>' for i,c in enumerate(story['chapters'],1))+'<li><a href="book.xhtml#notes">Evidence notes</a></li></ol></nav></body></html>'
    identifier='urn:sha256:'+hashlib.sha256(xhtml.encode()).hexdigest()
    opf=f'<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="id"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="id">{identifier}</dc:identifier><dc:title>The Matthew Effect — development proof</dc:title><dc:language>en</dc:language><meta property="dcterms:modified">{generated}</meta></metadata><manifest><item id="book" href="book.xhtml" media-type="application/xhtml+xml"/><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="css" href="book.css" media-type="text/css"/></manifest><spine><itemref idref="book"/></spine></package>'
    with zipfile.ZipFile(out/'horisma-design-proof.epub','w') as z:
        z.writestr('mimetype','application/epub+zip',compress_type=zipfile.ZIP_STORED)
        for path,data in {'META-INF/container.xml':'<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="EPUB/package.opf" media-type="application/oebps-package+xml"/></rootfiles></container>','EPUB/package.opf':opf,'EPUB/book.xhtml':xhtml,'EPUB/nav.xhtml':nav,'EPUB/book.css':style}.items():z.writestr(path,data,compress_type=zipfile.ZIP_DEFLATED)
    (out/'manifest.json').write_text(json.dumps({**development_export_metadata('pdf-epub'),'story_input':story_path.relative_to(ROOT).as_posix(),'snapshot':story['snapshot'],'guide':story['guide_version'],'generated_at_utc':generated,'builder_sha256':builder_hash,'release_authorized':False,'source_images_included':False,'epubcheck_run':False},indent=2),encoding='utf-8')
    print(out)
