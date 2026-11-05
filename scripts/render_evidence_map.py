"""Render a typed, metadata-only evidence map to reproducible SVG (no network)."""
import json
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]


def validate_map(graph):
    ids = [node['id'] for node in graph['nodes']]
    if len(ids) != len(set(ids)):
        raise ValueError('DUPLICATE_NODE')
    for edge in graph['edges']:
        if edge['from'] not in ids or edge['to'] not in ids:
            raise ValueError('DANGLING_EDGE')
        if edge['relation'] not in {'REPORTS', 'REFERENCES', 'LIMITS', 'PREMISE', 'PROPOSES', 'HYPOTHESIZES'}:
            raise ValueError('UNTYPED_RELATION')
        if edge['semantic_status'] != 'PROPOSED':
            raise ValueError('THIS_MAP_HAS_NO_QUALIFIED_SEMANTIC_EDGES')
    for node in graph['nodes']:
        if node['kind'] == 'AND_INFERENCE':
            incoming = {e['from'] for e in graph['edges'] if e['to'] == node['id'] and e['relation'] == 'PREMISE'}
            if len(incoming) < 2 or incoming != set(node['requires']):
                raise ValueError('INCOMPLETE_AND_PREMISES')
    dependencies = {i: [] for i in ids}
    for edge in graph['edges']:
        if edge['relation'] == 'PREMISE':
            dependencies[edge['from']].append(edge['to'])
    active, done = set(), set()
    def visit(node_id):
        if node_id in active:
            raise ValueError('CIRCULAR_PREMISE_DEPENDENCY')
        if node_id in done:
            return
        active.add(node_id)
        for target in dependencies[node_id]:
            visit(target)
        active.remove(node_id)
        done.add(node_id)
    for node_id in ids:
        visit(node_id)


def render(graph):
    validate_map(graph)
    palette = {'SOURCE': '#dbe8ef', 'CLAIM': '#f5e8c8', 'AND_INFERENCE': '#dcebe1',
               'HYPOTHESIS': '#eadff1', 'OUTCOME': '#e8e8e8'}
    positions = {n['id']: (45 + n['lane']*430, 180 + n['row']*155) for n in graph['nodes']}
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="1340" height="1300" viewBox="0 0 1340 1300" role="img" aria-labelledby="title desc">',
         '<title id="title">Horisma: typed evidence and contribution map</title>',
         '<desc id="desc">Metadata-only proposal map. All semantic edges are unqualified. Sources, claims, shared premises, hypotheses and abstentions are distinct.</desc>',
         '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#53616b"/></marker></defs>',
         '<rect width="1340" height="1300" fill="#fafaf7"/>',
         '<g font-family="Arial, sans-serif" fill="#24323b">',
         '<text x="45" y="46" font-size="25">HORISMA / Evidence, roles and inference</text>',
         '<text x="45" y="78" font-size="14">Local working map · semantic proposals only · no accepted miscredit or causal finding</text>',
         '<text x="45" y="108" font-size="13">Solid: reporting/reference/premise · dashed: limitation/proposal · dotted: mechanism hypothesis</text>']
    for x, label in [(45,'1 / Source records'),(475,'2 / Role-scoped synthesis'),(905,'3 / Revisions and open mechanisms')]:
        s.append(f'<text x="{x}" y="150" font-size="17">{label}</text>')
    for edge in graph['edges']:
        x,y = positions[edge['from']]; a,b = positions[edge['to']]
        x += 340; y += 48; b += 48
        dash = '2 6' if edge['relation']=='HYPOTHESIZES' else ('7 4' if edge['relation'] in {'LIMITS','PROPOSES'} else '')
        # Explicit segment geometry preserves line types in SVG-to-raster engines.
        def point(t):
            return ((1-t)**3*x + 3*(1-t)**2*t*(x+40) + 3*(1-t)*t*t*(a-40) + t**3*a,
                    (1-t)**3*y + 3*(1-t)**2*t*y + 3*(1-t)*t*t*b + t**3*b)
        for j in range(40):
            if dash and j % (4 if edge['relation']=='HYPOTHESIZES' else 6) >= (1 if edge['relation']=='HYPOTHESIZES' else 4):
                continue
            px,py = point(j/40); qx,qy = point((j+1)/40)
            s.append(f'<path d="M{px},{py} L{qx},{qy}" stroke="#53616b" stroke-width="1.4"/>')
        s.append(f'<polygon points="{a},{b} {a-8},{b-4} {a-8},{b+4}" fill="#53616b"/>')
        lx,ly = point(.5)
        s.append(f'<text x="{lx}" y="{ly-8}" text-anchor="middle" font-size="9">{escape(edge["relation"])}</text>')
    for node in graph['nodes']:
        x,y = positions[node['id']]
        s.append(f'<g><title>{escape(node["detail"])}</title><rect x="{x}" y="{y}" width="340" height="108" rx="7" fill="{palette[node["kind"]]}" stroke="#9ba8ad"/>')
        s.append(f'<text x="{x+14}" y="{y+22}" font-size="11">{escape(node["id"]+" / "+node["kind"])}</text>')
        for i,line in enumerate(node['lines']):
            s.append(f'<text x="{x+14}" y="{y+47+i*19}" font-size="14">{escape(line)}</text>')
        s.append('</g>')
    s.extend(['<text x="45" y="1180" font-size="13">AND nodes require every listed premise. Shared AAAS source cluster is not independent corroboration.</text>',
              '<text x="45" y="1205" font-size="13">File binding ≠ semantic acceptance. Citation ≠ reading/reliance. Absence in a window ≠ document omission.</text>',
              '<text x="45" y="1230" font-size="13">Hover nodes/edges for scope. Definitions and revision table: EVIDENCE_GRAPH_FRAMEWORK_EN.md.</text>', '</g></svg>'])
    return '\n'.join(s)


if __name__ == '__main__':
    graph = json.loads((ROOT/'spec/examples/matthew_evidence_map.json').read_text(encoding='utf-8'))
    output = ROOT/'docs/assets/matthew-evidence-map.svg'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(graph), encoding='utf-8')
    print(output)
