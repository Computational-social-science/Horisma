"""Prune only proven Git-reproducible technical exports; never research evidence."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile

from .research_slice import encoded, sha, read


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root)


def blob_id(body):
    return hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()


def export_inventory(path):
    """No links or unknown cache artifacts; fingerprint includes disposable test files."""
    files, tree = {}, {}
    total = 0
    if path.is_dir():
        for item in path.rglob('*'):
            if item.is_symlink() or getattr(item, 'is_junction', lambda: False)():
                raise ValueError('EXPORT_LINK_REJECTED')
            if item.is_file():
                name = item.relative_to(path).as_posix(); body = item.read_bytes()
                files[name] = sha(body); total += len(body)
                if name.startswith('.pytest_cache/') or ('/__pycache__/' in '/'+name and name.endswith('.pyc')):
                    continue
                tree[name] = blob_id(body)
    else:
        with tarfile.open(path) as archive:
            for member in archive:
                if member.isdir(): continue
                if not member.isfile() or member.name in files: raise ValueError('EXPORT_ARCHIVE_MEMBER_REJECTED')
                stream = archive.extractfile(member)
                if stream is None: raise ValueError('EXPORT_ARCHIVE_MEMBER_MISSING')
                body = stream.read(); files[member.name] = sha(body); total += len(body)
                tree[member.name] = blob_id(body)
    return {'fingerprint': sha(encoded(files)), 'tree': tree, 'sha256_files': files, 'files': len(files), 'bytes': total}


def run_roots(root):
    return [root/'outputs/full-document-ocr', *[root/'outputs/fidelity-campaigns'/name
            for name in ['docling', 'paddleocr', 'mineru']]]


def proof_matches(manifest, inventory):
    # Reject links anywhere in the retained proof chain, including its ancestors.
    if manifest.resolve() != manifest.absolute(): return False
    if manifest.is_symlink() or getattr(manifest, 'is_junction', lambda: False)(): return False
    raw = manifest.read_bytes()
    if sha(raw) != manifest.parent.name: return False
    declared = json.loads(raw)['files']
    if declared != inventory['sha256_files']: return False
    for name, digest in declared.items():
        item = manifest.parent/name
        if (Path(name).name != name or item.resolve() != item.absolute() or item.is_symlink()
                or getattr(item, 'is_junction', lambda: False)() or sha(item.read_bytes()) != digest): return False
    return True


def sealed_duplicate_runs(root):
    import yaml
    protected = yaml.safe_load((root/'.eidos/project.yaml').read_text(encoding='utf-8')).get('validity_inputs', []) if (root/'.eidos/project.yaml').exists() else []
    active = (root/'ops/state/research-model-screen.lock').exists()
    candidates, retained = [], []
    for directory in run_roots(root):
        boundary = directory/'runs'
        if boundary.exists() and boundary.resolve() != boundary.absolute():
            raise ValueError('RUN_CACHE_BOUNDARY_IS_LINK')
        for run in (directory/'runs').glob('*'):
            relative = run.relative_to(root).as_posix()
            if active or any(p == relative or p.startswith(relative+'/') for p in protected):
                retained.append({'path': relative, 'reason': 'ACTIVE_OR_DECLARED_INPUT'}); continue
            if not run.is_dir() or run.is_symlink() or getattr(run, 'is_junction', lambda: False)() or not run.resolve().is_relative_to((directory/'runs').resolve()):
                retained.append({'path': relative, 'reason': 'UNSAFE_RUN_PATH'}); continue
            inventory = export_inventory(run)
            match = None
            for manifest in (directory/'attempts').glob('*/manifest.json'):
                if not proof_matches(manifest, inventory): continue
                match = manifest; break
            if match is None:
                retained.append({'path': relative, 'reason': 'NO_BYTE_IDENTICAL_SEALED_ATTEMPT'}); continue
            candidates.append({'path': relative, 'kind': 'SEALED_RUN_DUPLICATE',
                'proof_manifest': match.relative_to(root).as_posix(), 'fingerprint': inventory['fingerprint'],
                'files': inventory['files'], 'bytes': inventory['bytes']})
    return candidates, retained


def cleanup_plan(root):
    root = Path(root).resolve(); base = root/'.rebuild/public-checkpoint'
    if base.exists() and base.resolve() != base.absolute(): raise ValueError('EXPORT_CACHE_BOUNDARY_IS_LINK')
    head = git(root, 'rev-parse', 'HEAD').decode().strip()
    commits = git(root, 'rev-list', '--max-count=20', 'HEAD').decode().splitlines()
    trees = {}
    for commit in commits:
        entries = git(root, 'ls-tree', '-r', '-z', commit).split(b'\0')
        tree = {}
        for entry in filter(None, entries):
            meta, name = entry.split(b'\t', 1); tree[name.decode()] = meta.split()[2].decode()
        trees[commit] = tree
    protected = set()
    # These pointers identify retained clean-test exports, not disposable caches.
    for pointer in base.glob('*path.txt'):
        value = Path(pointer.read_text(encoding='utf-8').strip()).resolve()
        protected.add(value)
    candidates, retained = [], []
    if not base.exists(): return {'head': head, 'candidates': [], 'retained': []}
    for path in base.iterdir():
        if not re.fullmatch(r'(?:checkout|fidelity-export|reading-export|ocr-export)-[a-zA-Z0-9]+|(?:fidelity|reading|ocr)-export\.tar', path.name):
            continue
        resolved = path.resolve()
        if not resolved.is_relative_to(base.resolve()) or path.is_symlink() or getattr(path, 'is_junction', lambda: False)():
            raise ValueError('EXPORT_OUTSIDE_CACHE_BOUNDARY')
        if resolved in protected:
            retained.append({'path': path.relative_to(root).as_posix(), 'reason': 'CURRENT_EXPORT_POINTER'}); continue
        try:
            inventory = export_inventory(path)
            commit = next((c for c, tree in trees.items() if inventory['tree'] == tree), None)
            if not commit:
                retained.append({'path': path.relative_to(root).as_posix(), 'reason': 'NO_EXACT_COMMITTED_TREE'}); continue
            candidates.append({'path': path.relative_to(root).as_posix(), 'rebuild_commit': commit,
                'kind': 'GIT_EXPORT',
                'fingerprint': inventory['fingerprint'], 'files': inventory['files'],
                'bytes': path.stat().st_size if path.is_file() else inventory['bytes']})
        except (ValueError, OSError, tarfile.TarError) as exc:
            retained.append({'path': path.relative_to(root).as_posix(), 'reason': str(exc)})
    duplicates, run_retained = sealed_duplicate_runs(root)
    return {'head': head, 'candidates': sorted(candidates+duplicates, key=lambda row: row['path']),
            'retained': retained+run_retained, 'scope': 'PROVEN_DUPLICATE_CACHES_NO_UNIQUE_RESEARCH_RECORDS'}


def apply_cleanup(root, plan):
    root = Path(root).resolve(); base = (root/'.rebuild/public-checkpoint').resolve()
    if git(root, 'rev-parse', 'HEAD').decode().strip() != plan['head']: raise ValueError('CLEANUP_HEAD_CHANGED')
    current = {row['path']: row for row in cleanup_plan(root)['candidates']}
    for row in plan['candidates']:
        if current.get(row['path']) != row: raise ValueError('CLEANUP_INPUT_CHANGED')
    removed, freed = [], 0
    for row in plan['candidates']:
        path = (root/row['path']).resolve()
        permitted = path.is_relative_to(base) and path != base
        if row.get('kind') == 'SEALED_RUN_DUPLICATE':
            permitted = any(path.is_relative_to(folder/'runs') and path != folder/'runs' for folder in run_roots(root))
            if (root/'ops/state/research-model-screen.lock').exists(): raise ValueError('INFERENCE_BECAME_ACTIVE')
        if not permitted: raise ValueError('CLEANUP_BOUNDARY_REJECTED')
        if export_inventory(path)['fingerprint'] != row['fingerprint']: raise ValueError('CLEANUP_CONTENT_CHANGED')
        if row.get('kind') == 'SEALED_RUN_DUPLICATE' and not proof_matches(root/row['proof_manifest'], export_inventory(path)):
            raise ValueError('CLEANUP_PROOF_CHANGED')
        if path.is_dir(): shutil.rmtree(path)
        else: path.unlink()
        removed.append(row['path']); freed += row['bytes']
    return {'removed': removed, 'freed_bytes': freed, 'scope': plan['scope'], 'plan_sha256': sha(encoded(plan))}


def current_documents(root):
    import yaml
    root = Path(root).resolve()
    catalog = yaml.safe_load(read(root, 'spec/extensions/document_authority.yaml'))
    for entry in catalog['current_entries']:
        if not (root/entry['path']).is_file() or not (root/entry['path']).resolve().is_relative_to(root):
            raise ValueError('INVALID_DOCUMENT_AUTHORITY_ENTRY')
    return catalog
