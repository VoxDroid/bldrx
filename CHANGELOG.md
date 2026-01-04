# Changelog

All notable changes to this project are documented in this file.

## Unreleased — Planned improvements (Top priorities)

- Safe backups & Git integration: create reversible backups before modifying files; optional `--git-commit` to create a commit with the injected template and message.
- Template validator / linter: completed — validation and tests added to detect Jinja syntax errors and unresolved variables; CLI integration planned.
- Improve preview & dry-run UX: completed — machine-readable `--json` dry-run output and preview diffs implemented.
- Transactional apply & atomic replace: completed — per-file atomic replace (using temp files and `os.replace`), rollback on failure, and backup support; tests added.
- Safe merging (merge strategies): completed — added `--merge` with `append`, `prepend`, and `marker` strategies; `patch` reserved for future work.
- Encoding & binary detection: completed — templates that are non-UTF8 and large/binary raw files are now detected and skipped with clear statuses; tests added.
- Concurrency & locking: implemented — per-template lockfiles prevent concurrent installs/uninstalls; supports timeouts and tests validate blocking and timeout behavior.
- Template provenance & signatures: completed — added manifest verification support (`Engine.verify_template`) and optional HMAC-SHA256 signatures using the `BLDRX_MANIFEST_KEY` env var; `--verify` will fail on mismatches or invalid signatures (HMAC support added; asymmetric signatures planned).
- Remote template fetching with sandbox: added `Engine.fetch_remote_template()` to fetch and extract local `file://` tar/zip archives into the user templates dir using a secure sandbox (prevents path traversal). Optionally runs manifest verification after extraction. Tests added (`tests/test_remote_fetch.py`).
- Manifest generation & registry CLI: added `Engine.generate_manifest()` and `bldrx manifest create` to generate `bldrx-manifest.json` files for templates, optionally sign them with HMAC (`--sign`) using `BLDRX_MANIFEST_KEY`, and aid template registry workflows (tests added `tests/test_manifest_registry.py`).
- Plugin system & remote sources: implemented — added a `PluginManager` to install/load simple Python plugins from `~/.bldrx/plugins` and CLI helpers `bldrx plugin install/list/remove`. Added HTTP(S) download and `git clone` support to `Engine.fetch_remote_template()` with sandboxed extraction and optional manifest verification. Tests added (`tests/test_plugins.py`, network calls mocked where appropriate).
- Template catalog CLI: added `bldrx catalog publish/search/info/remove` for a simple local template catalog format stored under `BLDRX_REGISTRY_DIR` (default: `~/.bldrx/registry`). Useful as a local index for sharing, searching, and publishing templates. Tests added (`tests/test_catalog.py`).
- CI: added `scripts/ci_validate_templates.py` and a `validate-templates` GitHub Actions job which runs on push/PR and validates template syntax, undefined variables, and manifests (including HMAC checks). Note: CI now installs the local package (editable mode) before running validation so scripts can import `bldrx`. The validation script treats undefined Jinja variables as **warnings** by default; set `BLDRX_VALIDATE_FAIL_ON_UNDEFINED=1` to make CI strict and fail on undefined variables.
- Analytics & telemetry (opt-in): added `bldrx.telemetry` with a small opt-in telemetry helper that writes newline-delimited JSON events to a local log file (`~/.bldrx/telemetry.log`) and a `bldrx telemetry` CLI group to enable/disable/check status. Telemetry is disabled by default and includes an optional `BLDRX_TELEMETRY_ENDPOINT` for remote collection (best-effort, disabled by default). Tests added (`tests/test_telemetry.py`).
- Docs: added `docs/ADVANCED_SCENARIOS.md` documenting manifest signing, registry/publish workflows, CI validation, telemetry privacy, plugin guidance, and troubleshooting tips.

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
