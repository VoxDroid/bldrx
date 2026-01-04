# bldrx — Project scaffolding & template injector

bldrx is a developer-first CLI for scaffolding new projects and injecting reusable templates (CI, GitHub meta files, README/license, lint configs) into new or existing repositories.

This README contains quick installation and usage instructions. For the project prototyping notes and full outline see `PROJECT_OUTLINE.md`.

---

## Quickstart

Install (editable mode is recommended during development):

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e .
```

Run tests:

```bash
pytest -q -vv
```

Get help:

```bash
bldrx --help
bldrx <command> --help
```


## Quick examples

List available templates (human- and machine-readable):

```bash
bldrx list-templates
bldrx list-templates --json
bldrx list-templates --details   # show files contained in each template
```

Install a user template and list templates:

```bash
bldrx install-template /path/to/local-template --name cool --wrap
bldrx list-templates
```

Preview a template file or its rendered output:

```bash
bldrx preview-template python-cli                  # list template files
bldrx preview-template python-cli --file README.md.j2
bldrx preview-template python-cli --file README.md.j2 --render --meta project_name=demo
bldrx preview-template python-cli --render --diff --meta project_name=demo
```

For full usage and prototyping notes, see `PROJECT_OUTLINE.md`, `BUILD_INSTRUCTIONS.md`, and `docs/ADVANCED_SCENARIOS.md`.


## Configuration

Environment variables and overrides:

- `BLDRX_TEMPLATES_DIR` — override the default user templates directory for the current session or environment.
- `--templates-dir <path>` — use a custom templates root for a single CLI invocation.

Config file (planned): support a `.bldrx` TOML/YAML file to store default metadata and templates selections per project.

## Contributing & Support

- Contributions are welcome: open issues or PRs. See `CONTRIBUTING.md` template for guidance.
- For support, open an issue on the repository or contact the project maintainer listed in `pyproject.toml`.

## Project metadata

- **Owner:** VoxDroid
- **GitHub:** https://github.com/VoxDroid
- **Repository:** https://github.com/VoxDroid/bldrx
- **Contact:** izeno.contact@gmail.com

---




### CLI reference — commands & options

Below is a comprehensive table with each command, key options, a short description, and a basic example. Use `bldrx <command> --help` for full option lists and platform-specific notes.

| Command | Key options | Description | Example |
| --- | --- | --- | --- |
| `bldrx new <project_name>` | `--type` `--templates` `--author` `--email` `--github-username` `--meta KEY=VAL` `--dry-run` `--json` `--force` `--merge` `--verify` | Scaffold a new project from templates. `--templates` overrides type defaults. `--dry-run` shows planned actions. | `bldrx new my-tool --type python-cli --templates python-cli,ci --author "You" --dry-run` |
| `bldrx add-templates <project_path>` | `--templates` `--templates-dir` `--author` `--email` `--github-username` `--meta` `--dry-run` `--json` `--force` `--merge` `--verify` | Inject one or more templates into an existing project. If `--templates` omitted, interactive prompt lists available templates. | `bldrx add-templates ./repo --templates contributing,ci --dry-run` |
| `bldrx list-templates` | `--details` `--templates-dir` `--json` | List templates from built-in and user sources. `--details` shows files inside templates. | `bldrx list-templates --details` |
| `bldrx preview-template <template>` | `--file <path>` `--render` `--diff` `--meta KEY=VAL` `--templates-dir` | Show raw template files or their rendered content. `--diff` shows patch/diff against target project when rendering. | `bldrx preview-template python-cli --file README.md.j2 --render --meta project_name=demo` |
| `bldrx install-template <src_path>` | `--name` `--wrap` `--force` | Install a local template into the user templates directory. `--wrap` preserves the source top folder. | `bldrx install-template ./my-template --name cool` |
| `bldrx uninstall-template <name>` | `--yes` | Remove a user template. Use `--yes` to skip confirmation. | `bldrx uninstall-template cool --yes` |
| `bldrx remove-template <project_path> <template_name>` | `--templates-dir` `--yes` `--force` `--dry-run` | Remove files previously added by a template. Requires explicit confirmation (`--yes`) or `--force`. Dangerous—use `--dry-run` first. | `bldrx remove-template ./repo contributing --dry-run` |
| `bldrx manifest create <template_name>` | `--templates-dir` `--output` `--sign` `--key` | Generate a `bldrx-manifest.json` with per-file SHA256 checksums; `--sign` adds HMAC-SHA256 (requires `BLDRX_MANIFEST_KEY` or `--key`). | `bldrx manifest create cool --sign` |
| `bldrx catalog publish` | `--name` `--version` `--description` `--tags` `--sign` `--key` `--force` | Publish a local template into the local catalog/registry (metadata entry only). | `bldrx catalog publish ./my-template --name cool --version 1.0.0 --tags "ci,github"` |
| `bldrx catalog search <query>` | (query optional) | Search the local catalog by name, tag, or description. | `bldrx catalog search ci` |
| `bldrx catalog info <name>` | `--version` | Show metadata for catalog entry. | `bldrx catalog info cool` |
| `bldrx catalog remove <name>` | `--version` `--yes` | Remove a catalog entry; `--yes` skips confirmation. | `bldrx catalog remove cool --yes` |
| `bldrx telemetry enable / disable /status` | (flags: none) | Opt-in telemetry controls (local-first, newline-delimited JSON log). | `bldrx telemetry enable` |
| `bldrx plugin install / list / remove` | `--name` `--force` `--yes` | Install, list, and remove plugins managed by the plugin manager. | `bldrx plugin install ./my-plugin` |

> Tip: pass repeated `--meta key=val` flags to provide multiple metadata values (e.g., `--meta project_name=MyProj --meta funding_url=https://...`).

