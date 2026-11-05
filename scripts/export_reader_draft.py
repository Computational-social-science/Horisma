"""Render the authored reader draft; no OCR or internal receipts enter this view."""
from pathlib import Path
from html import escape
import hashlib
import re
import argparse
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from horisma_p0.book_gate import check_book, development_export_metadata


def render(text):
    def linked(value):
        value=escape(value)
        value=re.sub(r'\[(\d+(?:,\s*\d+)*)\]',lambda m:' '.join('<a class="citation" href="#source-'+n.strip()+'">['+n.strip()+']</a>' for n in m[1].split(',')),value)
        return re.sub(r'\[(\d+),\s*(p{1,2}\.[^\]]+)\]',lambda m:'<a class="citation" href="#source-'+m[1]+'">['+m[1]+', '+m[2]+']</a>',value)
    blocks=[]
    for paragraph in re.split(r'\n\s*\n',text.strip()):
        if paragraph.startswith('# '):
            blocks.append('<h1>'+escape(paragraph[2:])+'</h1>')
        elif paragraph.startswith('## '):
            blocks.append('<h2>'+escape(paragraph[3:])+'</h2>')
        else:
            if re.match(r'^\d+\. ',paragraph):
                for line in paragraph.splitlines():
                    m=re.match(r'^(\d+)\. ',line)
                    blocks.append('<p id="source-'+m[1]+'">'+escape(line)+'</p>' if m else '<p>'+escape(line)+'</p>')
            else:blocks.append('<p>'+linked(paragraph).replace('\n','<br>')+'</p>')
    body='\n'.join(blocks)
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The Matthew Effect — Credit Where Credit Is Due</title><style>body{background:#f5f2e9;color:#24352d;margin:0;font:19px/1.85 Georgia,serif}header{font:11px Arial;letter-spacing:3px;border-bottom:1px solid #d6dbcc;padding:25px 7%;display:flex;justify-content:space-between}main{max-width:760px;padding:45px 30px 100px;margin:auto}h1{font:normal clamp(45px,7vw,78px)/1.05 Georgia;letter-spacing:-2px;margin:20px 0 70px}h2{font:normal 34px/1.25 Georgia;margin:75px 0 25px}p{margin:0 0 1.3em}header span{letter-spacing:1px;color:#68776c}@media(max-width:600px){body{font-size:18px}main{padding:25px 23px 60px}h2{font-size:29px}}@media print{body{background:white;font-size:11pt}main{padding:0}h2{break-before:page}p{widows:3;orphans:3}}</style><body><header>HORISMA <span>READER DRAFT / 0.1</span></header><main>'''+body+'</main></body></html>'


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['preview','release'], default='preview')
    args=parser.parse_args()
    source=ROOT/'docs/research/book/MATTHEW_CHAPTER_ONE_EN.md'
    text=source.read_text(encoding='utf-8')
    mapping_path=ROOT/'spec/examples/matthew_chapter_one_map.json'
    mapping=json.loads(mapping_path.read_text(encoding='utf-8'))
    gate=check_book(ROOT,text,mapping,mode=args.mode)
    gate.update(development_export_metadata('html'))
    html=render(text)
    html=html.replace('<main>','<main><p role="note"><strong>UNREVIEWED DEVELOPMENT DRAFT</strong> — evidence review and publication authorization remain incomplete.</p>',1)
    output=ROOT/'outputs/reader-preview'/hashlib.sha256(html.encode()).hexdigest()
    output.mkdir(parents=True,exist_ok=True);path=output/'index.html'
    path.write_text(html,encoding='utf-8');print(path)
    gate['html_sha256']=hashlib.sha256(html.encode()).hexdigest()
    gate['builder_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    gate['mapping_sha256']=hashlib.sha256(mapping_path.read_bytes()).hexdigest()
    (output/'manifest.json').write_text(json.dumps(gate,indent=2),encoding='utf-8')
