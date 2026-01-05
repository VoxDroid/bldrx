# Getting Started with bldrx

This guide walks through the most common workflows: installing the CLI, scaffolding a new project, injecting templates into existing repositories, and validating templates.

## Install

Recommended (PyPI):

```bash
pip install -U bldrx
# verify
bldrx --version
```

Optional: install in an isolated environment using `pipx`:

```bash
pipx install bldrx
```

Developer / editable install:

```bash
python -m venv .venv
source .venv/bin/activate  # (Windows PowerShell: .\.venv\Scripts\Activate.ps1)
pip install -U pip
pip install -e .
```

## Quick scaffold (new project)

1. Preview with a dry-run first (safe):

```bash
bldrx new mytool --type python-cli --templates python-cli --author "You" --email you@example.com --dry-run
```

2. Apply the template for real once satisfied:

```bash
bldrx new mytool --type python-cli --templates python-cli --author "You" --email you@example.com
# cd mytool && git init && git add -A && git commit -m "Initial scaffold"
```

Notes:
- Use `--only` / `--except` to include or exclude specific template files (comma-separated paths).
- Use `--license MIT` to conveniently add a license file.

## Inject templates into an existing repo

Preview what will change (dry-run + JSON output for automation):

```bash
bldrx add-templates ./existing-repo --templates contributing,ci --dry-run --json
```

Inspect diffs before applying:

```bash
bldrx preview-template contributing --render --diff --meta project_name=demo
```

Apply once satisfied:

```bash
bldrx add-templates ./existing-repo --templates contributing,ci --meta project_name=Demo --force
```

## Template provenance & verification

Generate a manifest for a template (adds per-file SHA256 checksums):

```bash
bldrx manifest create my-template --sign
```

When applying templates, use `--verify` to ensure the manifest matches (and fail on mismatch):

```bash
bldrx add-templates ./repo --templates cool --verify
```

## Managing user templates

Install a local template into your user templates dir:

```bash
bldrx install-template /path/to/local-template --name cool --wrap
```

Uninstall:

```bash
bldrx uninstall-template cool --yes
```

Publish/search in local catalog (metadata only):

```bash
bldrx catalog publish ./my-template --name cool --version 1.0.0 --description "Cool template"
bldrx catalog search ci
bldrx catalog info cool
```

## Troubleshooting & Tips

- Use `--dry-run` and `--json` when adding templates to scripts or CI checks to avoid surprises.
- Templates support manifest verification (HMAC via `BLDRX_MANIFEST_KEY`) to provide supply-chain guarantees.
- Developer ergonomics: use `pre-commit` (black, isort, ruff, mypy) and optionally `pyright` for fast local type checks. Run `pre-commit run --all-files` before opening a PR.

## Next steps

For advanced usage see `docs/ADVANCED_SCENARIOS.md` (manifests, CI validation, plugin guidance, and remote registries).
