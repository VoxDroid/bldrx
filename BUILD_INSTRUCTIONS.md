# Build & Setup Instructions

This document describes how to set up a development environment, run tests, build packages, and verify the `bldrx` templates are included in packaged artifacts.

## Quick Summary
- Run tests: `python -m pytest -q`
- Build package: `python -m build` (creates `dist/` artifacts)
- Install built wheel: `pip install dist/*.whl` and verify `bldrx --help` or `bldrx list-templates`

---

## Prerequisites
- Python 3.9, 3.10, or 3.11 (CI uses 3.9–3.11)
- Git
- Recommended: a virtual environment for development

## 1) Create & activate a virtual environment
- Windows (PowerShell)
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- macOS / Linux
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```

## 2) Install runtime & dev dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
# For building artifacts
pip install build twine
```

## 3) Run tests locally
```bash
python -m pytest -q
# Or run a specific test
python -m pytest tests/test_templates.py::test_apply_docker_and_prettier_templates -q
```

## 4) CLI smoke tests
```bash
# List templates
bldrx list-templates
# Dry-run scaffold
bldrx new demo_project --type python-cli --dry-run
# Add templates to existing dir (dry-run)
bldrx add-templates demo_project --templates github,ci --dry-run
# Include a license using the convenience flag
bldrx new demo_project --type python-cli --license MIT --meta author_name="VoxDroid" --meta year=2026 --dry-run
bldrx add-templates demo_project --license Apache-2.0 --meta author_name="VoxDroid" --meta year=2026 --dry-run
```

## User templates examples

```bash
# Install a local template into your user templates
bldrx install-template ~/my-templates/cool-template --name cool

# List available templates (user templates are marked)
bldrx list-templates

# Override for a single command
bldrx list-templates --templates-dir ~/other-templates

# Use env var to point to a custom user templates dir
export BLDRX_TEMPLATES_DIR="$HOME/.config/my-bldrx/templates"
bldrx list-templates
```

PowerShell example:

```powershell
$env:BLDRX_TEMPLATES_DIR = "$env:APPDATA\bldrx\templates"
bldrx list-templates
```
## 5) Build a source distribution and wheel
```bash
python -m build
# artifacts will be in dist/
ls dist/
```

## 6) Install from the built wheel (verify installed package)
```bash
pip install dist/*.whl
# Run the installed CLI
bldrx --help
bldrx list-templates
```

## 7) Verify package includes templates
- After installing from wheel, run:
```bash
python -c "import bldrx; from pathlib import Path; print(Path(bldrx.__file__).parent / 'templates')"
# Or just run `bldrx list-templates` and ensure templates are shown
```

## 8) Publish to PyPI (optional)
1. Ensure your account and `.pypirc` ready (or use API tokens)
2. Build artifacts: `python -m build`
3. Upload with Twine: `python -m twine upload dist/*`

> Note: bump the version in `pyproject.toml` before publishing.

## 9) Continuous Integration
- A GitHub Actions workflow is included at `.github/workflows/ci.yml` to run tests on push/pull-request (matrix: Python 3.9, 3.10, 3.11).

## Troubleshooting
- If `bldrx list-templates` fails after installing the package, ensure package data is included (we include `MANIFEST.in` and package data in `pyproject.toml`).
- Use `pip show -f bldrx` after installing to inspect files included in the package.

## Quick commands reference
- Run tests: `python -m pytest -q`
- Build: `python -m build`
- Install built wheel: `pip install dist/*.whl`
- Run CLI: `bldrx --help` / `bldrx list-templates`

---
