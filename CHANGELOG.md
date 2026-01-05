# Changelog

All notable changes to this project are documented in this file.

## Unreleased — Planned improvements (Top priorities)

- CI: Added a `type-check` job using `mypy` to run static typing checks against the `bldrx` package; follow-up work will add stricter mypy settings and annotate core modules.  

## 2026-01-05 — 0.1.6

- CI:
  - Expanded the test matrix to include **Windows** (`windows-latest`) and **macOS** (`macos-latest`) runners for the `test` and `validate-templates` jobs to improve cross-platform coverage; artifact names were updated to include the OS to avoid upload conflicts.
  - Added a follow-up task to enable static type checking (mypy/pyright), coverage reporting, and security scanning in CI.
- Docs & packaging:
  - Updated `README.md` with PyPI installation instructions (`pip` and `pipx`) and added a PyPI version badge and link to the project metadata.
- Project management:
  - Updated `PROJECT_OUTLINE.md` and TODO list to reflect the CI updates and next steps.

## 2026-01-05 — 0.1.5

- Hidden easter-egg:
  - Added a *hidden* global `--whoami` flag that prints a small developer attribution message ("Developed by VoxDroid — https://github.com/VoxDroid") and exits cleanly. The option is intentionally hidden from `--help` to act as an easter egg. Tests were added to verify behavior (`tests/test_cli_whoami.py`).

## 2026-01-05 — 0.1.4

- CLI & UX improvements:
  - Added `--version` support (`bldrx --version`) and a global `--developer-metadata` flag to inject developer metadata (`bldrx_version`, `dev_timestamp`) into rendered templates for debugging and provenance.
  - Improved `--license` handling: fuzzy matching for license identifiers (e.g., `--license Apache` now resolves to `licenses/Apache-2.0` when appropriate), deterministic resolution when multiple matches are present (first match is chosen with a warning), and clearer errors when no license is found.
  - Added robust error handling around applying templates: unresolved placeholders and missing templates are reported with friendly messages instead of tracebacks.
- Docs & tests:
  - Documented fuzzy license behavior and developer metadata flag in `docs/TEMPLATES.md`.
  - Added tests for `--version` and license not-found/fuzzy-match behaviors (`tests/test_cli_version.py`, `tests/test_cli_license_not_found.py`).

## 2026-01-05 — 0.1.3

- Documentation & developer tooling:
  - Added docstrings and type hints to core modules (`renderer`, `plugins`, `registry`) to improve code clarity and editor support.
  - Added `.pre-commit-config.yaml` with `black`, `isort`, and `ruff` to standardize formatting and linting.
  - CI updated to run pre-commit checks on push and pull requests.
- Tests:
  - Added tests to verify package version and basic rendering behavior: `tests/test_version.py`, `tests/test_renderer.py`, `tests/test_docstrings.py`.
- Packaging:
  - Bumped package version to **0.1.3** and updated `pyproject.toml` and `bldrx.__version__`.
- Misc:
  - Updated `README.md` contributing section with pre-commit usage.
- Type annotations & tests:
  - Added additional type annotations and docstrings to `bldrx.engine` public methods to improve clarity and enable static analysis.
  - Added tests covering `Engine` behaviors: listing templates, rendering a template file, manifest generation & verification, and dry-run apply previews (`tests/test_engine.py`).
  - Extended `tests/test_docstrings.py` to assert presence of Engine docstrings.
  - Added comprehensive license templates (MIT, Apache-2.0, BSD-3-Clause, BSD-2-Clause, ISC, GPL-3.0, AGPL-3.0, LGPL-3.0, MPL-2.0, UNLICENSE, CC0-1.0, Artistic-2.0, EPL-2.0, Boost-1.0) under `bldrx/templates/licenses` with defaults and documentation. (`tests/test_templates_licenses.py` and `tests/test_templates_render.py` added to exercise rendering and validation.)
  - Added `docs/TEMPLATES.md` describing the license templates and usage.
  - CLI: added `--license` flag to `bldrx new` and `bldrx add-templates` to conveniently include a chosen license template by identifier (e.g., `--license MIT`).


## 2026-01-04 — 0.1.1

