"""CI helper: validate templates in the repository.

This script iterates over packaged and user templates roots and for each template:
- runs `Engine.validate_template()` to detect syntax errors and undefined variables
- if a `bldrx-manifest.json` exists, runs `Engine.verify_template()` and reports issues

Exit code is non-zero if any issues are found.
"""
import sys
from pathlib import Path
from bldrx.engine import Engine


def main():
    engine = Engine()
    problems = []
    # check both package and user templates roots
    roots = [engine.package_templates_root, engine.user_templates_root]
    checked = set()
    for root in roots:
        if not root.exists():
            continue
        for tpl in root.iterdir():
            if not tpl.is_dir():
                continue
            name = tpl.name
            if name in checked:
                continue
            checked.add(name)
            try:
                res = engine.validate_template(name, templates_dir=root)
                if res['syntax_errors'] or any(v for v in res.get('undefined_variables', {}).values() if v):
                    problems.append((name, 'validation', res))
                # if manifest exists, verify
                vres = engine.verify_template(name, templates_dir=root)
                if not vres.get('ok'):
                    problems.append((name, 'manifest', vres))
            except Exception as e:
                problems.append((name, 'exception', str(e)))
    if problems:
        print('Template validation failures detected:')
        for p in problems:
            name, typ, details = p
            print(f"- {name}: {typ}: {details}")
        sys.exit(2)
    print('All templates validated successfully.')
    return 0


if __name__ == '__main__':
    sys.exit(main())