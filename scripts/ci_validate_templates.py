"""CI helper: validate templates in the repository.

This script iterates over packaged and user templates roots and for each template:
- runs `Engine.validate_template()` to detect syntax errors and undefined variables
- if a `bldrx-manifest.json` exists, runs `Engine.verify_template()` and reports issues

Exit code is non-zero if any issues are found.
"""

import os
import sys
from pathlib import Path

# Ensure workspace root is importable when running this script directly (CI also installs package)
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
from bldrx.engine import Engine  # noqa: E402


def main():
    engine = Engine()
    errors = []
    warnings = []
    # check both package and user templates roots
    roots = [engine.package_templates_root, engine.user_templates_root]
    checked = set()
    strict = os.getenv("BLDRX_VALIDATE_FAIL_ON_UNDEFINED") == "1"
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
                if res.get("syntax_errors"):
                    errors.append((name, "syntax", res["syntax_errors"]))
                undef = {
                    p: v for p, v in (res.get("undefined_variables") or {}).items() if v
                }
                if undef:
                    # If a per-template CI metadata file exists (ci_metadata.json), try rendering
                    # templates with that metadata to resolve undefined vars used only at render time.
                    md_path = tpl / "ci_metadata.json"
                    if md_path.exists():
                        try:
                            import json

                            metadata = json.loads(md_path.read_text(encoding="utf-8"))
                        except Exception:
                            metadata = {}
                        render_ok = True
                        for rel_path in undef.keys():
                            try:
                                # engine.render_template_file will raise if a variable is still undefined
                                engine.render_template_file(
                                    name, rel_path, metadata, templates_dir=root
                                )
                            except Exception:
                                render_ok = False
                                break
                        if render_ok:
                            # metadata satisfied all undefined variables for this template
                            undef = {}
                    if undef:
                        if strict:
                            errors.append((name, "undefined_variables", undef))
                        else:
                            warnings.append((name, "undefined_variables", undef))
                # if manifest exists, verify
                vres = engine.verify_template(name, templates_dir=root)
                if not vres.get("ok"):
                    errors.append((name, "manifest", vres))

                # warn if README or LICENSE files are missing (recommendation)
                existing_files = [p.name for p in tpl.rglob("*") if p.is_file()]
                lower_files = [f.lower() for f in existing_files]
                has_readme = any(
                    f in lower_files for f in ("readme.md", "readme.md.j2")
                )
                has_license = any(
                    f.startswith("license")
                    or f.startswith("copying")
                    or f.startswith("unlicense")
                    for f in lower_files
                )
                if not has_readme:
                    warnings.append(
                        (name, "missing_readme", "No README.md or README.md.j2 found")
                    )
                if not has_license:
                    warnings.append(
                        (
                            name,
                            "missing_license",
                            "No LICENSE/COPYING/UNLICENSE file found",
                        )
                    )
            except Exception as e:
                errors.append((name, "exception", str(e)))
    if errors:
        print("Template validation failures detected:")
        for p in errors:
            name, typ, details = p
            print(f"- {name}: {typ}: {details}")
        # print warnings as well if present
        if warnings:
            print("\nWarnings:")
            for p in warnings:
                name, typ, details = p
                print(f"- {name}: {typ}: {details}")
        sys.exit(2)
    if warnings:
        print("Template validation generated warnings:")
        for p in warnings:
            name, typ, details = p
            print(f"- {name}: {typ}: {details}")
        print("\nAll templates validated with warnings.")
        return 0
    print("All templates validated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
