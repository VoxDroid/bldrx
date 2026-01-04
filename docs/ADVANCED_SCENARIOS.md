# Advanced Scenarios — Bldrx

This document explains advanced workflows and recommendations for template authors and integrators.

## Manifest signing & verification

- bldrx supports `bldrx-manifest.json` files which map `files` → SHA256 hex strings. Use `bldrx manifest create <template>` to generate a manifest.
- Optional HMAC signing: `bldrx manifest create <template> --sign` adds an `hmac` field computed with HMAC-SHA256 over the canonical `{"files": ...}` JSON using the `BLDRX_MANIFEST_KEY` secret.
- Best practices:
  - Keep signing keys private; use CI secrets to sign manifests at publish time.
  - Prefer asymmetric signatures (public-key) for distributed trust; HMAC is suitable for shared-secret workflows.
  - Verify manifests before applying templates using `--verify` (for CLI commands: `bldrx new ... --verify`, `bldrx add-templates ... --verify`).

## Registry & catalog workflows

- Local catalog: use `bldrx catalog publish <src> --name <name> --version <ver> --tags "a,b"` to add a JSON metadata entry into your local registry (`BLDRX_REGISTRY_DIR` or `~/.bldrx/registry`).
- Search and info: `bldrx catalog search <query>` and `bldrx catalog info <name>` to discover installed templates.
- Publish workflow:
  1. Author template and test locally (use `bldrx validate-template` helpers or `scripts/ci_validate_templates.py`).
  2. Create and sign manifest (CI signs manifest) and commit it to the template source.
  3. Publish to registry (local or remote; remote publishing will be supported in a future release).

## Remote fetch & verification

- `Engine.fetch_remote_template(url)` supports `file://`, HTTP(S) downloads, and `git+` or git remote URLs.
- Archives are extracted in a sandbox and checked to avoid path traversal. After extraction, if `bldrx-manifest.json` is present, verification is performed (if requested).
- Always use `--verify` or require manifests for production flows.
- CI validation strictness: by default the CI validation script (`scripts/ci_validate_templates.py`) treats Jinja undefined variables as **warnings** (helps avoid false positives when templates intentionally rely on user metadata). To make CI fail on undefined variables, set the environment variable `BLDRX_VALIDATE_FAIL_ON_UNDEFINED=1` in the workflow or job.

## CI Integration

- Use `scripts/ci_validate_templates.py` in CI to validate templates (syntax, unresolved variables, and manifest verification). The repository includes a `validate-templates` job in `.github/workflows/ci.yml` which runs on push/PR.
- For publishing artifacts (sdist/wheel), use the `build-artifacts` job (runs on tag) and add a `publish` job that runs on release with `twine` and secure secrets (not yet added).

## Telemetry & privacy

- Telemetry is strictly opt-in. Users must enable telemetry via `BLDRX_ENABLE_TELEMETRY=1` or `bldrx telemetry enable`.
- Events are written locally to `~/.bldrx/telemetry.log` (newline-delimited JSON). If `BLDRX_TELEMETRY_ENDPOINT` is configured, bldrx will attempt to POST events to the endpoint (best-effort, non-blocking).
- Do not send secrets or private data in telemetry events. The telemetry helper is intentionally minimal and focuses on usage metrics and errors only.

## Plugins & Extensions

- Plugins are simple Python modules with a `register(engine)` function. Install via `bldrx plugin install <path>` and `bldrx plugin list` / `bldrx plugin remove <name>`.
- Plugins should avoid side effects at import time and should register handlers or modify engine behavior in `register`.
- Plugins are loaded in a best-effort manner; plugin failures do not prevent the engine from running.

## Template authorship tips

- Keep templates small and modular (e.g., `github/`, `ci/`, `lint/`).
- Add `bldrx-manifest.json` to the template and sign it via CI for distribution.
- Add snapshot tests (see `tests/snapshots/`) so CI can detect regressions in rendered templates.

## Troubleshooting

- If `bldrx apply` fails due to manifest mismatch, run `bldrx manifest create` locally and confirm checksums, then re-run with `--verify` after fixing or acquiring the correct manifest/signature.
- Use `bldrx preview-template` to inspect rendered output before applying.
- For plugin issues, check `~/.bldrx/plugins/` for installed plugins and use `bldrx plugin remove <name>` to disable.

