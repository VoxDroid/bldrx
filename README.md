# Bldrx — Project Scaffolding & Template Injector

Bldrx is a CLI-first tool to quickly scaffold new projects and inject reusable templates into existing repositories.

This README contains quick installation and usage instructions. For the project prototyping notes and full outline see `PROJECT_OUTLINE.md`.

---

## Quickstart

Install in a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows
pip install --upgrade pip
pip install -r requirements.txt
```

Run tests:

```bash
python -m pytest -q
```

Build and install locally:

```bash
python -m build
pip install dist/*.whl
```

## Examples

List available templates:

```bash
bldrx list-templates
```

Install a user template and list templates:

```bash
bldrx install-template ~/my-templates/cool-template --name cool
bldrx list-templates
```

Preview a template file or its rendered output:

```bash
bldrx list-templates --details
bldrx preview-template python-cli --file README.md.j2
bldrx preview-template python-cli --file README.md.j2 --render --meta project_name=demo
```

For full usage and prototyping notes, see `PROJECT_OUTLINE.md` and `BUILD_INSTRUCTIONS.md`.

## Configuration

Environment variables and overrides:

- `BLDRX_TEMPLATES_DIR` — override the default user templates directory for the current session or environment.
- `--templates-dir <path>` — use a custom templates root for a single CLI invocation.

Config file (planned): support a `.bldrx` TOML/YAML file to store default metadata and templates selections per project.

## Contributing & Support

- Contributions are welcome: open issues or PRs. See `CONTRIBUTING.md` template for guidance.
- For support, open an issue on the repository or contact the project maintainer listed in `pyproject.toml`.

---




### A. CLI Commands

| Command                                  | Purpose                                | Details                                                                                  |
| ---------------------------------------- | -------------------------------------- | ---------------------------------------------------------------------------------------- |
| `bldrx new <project_name>`               | Scaffold a new project                 | Choose project type (Python CLI / library / Node API / React app) and optional templates |
| `bldrx add-templates <existing_project>` | Inject templates into existing project | Add GitHub meta files, CI/CD workflows, README, contributing docs, etc. |
| `bldrx list-templates`                   | Show available templates               | JSON or human-readable table                                                           |
| `bldrx remove-template <name>`           | Remove a template from a project       | Safety flag to prevent accidental deletes (requires `--force` or `--yes`)             |

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

Remote fetching (local archives)

- `Engine.fetch_remote_template(url, name, force=True)` supports local `file://` archives (`.tar.gz`, `.tgz`, `.zip`) and directories. Archives are extracted into a secure sandbox and checked for path traversal before installation. A CLI helper for remote installs (HTTP/Git) is planned.

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

Planned: Add a workflow that builds distribution artifacts on tags (sdist/wheel) and stores them as GitHub Actions artifacts — optionally publish to PyPI on release tags.

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