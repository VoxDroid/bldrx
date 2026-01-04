import os
from pathlib import Path
from datetime import datetime
import pytest
from bldrx.engine import Engine

SNAPSHOT_DIR = Path(__file__).parent / 'snapshots'
SAMPLE_METADATA = {
    'project_name': 'demo',
    'author_name': 'VoxDroid',
    'email': 'izeno.contact@gmail.com',
    'github_username': 'VoxDroid'
}

# List of (template_name, jinja_relative_path) tuples to snapshot
TARGETS = [
    ('python-cli', 'README.md.j2'),
    ('python-cli', 'src_main.py.j2'),
    ('github', 'CONTRIBUTING.md.j2'),
]


def _snapshot_path(template, rel_path):
    # normalize rel_path to filesystem-safe path
    out_dir = SNAPSHOT_DIR / template
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = rel_path.replace('/', '__')
    return out_dir / (safe + '.snap')


@pytest.mark.parametrize('template,rel_path', TARGETS)
def test_template_snapshot(template, rel_path):
    engine = Engine()
    # render template
    rendered = engine.render_template_file(template, rel_path, {**SAMPLE_METADATA, 'year': datetime.now().year})
    snap = _snapshot_path(template, rel_path)
    update = os.getenv('BLDRX_UPDATE_SNAPSHOTS')
    if not snap.exists():
        if update:
            snap.write_text(rendered, encoding='utf-8')
            pytest.skip(f"Snapshot for {template}/{rel_path} created; rerun tests")
        else:
            pytest.fail(f"Missing snapshot for {template}/{rel_path}. Set BLDRX_UPDATE_SNAPSHOTS=1 to create.")
    expected = snap.read_text(encoding='utf-8')
    if expected != rendered:
        if update:
            snap.write_text(rendered, encoding='utf-8')
            pytest.skip(f"Snapshot for {template}/{rel_path} updated; rerun tests")
        else:
            # show unified diff
            import difflib
            diff = '\n'.join(list(difflib.unified_diff(expected.splitlines(), rendered.splitlines(), fromfile=str(snap), tofile='(rendered)', lineterm='')))
            pytest.fail(f"Snapshot mismatch for {template}/{rel_path}:\n{diff}")
