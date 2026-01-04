from pathlib import Path
from datetime import datetime
from bldrx.engine import Engine

engine = Engine()
SAMPLE_METADATA = {'project_name':'demo','author_name':'Alice','email':'alice@example.com','github_username':'alice'}
targets = [('python-cli','README.md.j2'),('python-cli','src_main.py.j2'),('github','CONTRIBUTING.md.j2')]
for tpl,rel in targets:
    out_dir = Path('tests/snapshots')/tpl
    out_dir.mkdir(parents=True,exist_ok=True)
    rendered = engine.render_template_file(tpl, rel, {**SAMPLE_METADATA, 'year': datetime.now().year})
    safe = rel.replace('/','__')
    p = out_dir/(safe+'.snap')
    p.write_text(rendered, encoding='utf-8')
    print('WROTE', p)
