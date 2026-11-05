"""Export a private local ledger view; this is not a public redaction boundary."""
import argparse
from html import escape
import json
from pathlib import Path
import sys
import base64
import pymupdf
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from horisma_p0.live_ledger import Ledger, encoded
from horisma_p0.operators import digest, save_new_json
from horisma_p0.operators import owned_path
from horisma_p0.temporal import validate_event


def comparison_drawer(payload):
    data = payload.get('source_comparison')
    if not data:
        return '<small>No bound passage in this record.</small>'
    try:
        if not isinstance(data,dict) or any(not isinstance(data.get(k),str) for k in ['source_path','source_sha256','text_sha256','extracted_text','locator']):
            raise ValueError('TYPED_COMPARISON_FIELDS_REQUIRED')
        source = owned_path(ROOT,data['source_path'])
        raw = source.read_bytes()
        if digest(raw) != data['source_sha256'] or digest(data['extracted_text'].encode()) != data['text_sha256']:
            raise ValueError('SOURCE_OR_PASSAGE_CHANGED')
        excerpt=' '.join(data['extracted_text'].split()[:45])
        return '<details><summary>Source quotation and locator</summary><p>'+escape(data['locator'])+'</p><blockquote>'+escape(excerpt)+'</blockquote><p>Shortened bounded context; not a license determination or qualified transcription. Page images withheld by current IP policy.</p></details>'
    except (KeyError,ValueError,OSError,TypeError):
        return '<strong>Source/passsage binding unavailable or changed; comparison withheld.</strong>'


