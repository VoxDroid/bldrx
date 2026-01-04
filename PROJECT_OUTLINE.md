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

## Notes

This file is a project outline and prototype documentation. For the canonical user-facing documentation and quickstart, see `README.md`.
