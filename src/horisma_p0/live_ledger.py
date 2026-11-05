"""Local immutable revisions and facet-specific effective-state projections."""
import json
import os
import re
import uuid
from datetime import datetime, timezone
from .operators import owned_path, digest, load_json
from .temporal import validate_event


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode('utf-8')


class Ledger:
    def __init__(self, root, relative='data/evidence/live-ledger-v1'):
        self.path = owned_path(root, relative)
        self.path.mkdir(parents=True, exist_ok=True)

    def _atomic(self, path, value):
        temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
        try:
            with temp.open('xb') as stream:
                stream.write(encoded(value))
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
        finally:
            temp.unlink(missing_ok=True)

    def _put(self, value):
        revision = digest(encoded(value))
        path = self.path / (revision + '.json')
        if path.exists():
            self._get(revision)
        else:
            self._atomic(path, value)
        return revision

    def _get(self, revision):
        if not isinstance(revision, str) or not re.fullmatch('[a-f0-9]{64}', revision):
            raise ValueError('INVALID_REVISION')
        value = load_json(self.path / (revision + '.json'))
        if digest(encoded(value)) != revision:
            raise ValueError('REVISION_INTEGRITY_FAILURE')
        return value

    def head(self):
        path = self.path / 'HEAD.json'
        return load_json(path)['snapshot'] if path.exists() else None

    def commit(self, entity_id, payload, facets, dependencies=()):
        if not isinstance(dependencies, (list, tuple)):
            raise ValueError('DEPENDENCIES_MUST_BE_MATERIALIZED')
        if not isinstance(entity_id, str) or not entity_id.strip() or not facets:
            raise ValueError('ENTITY_AND_FACETS_REQUIRED')
        if not isinstance(payload, dict) or not isinstance(facets, dict) or any(v not in {'SATISFIED', 'PENDING', 'REJECTED'} for v in facets.values()):
            raise ValueError('INVALID_ENTITY_PAYLOAD')
        if any(not isinstance(key, str) or not key.strip() for key in facets):
            raise ValueError('STRING_FACET_NAMES_REQUIRED')
        if 'historical_event' in payload:
            validate_event(payload['historical_event'])
        lock = self.path / 'writer.lock'
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        try:
            os.close(fd)
            previous = self.head()
            heads = dict(self._get(previous)['heads']) if previous else {}
            for dep in dependencies:
                if not isinstance(dep, dict) or set(dep) != {'entity_id','revision','requires_facet','affects_facet'}:
                    raise ValueError('INVALID_DEPENDENCY')
                if any(not isinstance(value, str) or not value.strip() for value in dep.values()) or dep['affects_facet'] not in facets:
                    raise ValueError('INVALID_DEPENDENCY')
                if heads.get(dep['entity_id']) != dep['revision']:
                    raise ValueError('DEPENDENCY_NOT_CURRENT')
                if dep['requires_facet'] not in self._get(dep['revision'])['facets']:
                    raise ValueError('DEPENDENCY_FACET_MISSING')
            record = {'entity_id': entity_id, 'payload': payload, 'facets': facets,
                      'dependencies': list(dependencies), 'previous_revision': heads.get(entity_id)}
            revision = self._put(record)
            heads[entity_id] = revision
            snapshot = self._put({'heads': heads, 'previous_snapshot': previous,
                                  'recorded_at_utc': datetime.now(timezone.utc).isoformat()})
            self.project(snapshot)  # Reject circular dependencies before publishing HEAD.
            self._atomic(self.path/'HEAD.json', {'snapshot': snapshot})
            return snapshot
        finally:
            lock.unlink(missing_ok=True)

    def project(self, snapshot=None):
        snapshot = snapshot or self.head()
        if snapshot is None:
            return {'snapshot': None, 'entities': {}, 'semantic_qualification': False}
        snapshot_record = self._get(snapshot)
        heads = snapshot_record['heads']
        effective, active = {}, set()
        def resolve(entity_id):
            if entity_id in active:
                raise ValueError('CIRCULAR_ACCEPTANCE_DEPENDENCY')
            if entity_id in effective:
                return effective[entity_id]
            active.add(entity_id)
            record = self._get(heads[entity_id])
            result = {'revision': heads[entity_id], 'payload': record['payload'],
                      'declared_facets': record['facets'], 'effective_facets': dict(record['facets']),
                      'dependencies': record['dependencies'], 'reasons': []}
            for dep in record['dependencies']:
                parent = resolve(dep['entity_id'])
                changed = heads[dep['entity_id']] != dep['revision']
                state = parent['effective_facets'].get(dep['requires_facet'])
                if changed or state != 'SATISFIED':
                    facet = dep['affects_facet']
                    if result['effective_facets'][facet] == 'SATISFIED':
                        result['effective_facets'][facet] = 'STALE'
                    result['reasons'].append({'facet':facet,'dependency':dep['entity_id'],
                        'reason':'REVISION_CHANGED' if changed else 'REQUIRED_FACET_NOT_SATISFIED'})
            active.remove(entity_id)
            effective[entity_id] = result
            return result
        for entity_id in sorted(heads):
            resolve(entity_id)
        return {'snapshot':snapshot, 'recorded_at_utc':snapshot_record['recorded_at_utc'],
                'entities':effective, 'semantic_qualification':False}

    def view(self, snapshot=None, previous=None, focus=None):
        current = self.project(snapshot)
        before = self.project(previous)['entities'] if previous else {}
        rows = current['entities']
        diff = [{'entity_id': key, 'change': 'ADDED' if key not in before else 'CHANGED'}
                for key in sorted(rows) if key not in before or rows[key] != before[key]]
        selected = set(rows) if focus is None else {focus}
        pending = list(selected)
        while pending:
            key = pending.pop()
            for dep in rows[key]['dependencies']:
                if dep['entity_id'] not in selected:
                    selected.add(dep['entity_id']); pending.append(dep['entity_id'])
        return {'snapshot':current['snapshot'], 'recorded_at_utc':current.get('recorded_at_utc'),
                'previous_snapshot':previous, 'table':rows, 'diff':diff,
                'focus_nodes':sorted(selected), 'focus_edges':[
                    {'from':d['entity_id'], 'to':key, 'requires_facet':d['requires_facet'], 'affects_facet':d['affects_facet']}
                    for key in sorted(selected) for d in rows[key]['dependencies']],
                'scientific_acceptance':False}