---

### B. Templates (Expanded)

**Core idea:** Each template is self-contained and customizable. Placeholders can be automatically replaced, and users can provide **custom names, emails, project name, year, and other metadata**.

**Categories of templates:**

#### 1. **Project structure templates**

* `src/`, `tests/`, `README.md`, `LICENSE`
* Placeholders: `{{project_name}}`, `{{author_name}}`, `{{email}}`, `{{year}}`

#### 2. **GitHub meta templates**

* `.github/CODEOWNERS`
* `.github/CONTRIBUTING.md`
* `.github/CODE_OF_CONDUCT.md`
* `.github/SUPPORT.md`
* `.github/funding.yml`
* `.github/ISSUE_TEMPLATE/bug_report.md`
* `.github/ISSUE_TEMPLATE/feature_request.md`
* Users can provide **custom names, emails, GitHub usernames, funding links, and project names**

#### 3. **CI/CD workflows**

* `.github/workflows/ci.yml`
* `.github/workflows/deploy.yml`

#### 4. **Lint/Formatter configs**

* `.eslintrc.js`, `.prettierrc`, `pyproject.toml`

---

### C. Customization & Placeholders

All templates allow placeholders to be replaced automatically:

```text
{{project_name}} → user-defined or CLI argument
{{author_name}} → user-defined
{{email}} → user-defined
{{year}} → auto-detect current year
{{github_username}} → user-defined (via `--github-username` or `--meta github_username=...`) 
```

* Optional CLI flags or JSON/YAML config to provide default values (config file support planned).

**User templates & overrides:**

- Install reusable templates for the current user with `bldrx install-template <path> [--name NAME] [--force]`.
- Remove user templates with `bldrx uninstall-template <name> [--yes]`.
- Override or add a templates root for a single command using `--templates-dir <path>` or configure `BLDRX_TEMPLATES_DIR` env var to point to your user templates directory.

New: list & preview enhancements

- `bldrx list-templates --details` shows the subfiles contained in each template (including `.github` subfolders).
- `bldrx preview-template <template> --file <path>` shows raw template content; add `--render` and `--meta key=val` to render it with provided metadata.

Security & integrity

- Templates may include a `bldrx-manifest.json` describing per-file SHA256 checksums in a `files` mapping and an optional HMAC signature in the `hmac` field.
- Use the `--verify` flag when applying templates (`bldrx new ... --verify` or `bldrx add-templates ... --verify`) to require manifest verification before files are applied.
- For HMAC-protected manifests, set `BLDRX_MANIFEST_KEY` (shared secret) in the environment to validate signatures. Asymmetric signatures (public-key) are planned for a future release.
- You can generate manifests (and optional HMAC signatures) locally using the new CLI helper:

