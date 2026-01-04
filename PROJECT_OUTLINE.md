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
| Template rendering (Jinja2) | Implemented | StrictUndefined to detect missing placeholders |
| Dry-run and force behavior | Implemented | `would-render` / `would-copy` / `would-remove` statuses reported |
| User templates directory & env override | Implemented | `BLDRX_TEMPLATES_DIR` and default user dir supported |
| Template preview & file list | Implemented | `preview-template` and `list-templates --details` added |
| Templates: python-cli | Implemented | README, LICENSE, src template |
| Templates: github meta files | Implemented | Root files and `.github/` issue templates, funding.yml |
| Templates: CI workflows | Implemented | `ci.yml` and `deploy.yml` templates included |
| Templates: lint/format | Implemented | `.eslintrc`, `.prettierrc`, `pyproject.toml` templates |
| Templates: docker | Implemented | `Dockerfile.j2` and `.dockerignore.j2` |
| Templates: node-api, react-app | Implemented | Basic skeleton templates included |
| Safe merging (content-level merge) | Planned | Current behavior: skip existing unless `--force` (no intelligent merge yet) |
| Config files for defaults (`.bldrx` etc.) | Planned | Add user config to store defaults and metadata per user/project |
| Tests | Implemented | Unit tests for engine, CLI, templates, user templates, docs included |
| CI (tests on push/PR) | Implemented | `.github/workflows/ci.yml` runs pytest matrix (3.9–3.11) |
| CI artifact build/publish on tag | Planned | Add workflow to build artifacts and upload/publish on tag |

---

## Roadmap & Notes

- Priorities: add content-merge strategies, plugin/remote template fetching, config file support.
- This outline documents the current implementation and planned improvements; use `README.md` for quickstart and user documentation.

---

## Top priorities (High impact, small→medium effort) ✅

These are the next features we will implement, prioritized for impact and feasibility. Each entry includes a short acceptance criteria and testing notes so we can proceed TDD-style.

1. Safe backups & Git integration (High priority, small effort)
   - Goal: Before modifying files, create a reversible backup (on-disk snapshot) and optionally create a git commit for the injected changes.
   - Acceptance criteria:
     - `Engine.apply_template(..., backup=True)` creates a `./.bldrx/backups/<timestamp>/` snapshot of overwritten files.
     - `Engine.apply_template(..., git_commit=True, git_message=<msg>)` commits the changes into the repo in `dest` with the provided message.
     - Tests: unit tests that validate backup files and git commit message.

2. Show diffs / patch preview (small)
   - Goal: On `--dry-run` or `preview`, show unified diffs of what would change.
   - Acceptance criteria:
     - `preview-template --render --diff` prints unified diff to stdout.
     - `engine.render_preview(..., diff=True)` returns a diff string.
     - Tests: snapshot tests asserting expected diff output for a small template change.

3. Template validator / linter (small)
   - Goal: Validate `.j2` syntax and warn about unresolved variables before apply.
   - Acceptance criteria:
     - `Engine.validate_template(src)` detects Jinja syntax errors and missing placeholders (configurable required placeholders).
     - Tests: unit tests that feed a broken template and assert validation errors.

4. Improve preview & dry-run UX (small)
   - Goal: Make `--dry-run` verbose by default and add `--json` output for automation.
   - Acceptance criteria:
     - `engine.apply_template(..., dry_run=True)` returns structured actions; `--json` flag prints machine-readable output.
     - Tests: validate machine-readable (JSON) dry-run output structure and values.

(Other planned items will be added below in order of priority.)

## Notes

This file is a project outline and prototype documentation. For the canonical user-facing documentation and quickstart, see `README.md`.
