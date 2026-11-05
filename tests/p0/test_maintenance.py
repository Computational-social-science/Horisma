import json
from pathlib import Path
import shutil
import subprocess

import pytest

from horisma_p0.maintenance import cleanup_plan, apply_cleanup
from horisma_p0.probe_artifacts import seal_attempt


def repository(root):
    subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
    (root/'README.md').write_text('Technical synthetic fixture.\n')
    subprocess.run(['git', 'add', 'README.md'], cwd=root, check=True)
    subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                    '-c', 'commit.gpgsign=false', 'commit', '-qm', 'fixture'], cwd=root, check=True)


def test_only_exact_git_export_is_removed_and_pointer_retained(tmp_path):
    repository(tmp_path)
    base = tmp_path/'.rebuild/public-checkpoint'; base.mkdir(parents=True)
    for name in ['reading-export-old', 'reading-export-current', 'reading-export-unique']:
        folder = base/name; folder.mkdir()
        (folder/'README.md').write_bytes(subprocess.check_output(['git', 'show', 'HEAD:README.md'], cwd=tmp_path))
    (base/'reading-export-unique/research.txt').write_text('Unique data must survive.')
    (base/'current-path.txt').write_text(str(base/'reading-export-current'))
    plan = cleanup_plan(tmp_path)
    assert [Path(row['path']).name for row in plan['candidates']] == ['reading-export-old']
    result = apply_cleanup(tmp_path, plan)
    assert result['freed_bytes'] > 0 and not (base/'reading-export-old').exists()
    assert (base/'reading-export-current').exists() and (base/'reading-export-unique/research.txt').exists()


def test_sealed_duplicate_only_and_active_or_changed_run_survives(tmp_path):
    repository(tmp_path)
    (tmp_path/'.rebuild/public-checkpoint').mkdir(parents=True)
    folder = tmp_path/'outputs/full-document-ocr'; run = folder/'runs/example'; run.mkdir(parents=True)
    (run/'process.json').write_bytes(b'{"status":"DONE"}')
    seal_attempt(folder, 'recipe', {'process.json': (run/'process.json').read_bytes()})
    plan = cleanup_plan(tmp_path); assert len(plan['candidates']) == 1
    lock = tmp_path/'ops/state/research-model-screen.lock'; lock.parent.mkdir(parents=True); lock.write_text('foreign')
    with pytest.raises(ValueError): apply_cleanup(tmp_path, plan)
    assert run.exists(); lock.unlink()
    (run/'process.json').write_bytes(b'changed')
    with pytest.raises(ValueError): apply_cleanup(tmp_path, plan)
    assert run.exists()


def test_proof_symlink_back_into_deleted_run_is_not_a_retained_copy(tmp_path):
    repository(tmp_path)
    (tmp_path/'.rebuild/public-checkpoint').mkdir(parents=True)
    folder = tmp_path/'outputs/full-document-ocr'; run = folder/'runs/example'; run.mkdir(parents=True)
    raw = b'unique research evidence'; (run/'raw.json').write_bytes(raw)
    ident = seal_attempt(folder, 'recipe', {'raw.json': raw})
    proof = folder/'attempts'/ident/'raw.json'; proof.unlink()
    try: proof.symlink_to(run/'raw.json')
    except OSError: pytest.skip('Symlink creation unavailable on this host')
    assert not cleanup_plan(tmp_path)['candidates']
    assert (run/'raw.json').exists()
