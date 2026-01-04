"""CI helper: validate templates in the repository.

This script iterates over packaged and user templates roots and for each template:
- runs `Engine.validate_template()` to detect syntax errors and undefined variables
- if a `bldrx-manifest.json` exists, runs `Engine.verify_template()` and reports issues

Exit code is non-zero if any issues are found.
"""
import sys
from pathlib import Path
import sys
import os
# Ensure workspace root is importable when running this script directly (CI also installs package)
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
from bldrx.engine import Engine


def main():
    engine = Engine()
    errors = []
    warnings = []
    # check both package and user templates roots
    roots = [engine.package_templates_root, engine.user_templates_root]
    checked = set()
    strict = (os.getenv('BLDRX_VALIDATE_FAIL_ON_UNDEFINED') == '1')
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
                if res.get('syntax_errors'):
                    errors.append((name, 'syntax', res['syntax_errors']))
                undef = {p:v for p,v in (res.get('undefined_variables') or {}).items() if v}
                if undef:
                    if strict:
                        errors.append((name, 'undefined_variables', undef))
                    else:
                        warnings.append((name, 'undefined_variables', undef))
                # if manifest exists, verify
                vres = engine.verify_template(name, templates_dir=root)
                if not vres.get('ok'):
                    errors.append((name, 'manifest', vres))
            except Exception as e:
                errors.append((name, 'exception', str(e)))
    if errors:
        print('Template validation failures detected:')
        for p in errors:
            name, typ, details = p
            print(f"- {name}: {typ}: {details}")
        # print warnings as well if present
        if warnings:
            print('\nWarnings:')
            for p in warnings:
                name, typ, details = p
                print(f"- {name}: {typ}: {details}")
        sys.exit(2)
    if warnings:
        print('Template validation generated warnings:')
        for p in warnings:
            name, typ, details = p
            print(f"- {name}: {typ}: {details}")
        print('\nAll templates validated with warnings.')
        return 0
    print('All templates validated successfully.')
    return 0


if __name__ == '__main__':
    sys.exit(main())