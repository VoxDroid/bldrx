# **Project Outline: Bldrx – Project Scaffold & Template Injector**

**Goal:** A CLI-first tool that lets you **quickly scaffold new projects** and **inject templates into existing projects**, including GitHub meta files, CI/CD configs, folder structures, and fully customizable placeholders.

---

## **Core Features (MVP)**

### A. CLI Commands

| Command                                  | Purpose                                | Details                                                                                  |
| ---------------------------------------- | -------------------------------------- | ---------------------------------------------------------------------------------------- |
| `bldrx new <project_name>`               | Scaffold a new project                 | Choose project type (Python CLI / library / Node API / React app) and optional templates |
| `bldrx add-templates <existing_project>` | Inject templates into existing project | Add GitHub meta files, CI/CD workflows, README, contributing docs, etc.               |
| `bldrx list-templates`                   | Show available templates               | JSON or human-readable table                                                           |
| `bldrx remove-template <name>`           | Remove a template from a project       | Safety flag to prevent accidental deletes (requires `--force` or `--yes`)             |
---

### B. Templates (Expanded)

**Core idea:** Each template is self-contained and customizable. Placeholders can be automatically replaced, and users can provide **custom names, emails, project name, year, and other metadata**.

---

## Checklist

| Feature / Area | Status | Notes |
| --- | --- | --- |
| CLI: `new` (project scaffolding) | Implemented | Supports `--type`, `--templates`, `--dry-run`, `--force` |
| CLI: `add-templates` | Implemented | Supports interactive selection, `--templates-dir`, metadata |
| CLI: `list-templates` | Implemented | `--details` shows files, `--json` outputs JSON |
| CLI: `remove-template` | Implemented | Safety prompts, `--yes` implies removal, `--dry-run` available |
| CLI: `install-template` / `uninstall-template` | Implemented | Installs to user templates dir; interactive prompts supported. Supports `--wrap` to preserve the source top-level folder (e.g., install `.github` as a folder); default behavior copies contents only. |
| Remote template fetching with sandbox | Implemented | `Engine.fetch_remote_template(url, name, force=True)` supports `file://` archives (tar.gz, zip) and directories; extracts in a sandbox, prevents path traversal, and optionally verifies manifest before installation. |
| Template rendering (Jinja2) | Implemented | StrictUndefined to detect missing placeholders |
| Dry-run and force behavior | Implemented | `would-render` / `would-copy` / `would-remove` statuses reported |
| User templates directory & env override | Implemented | `BLDRX_TEMPLATES_DIR` and default user dir supported |
| Template preview & file list | Implemented | `preview-template` and `list-templates --details` added |
| Show diffs / patch preview | Implemented | `preview-template --render --diff` shows unified diffs; `--json` outputs machine-readable previews; `Engine.preview_template` added |
| Templates: python-cli | Implemented | README, LICENSE, src template |
| Templates: github meta files | Implemented | Root files and `.github/` issue templates, funding.yml |
| Templates: CI workflows | Implemented | `ci.yml` and `deploy.yml` templates included |
| Templates: lint/format | Implemented | `.eslintrc`, `.prettierrc`, `pyproject.toml` templates |
| Templates: docker | Implemented | `Dockerfile.j2` and `.dockerignore.j2` |
| Templates: node-api, react-app | Implemented | Basic skeleton templates included |
| Safe merging (content-level merge) | Implemented | Added `--merge` strategies: `append`, `prepend`, `marker` (file markers). `patch` reserved for future work. |
| File inclusion/exclusion filters (`--only` / `--except`) | Implemented | Added CLI flags and `Engine.apply_template(..., only_files=..., except_files=...)`. Matches rendered target names for `.j2` templates. |
| Safe backups & Git integration | Implemented | `Engine.apply_template(..., backup=True)` creates backups; `git_commit=True` stages and commits changes when `dest` is a git repo. |
| Config files for defaults (`.bldrx` etc.) | Planned | Add user config to store defaults and metadata per user/project |
| Template registry / manifest | Implemented | Add manifest generation, signing helpers and `bldrx manifest create` CLI; tests added, HMAC support implemented. |
| Template catalog CLI (search/info) | Implemented | `bldrx catalog publish/search/info/remove` added; simple local registry format and CLI helpers implemented. |
| Encoding & binary detection | Implemented | Detect non-UTF8 templates and large/binary files and skip with clear statuses (`would-skip-binary`, `would-skip-large`) |
| Concurrency & locking for user templates dir | Implemented | Per-template lockfiles to serialize installs/uninstalls; Timeout and errors handled; tests added |
| Transactional apply & atomic replace | Implemented | Per-file atomic replace using temp files in destination dir; rollback on failure; supports `--atomic` and `backup`; tests added (see `tests/test_transactional_apply.py`) |
| Tests | Implemented | Unit tests for engine, CLI, templates, user templates, docs included |
| CI (tests on push/PR) | Implemented | `.github/workflows/ci.yml` runs pytest matrix (3.9–3.11), a `type-check` job using `pyright` (configured by `pyrightconfig.json`), and a `validate-templates` job which validates templates and manifests. Matrix has been expanded to include `windows-latest` and `macos-latest` to improve cross-platform coverage. A local `mypy` pre-commit hook provides fast developer feedback. |
| CI artifact build/publish on tag | Implemented | `build-artifacts` job builds sdist/wheel on tag and uploads as artifacts. |
| Analytics/logging (opt-in) | Implemented | `bldrx telemetry` CLI group and `bldrx.telemetry` helper; opt-in only (BLDRX_ENABLE_TELEMETRY). |
| Docs for advanced scenarios | Implemented | Added `docs/ADVANCED_SCENARIOS.md` covering manifests, registry, CI, plugins, and telemetry. |

