# Changelog

All notable changes to this project are documented in this file.

## 2026-01-04 — Summary of implemented features & fixes

- Added comprehensive templates:
  - `python-cli`, `node-api`, `react-app`, `ci`, `docker`, `lint`, `github` (including `.github/ISSUE_TEMPLATE` and `funding.yml`).
- Implemented CLI features:
  - `new`, `add-templates`, `list-templates` (with `--details` and `--json`), `remove-template` (with `--yes`, `--force`, `--dry-run`),
  - `install-template` (interactive install into user templates), `uninstall-template`, and `preview-template` (raw and rendered preview with `--meta`).
- Added user templates support:
  - Default user templates dir (`~/.bldrx/templates` or `%APPDATA%\bldrx\templates`) and `BLDRX_TEMPLATES_DIR` env override.
  - `--templates-dir` option to point a single command at a custom templates root.
- Improved engine behavior:
  - Safe write/skip/force/dry-run statuses, template search order (override → user → package), and template file rendering helpers.
- Documentation & tests:
  - Split docs into `README.md` (user docs) and `PROJECT_OUTLINE.md` (design/roadmap); added `BUILD_INSTRUCTIONS.md` and `CHANGELOG.md`.
  - Added tests for engine, CLI, templates, user templates, preview, docs and packaging; all tests passing locally.
- Packaging & CI:
  - Ensure templates included in package via `MANIFEST.in` and `pyproject.toml` package-data.
  - Built and validated wheel locally.
  - Added GitHub Actions workflow to run tests on push/PR and fixed artifact uploads.
  - Fix applied: make artifact names unique per job/run and add `build-artifacts` job to build and upload distributions on tag pushes.
- Added `--wrap` option to `install-template` to allow preserving the source top-level folder when installing templates (useful for `.github` directories); default installs contents-only.

---

(End of changelog entry.)