def html_view(view):
    h = lambda value: escape(str(value))
    rows = view['table']
    tracks = {'SOURCE_PUBLICATION':[], 'PLANNED_EVENT':[], 'OCCURRENCE_CLAIM':[], 'SYSTEM_REVISION':[]}
    for key,row in sorted(rows.items()):
        event = row['payload'].get('historical_event')
        if event:
            event = validate_event(event)
            interval = event.get('interval',{})
            label = event.get('recorded_at') if event['track']=='SYSTEM_REVISION' else (('Unknown · '+str(interval.get('missing_reason'))) if interval.get('precision')=='UNKNOWN' else (interval.get('value') or (str(interval.get('earliest'))+' … '+str(interval.get('latest')))))
            bounds = ('<br><small>Date uncertainty: '+h(interval.get('earliest'))+' … '+h(interval.get('latest'))+'</small>') if interval.get('precision') in {'MONTH','YEAR','INTERVAL'} else ''
            sort_key = datetime.fromisoformat(event['recorded_at']).astimezone(timezone.utc).isoformat() if event['track']=='SYSTEM_REVISION' else interval.get('earliest') or '9999'
            tracks[event['track']].append((sort_key, '<li><strong>'+h(label)+'</strong><br>'+h(key)+'<br><small>'+h(event['event_type'])+' · '+h(event.get('verification',''))+'</small><br>Precision: '+h(interval.get('precision'))+bounds+'</li>'))
    snapshot_time = view.get('recorded_at_utc')
    sort_key = datetime.fromisoformat(snapshot_time).astimezone(timezone.utc).isoformat() if snapshot_time else '9999'
    tracks['SYSTEM_REVISION'].append((sort_key, '<li><strong>'+h(snapshot_time)+'</strong><br>Snapshot recorded (UTC)<br><small>Not a historical event date.</small></li>'))
    titles = {'SOURCE_PUBLICATION':'Source publication', 'PLANNED_EVENT':'Planned presentations', 'OCCURRENCE_CLAIM':'Occurrence claims · not verified', 'SYSTEM_REVISION':'System revisions'}
    events = '<div class="tracks">'+''.join('<div><h3>'+titles[key]+'</h3><ol>'+(''.join(item[1] for item in sorted(items)) or '<li>No eligible record.</li>')+'</ol></div>' for key,items in tracks.items())+'</div>'
    table = ''.join('<tr><td>'+h(key)+'</td><td>'+h(row['payload'].get('label',key))+comparison_drawer(row['payload'])+'</td><td>'+h('; '.join(k+': '+v for k,v in row['effective_facets'].items()))+'</td><td>'+h('; '.join(reason['facet']+' ← '+reason['dependency']+': '+reason['reason'] for reason in row['reasons']) or '—')+'</td></tr>' for key,row in sorted(rows.items()))
    changes = ''.join(f'<li>{h(change["entity_id"])} · {h(change["change"])}</li>' for change in view['diff']) or '<li>No changes in this comparison.</li>'
    edges = ''.join(f'<li>{h(e["from"])} → {h(e["to"])}<br><small>requires {h(e["requires_facet"])}; affects {h(e["affects_facet"])}</small></li>' for e in view['focus_edges']) or '<li>No dependencies in the selected scope.</li>'
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Horisma evidence revision</title>
<style>body{{font:16px/1.55 system-ui,sans-serif;background:#f5f5f0;color:#22313b;margin:0}}main{{max-width:1300px;margin:auto;padding:32px}}h1{{font-size:28px}}a{{color:#176481}}.badge{{background:#e9ddb9;padding:6px 12px;border-radius:4px}}.tracks{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px}}.source-image{{max-width:100%;height:auto}}details{{margin-top:10px}}summary{{cursor:pointer;color:#176481}}blockquote{{margin:10px 0;padding-left:12px;border-left:2px solid #a0b5b8}}.cols{{display:grid;grid-template-columns:1fr 1fr;gap:28px}}section{{min-width:0;overflow-wrap:anywhere;background:white;padding:22px;border:1px solid #d7dcd9;margin-top:22px;border-radius:8px}}li{{margin-bottom:15px}}ol{{border-left:2px solid #779396;padding-left:26px;list-style:none}}small{{color:#576771}}code{{overflow-wrap:anywhere}}table{{border-collapse:collapse;table-layout:fixed;width:100%;min-width:760px;font-size:14px}}th:nth-child(1){{width:16%}}th:nth-child(2){{width:44%}}th:nth-child(3),th:nth-child(4){{width:20%}}th,td{{text-align:left;vertical-align:top;border-bottom:1px solid #ddd;padding:10px;overflow-wrap:anywhere}}.scroll{{overflow:auto;max-width:100%}}nav{{display:flex;flex-wrap:wrap;gap:10px 18px}}nav a{{margin:0}}@media(max-width:760px){{.cols,.tracks{{grid-template-columns:1fr}}main{{padding:16px}}}}</style>
<main><h1>Horisma / evidence revision</h1><p class="badge">Private local snapshot · unqualified metadata · not scientific approval</p><p>Snapshot <code>{h(view['snapshot'])}</code></p><p>Recorded (UTC): {h(view.get('recorded_at_utc'))}. Comparison: <code>{h(view.get('previous_snapshot') or 'empty baseline')}</code></p><nav><a href="#timeline">Chronology</a><a href="#ledger">Ledger</a><a href="#focus">Dependencies</a><a href="#changes">Changes</a><a href="view.json">Machine view</a></nav>
<section id="timeline"><h2>Parallel chronology tracks</h2><p>Each track is ordered independently; positions are not a shared proportional time axis. Month/year bounds preserve uncertainty, not exact days. Occurrence claims are not verified occurrence.</p>{events}</section><section id="focus"><h2>Focused dependency graph</h2><p>Dependency adjacency view from this same snapshot. Arrows express declared facet dependencies, not causal proof.</p><p>{h(', '.join(view['focus_nodes']))}</p><ul>{edges}</ul></section>
<section id="ledger"><h2>Evidence ledger</h2><div class="scroll"><table><thead><tr><th>Entity</th><th>Label</th><th>Effective facets</th><th>Invalidation reasons</th></tr></thead><tbody>{table}</tbody></table></div></section><section id="changes"><h2>Revision changes</h2><ul>{changes}</ul></section><p>Generated on demand. This page does not poll, invoke models or update itself. Re-export after ledger changes; keep this snapshot for reproducibility.</p></main></html>'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot')
    parser.add_argument('--previous')
    parser.add_argument('--focus')
    args = parser.parse_args()
    ledger = Ledger(ROOT)
    view = ledger.view(args.snapshot, previous=args.previous, focus=args.focus)
    body = html_view(view).encode('utf-8')
    manifest = {'renderer_sha256':digest(Path(__file__).read_bytes()), 'view':view,
                'pymupdf_version':pymupdf.VersionBind, 'html_sha256':digest(body)}
    output = ROOT/'outputs/live-evidence'/digest(encoded(manifest))
    output.mkdir(parents=True,exist_ok=True)
    save_new_json(output/'view.json',view)
    save_new_json(output/'manifest.json',manifest)
    page = output/'index.html'
    if page.exists():
        if page.read_bytes() != body:
            raise ValueError('IMMUTABLE_VIEW_CHANGED')
    else:
        with page.open('xb') as stream:
            stream.write(body)
    print(page)