---

## Roadmap & Notes

- Priorities: add content-merge strategies, plugin/remote template fetching, config file support.
- This outline documents the current implementation and planned improvements; use `README.md` for quickstart and user documentation.

---

## Top priorities (High impact, small→medium effort) ✅

These are the next features we will implement, prioritized for impact and feasibility. Each entry includes a short acceptance criteria and testing notes so we can proceed TDD-style.

2. Show diffs / patch preview (Implemented)
   - Goal: On `--dry-run` or `preview`, show unified diffs of what would change.
   - Status: Implemented. See `Engine.preview_template(...)` and CLI flags `preview-template --render --diff` and `--json`.
   - Acceptance criteria (met):
     - `preview-template --render --diff` prints unified diff to stdout.
     - `preview-template --render --diff --json` outputs machine-readable JSON suitable for CI/automation.
     - `Engine.preview_template(..., diff=True)` returns a list of preview entries with `diff` fields when requested.
     - Tests: added `tests/test_preview_diff.py` and `tests/test_cli_preview_diff.py` validating unified diff and JSON output.

3. Template validator / linter (Implemented)
   - Goal: Validate `.j2` syntax and warn about unresolved variables before apply.
   - Status: Implemented. `Engine.validate_template` (TDD) detects template syntax errors and reports unresolved variables; tests are included.
   - Acceptance criteria:
     - `Engine.validate_template(template_name)` returns a dict containing `syntax_errors` and `undefined_variables` mappings per-file.
     - Tests: unit tests `tests/test_template_validator.py` verify detection of syntax errors, unresolved variables, and clean templates.

4. Improve preview & dry-run UX (small)
   - Goal: Make `--dry-run` verbose by default and add `--json` output for automation.
   - Acceptance criteria:
     - `engine.apply_template(..., dry_run=True)` returns structured actions; `--json` flag prints machine-readable output.
     - Tests: validate machine-readable (JSON) dry-run output structure and values.

(Other planned items will be added below in order of priority.)
3. Template validator / linter (Implemented)
   - Goal: Validate `.j2` syntax and warn about unresolved variables before apply.
   - Status: Implemented. `Engine.validate_template` (TDD) detects template syntax errors and reports unresolved variables; tests are included.
   - Acceptance criteria:
     - `Engine.validate_template(template_name)` returns a dict containing `syntax_errors` and `undefined_variables` mappings per-file.
     - Tests: unit tests `tests/test_template_validator.py` verify detection of syntax errors, unresolved variables, and clean templates.

4. Improve preview & dry-run UX (small)
   - Goal: Make `--dry-run` verbose by default and add `--json` output for automation.
   - Acceptance criteria:
     - `engine.apply_template(..., dry_run=True)` returns structured actions; `--json` flag prints machine-readable output.
     - Tests: validate machine-readable (JSON) dry-run output structure and values.

(Other planned items will be added below in order of priority.)

## Notes

This file is a project outline and prototype documentation. For the canonical user-facing documentation and quickstart, see `README.md`.
