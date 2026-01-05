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

Use the CLI convenience flag `--license <ID>` with `bldrx new` or `bldrx add-templates` to include a specific license template (e.g., `--license MIT`). You can also list or preview license templates via `bldrx preview-template licenses` or `bldrx preview-template licenses/MIT --file LICENSE.j2 --render --meta author_name="You" --meta year=2026`.

Each license template provides `LICENSE.j2` which expects:

- `year` (int)
- `author_name` (string)

For convenience, each license folder includes a `ci_metadata.json` with sane defaults that will be used by the validator when rendering templates during CI.

## Best practices

- Provide `project_name`, `author_name`, `github_username` metadata when rendering templates.
- Ensure templates include a `README.md` and `LICENSE` where appropriate. The CI helper will warn if they are missing.