- Template validator / linter: validation and tests added to detect Jinja syntax errors and unresolved variables; `Engine.validate_template` implemented and CLI integration available.
- Improve preview & dry-run UX: machine-readable `--json` dry-run output and preview diffs implemented (`preview-template --render --diff`, `--json`).
- Transactional apply & atomic replace: per-file atomic replace using temp files and `os.replace`, rollback on failure; backup support added to allow reversible changes.
- Safe merging (merge strategies): added `--merge` strategies: `append`, `prepend`, and `marker` (file markers).
- Encoding & binary detection: templates and raw files that are non-UTF8 or large/binary are detected and skipped with clear statuses (`would-skip-binary`, `would-skip-large`).
- Concurrency & locking: per-template lockfiles prevent concurrent installs/uninstalls; supports timeouts and robust error handling.
- Template provenance & signatures: `bldrx-manifest.json` generation and verification (`Engine.generate_manifest`, `Engine.verify_template`); optional HMAC-SHA256 signatures via `BLDRX_MANIFEST_KEY` and `--sign`/`--verify` flags.
- Remote template fetching with sandbox: `Engine.fetch_remote_template()` supports `file://` archives, `.tar.gz`/`.zip`, and `git` remotes with safe extraction and optional manifest verification.
- Manifest generation & registry CLI: added `bldrx manifest create` to generate manifests and sign them; tests added for provenance workflows.
- Plugin system & remote sources: `PluginManager` and `bldrx plugin` CLI implemented; fetch improvements include HTTP(S) download and Git clone support.
- Template catalog CLI: added `bldrx catalog publish/search/info/remove` for a local JSON registry format stored under `BLDRX_REGISTRY_DIR` (useful for sharing and discovery).
- CI: added `scripts/ci_validate_templates.py` and a `validate-templates` GitHub Actions job which validates template syntax, undefined variables (warnings by default), and manifests (HMAC checks); CI installs the package in editable mode prior to validation.
- Analytics & telemetry (opt-in): added `bldrx.telemetry` and `bldrx telemetry` CLI for opt-in telemetry; events are written locally to `~/.bldrx/telemetry.log` and remote endpoint support is available but off by default.
- Docs: added `docs/ADVANCED_SCENARIOS.md` documenting manifest signing, registry/publish workflows, CI validation, telemetry privacy, plugin guidance, and troubleshooting tips.



## 2026-01-04 — 0.1.2

- Added file inclusion/exclusion filters for templates:
  - CLI options: `--only` and `--except` (comma-separated relative paths) added to `bldrx new`, `bldrx add-templates` and `bldrx preview-template`.
  - Engine support: `Engine.apply_template(..., only_files=[...], except_files=[...])` filters applied to both raw and `.j2` template files (for `.j2` use rendered target paths, e.g. `README.md`).
  - Tests: added `tests/test_apply_filters.py` covering `--only`, `--except`, and combined behaviors.
- Documentation: updated `README.md` with a comprehensive commands table and examples for `--only`/`--except` usage.
- Added safe backups and optional git commit support for applied changes: `backup=True` stores reversible backups under `./.bldrx/backups/<timestamp>/...` and `git_commit=True` stages & commits changes in destination repos when available.

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
- Added diffs & preview enhancements:
  - `Engine.preview_template(..., diff=True)` returns unified diffs for changed or new files; `preview-template --render --diff` prints diffs and `--json` prints machine-readable previews.
- Documentation & tests:
  - Split docs into `README.md` (user docs) and `PROJECT_OUTLINE.md` (design/roadmap); added `BUILD_INSTRUCTIONS.md` and `CHANGELOG.md`.
  - Added tests for engine, CLI, templates, user templates, preview, docs and packaging; all tests passing locally.
- Packaging & CI:
  - Ensure templates included in package via `MANIFEST.in` and `pyproject.toml` package-data.
  - Built and validated wheel locally.
  - Added GitHub Actions workflow to run tests on push/PR and fixed artifact uploads.
  - Fix applied: make artifact names unique per job/run and add `build-artifacts` job to build and upload distributions on tag pushes.
- Added `--wrap` option to `install-template` to allow preserving the source top-level folder when installing templates (useful for `.github` directories); default installs contents-only.

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
- Template provenance & signatures: completed — added manifest verification support (`Engine.verify_template`) and optional HMAC-SHA256 signatures using the `BLDRX_MANIFEST_KEY` env var; `--verify` will fail on mismatches or invalid signatures (HMAC support added; asymmetric signatures planned).
- Remote template fetching with sandbox: implemented — added `Engine.fetch_remote_template()` to fetch and extract local `file://` tar/zip archives into the user templates dir using a secure sandbox (prevents path traversal). Optionally runs manifest verification after extraction.

---

(End of changelog entry.)