```bash
# create and write a manifest for a user template named `cool` (writes to template root)
bldrx manifest create cool --sign

# generate a manifest and write it to a specific file
bldrx manifest create cool --output /tmp/cool-manifest.json
```

Catalog (local)

- Publish a template metadata entry into your local catalog/registry:

```bash
# publish a local template directory as `cool` version 1.0.0
bldrx catalog publish ./my-template --name cool --version 1.0.0 --description "Cool template" --tags "ci,github"

# search the local catalog
bldrx catalog search ci

# show info for a specific template
bldrx catalog info cool

# remove an entry
bldrx catalog remove cool --yes
```

Telemetry (opt-in)

- Telemetry is strictly opt-in. You can enable it via environment or CLI:

```bash
# enable in current session
export BLDRX_ENABLE_TELEMETRY=1
# or CLI
bldrx telemetry enable

# check status
bldrx telemetry status
```

- By default telemetry writes newline-delimited JSON events to `~/.bldrx/telemetry.log`. You can override the endpoint for external collection with `BLDRX_TELEMETRY_ENDPOINT` (not enabled by default). All telemetry is best-effort and non-blocking; failures are ignored and events are local first.

Remote fetching (local archives, HTTP, Git)

- `Engine.fetch_remote_template(url, name, force=True)` supports local `file://` archives (`.tar.gz`, `.tgz`, `.zip`) and directories, HTTP(S) downloads, and `git+` or Git remote URLs (shallow `git clone`).
- Archives are extracted into a secure sandbox and checked for path traversal before installation. HTTP downloads are saved to a temporary file and then extracted; Git remotes are cloned and the repo root is used as the template source. Verification with `--verify` is applied after extraction/cloning when requested.
- CLI helpers for `bldrx fetch` and advanced remote registry are planned (for now use `bldrx manifest create` and `Engine.fetch_remote_template`).

Example (bash/macOS/Linux):

```bash
# install a template directory into the user templates dir
bldrx install-template ~/my-templates/cool-template --name cool

# list templates including user templates marker
bldrx list-templates
# or point a single command at a custom templates root
bldrx list-templates --templates-dir ~/other-templates

# Use BLDRX_TEMPLATES_DIR to override the default user templates dir
export BLDRX_TEMPLATES_DIR="$HOME/.config/my-bldrx/templates"
bldrx list-templates
```

Example (Windows PowerShell):

```powershell
# set env var for current session
$env:BLDRX_TEMPLATES_DIR = "$env:APPDATA\bldrx\templates"
# install using interactive prompt or explicit name
bldrx install-template C:\path\to\template --name cool
```
---

### D. CLI Options (Example)

```bash
# Scaffold new project with selected templates (dry-run)
bldrx new python-cli my_tool --templates security,ci --dry-run

# Inject templates into existing repo (dry-run)
bldrx add-templates ./existing-project --templates contributing,support --dry-run

# List all available templates (human-readable)
bldrx list-templates

# List templates as a JSON array
bldrx list-templates --json

# Remove templates from a project (requires --yes to confirm or --force)
bldrx remove-template ./existing-project contributing --yes

# Provide metadata overrides
bldrx new my_tool --author "Andrei" --email "andrei@example.com"
```

---

### E. Template Injection & Safe Merging

* Templates can be **applied to existing projects**
* Engine automatically:

  * Merges files safely
  * Replaces placeholders
  * Adds missing folders
  * Avoids overwriting existing files unless `--force` is used

---

## **Workflow**

### A. New Project Flow

1. User runs `bldrx new <project_name>`
2. CLI prompts for:

   * Project type (Python CLI, Python library, Node API, React app)
   * Optional templates (security.md, PR template, CI/CD, CONTRIBUTING.md, LICENSE, funding.yml, etc.)
   * Optional metadata: author name, email, GitHub username
3. Engine copies folder structure + applies templates + replaces placeholders
4. Output: fully scaffolded project ready to go

---

### B. Existing Project Flow

