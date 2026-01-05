# Templates

This document describes the packaged templates and recommended metadata.

## License templates

We include a curated set of common licenses under `bldrx/templates/licenses/`:

- MIT
- Apache-2.0
- BSD-3-Clause
- BSD-2-Clause
- ISC
- GPL-3.0
- AGPL-3.0
- LGPL-3.0
- MPL-2.0
- Artistic-2.0
- EPL-2.0
- Boost-1.0
- UNLICENSE
- CC0-1.0

Use the CLI convenience flag `--license <ID>` with `bldrx new` or `bldrx add-templates` to include a specific license template (e.g., `--license MIT`). The CLI will attempt to resolve fuzzy identifiers (e.g., `--license Apache` → `licenses/Apache-2.0`) and will warn when multiple matches are found and choose the first match; when no matches exist, a friendly error lists available licenses. You can also list or preview license templates via `bldrx preview-template licenses` or `bldrx preview-template licenses/MIT --file LICENSE.j2 --render --meta author_name="You" --meta year=2026`.

Each license template provides `LICENSE.j2` which expects:

- `year` (int)
- `author_name` (string)

There is also a global developer flag `--developer-metadata` (set on the `bldrx` command group) that, when enabled, injects additional metadata into rendered templates for debugging and provenance: `developer` (true), `bldrx_version` and `dev_timestamp` (ISO 8601 UTC). This is useful when you need to track what version of `bldrx` produced a rendered artifact.
For convenience, each license folder includes a `ci_metadata.json` with sane defaults that will be used by the validator when rendering templates during CI.

## Best practices

- Provide `project_name`, `author_name`, `github_username` metadata when rendering templates.
- Ensure templates include a `README.md` and `LICENSE` where appropriate. The CI helper will warn if they are missing.