1. User runs `bldrx add-templates ./existing-project`
2. CLI lists available templates
3. User selects templates + metadata
4. Engine safely merges templates into project, replacing placeholders

---

## **Tech Stack**

| Layer           | Tech / Library         | Reason                                        |
| --------------- | ---------------------- | --------------------------------------------- |
| CLI             | Python                 | Cross-platform, easy file handling            |
| CLI Lib         | `click` or `argparse`  | Clean command definitions and options         |
| Template Engine | `jinja2`               | Placeholder replacement in templates          |
| File Handling   | `pathlib`, `shutil`    | File copy, merge, create directories          |
| Optional        | `watchdog`             | Detect changes for real-time template updates |
| Optional GUI    | `PySide6` or `Tkinter` | Interactive template selection                |

---

### CI / Continuous Integration

A GitHub Actions workflow is included at `.github/workflows/ci.yml` which runs the test suite on push and pull requests (matrix: Python 3.9, 3.10, 3.11).

This repository includes a `publish.yml` workflow (in `.github/workflows`) that will publish to PyPI when the latest commit subject equals `v<version>` from `pyproject.toml` (e.g., commit subject `v0.1.1` when package version is `0.1.1`).

- Set `PYPI_API_TOKEN` (PyPI API token) in GitHub Secrets to enable uploads.
- Optionally set `RELEASE_GITHUB_TOKEN` (a personal access token) to have the GitHub Release authored by your user rather than the Actions bot.

Prefer testing against TestPyPI before publishing to the real PyPI; the workflow can be adapted to publish to TestPyPI first.


## **Folder / File Structure**

```
bldrx/
├── bldrx/
│   ├── cli.py
│   ├── engine.py
│   ├── renderer.py
│   ├── templates/
│   │   ├── python-cli/ (implemented)
│   │   │   ├── src/main.py.j2
│   │   │   ├── README.md.j2
│   │   │   └── LICENSE.j2
│   │   ├── github/
│   │   │   ├── CODEOWNERS.j2
│   │   │   ├── CONTRIBUTING.md.j2
│   │   │   ├── CODE_OF_CONDUCT.md.j2
│   │   │   ├── SUPPORT.md.j2
│   │   │   ├── .github/
│   │   │   │   ├── funding.yml.j2
│   │   │   │   └── ISSUE_TEMPLATE/
│   │   │   │       ├── bug_report.md.j2
│   │   │   │       └── feature_request.md.j2
│   │   ├── node-api/
│   │   │   ├── package.json.j2
│   │   │   ├── src/index.js.j2
│   │   │   └── README.md.j2
│   │   ├── react-app/
│   │   │   ├── package.json.j2
│   │   │   ├── src/App.js.j2
│   │   │   └── README.md.j2
│   │   ├── ci/
│   │   │   ├── ci.yml.j2
│   │   │   └── deploy.yml.j2
│   │   ├── docker/
│   │   │   ├── Dockerfile.j2
│   │   │   └── .dockerignore.j2
│   │   └── lint/
│   │       ├── .eslintrc.js.j2
│   │       ├── .prettierrc.j2
│   │       └── pyproject.toml.j2
│   └── gui.py  # Optional GUI
├── tests/
├── README.md
└── setup.py
```

---

## **Optional / Future Features**

* Add **plugin system**: users can drop in custom templates (planned)
* Dry-run mode: preview changes before applying (implemented)
* Auto-fetch templates from GitHub repo (planned)
* Multi-language support (Python, Node, React) (partial support via `--type`, templates needed)
* Interactive metadata prompts for faster scaffolding (partial — prompts for project type implemented)

---

## **Resume Bullet Points**

1. **Primary bullet:**

> Developed **Bldrx**, a CLI tool for scaffolding new projects and injecting customizable templates into existing repositories, supporting GitHub meta files (CODEOWNERS, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SUPPORT.md, funding.yml, issue templates), CI/CD workflows, and project structure setup.

2. **Customization bullet:**

> Templates are fully configurable with placeholders for project name, author, email, GitHub username, and year, allowing automated metadata injection across multiple projects.

3. **Impact bullet:**

> Standardized project setup and reduced manual boilerplate tasks by ~80%, enabling fast, consistent project initialization for personal and client repositories.

---