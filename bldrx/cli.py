from datetime import datetime
from pathlib import Path

import click

from . import __version__
from .engine import Engine


def _whoami_callback(ctx, param, value):
    # Use callback to handle the hidden easter egg cleanly during parsing
    if not value or getattr(ctx, "resilient_parsing", False):
        return value
    click.echo("Developed by VoxDroid — https://github.com/VoxDroid")
    ctx.exit(0)


@click.group()
@click.version_option(__version__)
@click.option(
    "--developer-metadata",
    "developer_metadata",
    is_flag=True,
    help="Include developer metadata (bldrx_version, dev_timestamp) when rendering templates",
)
@click.option(
    "--whoami",
    is_flag=True,
    hidden=True,
    callback=_whoami_callback,
    help="(hidden) Show developer attribution",
)
@click.pass_context
def cli(ctx, developer_metadata, whoami):
    """bldrx - project scaffold & template injector"""
    # Note: the --whoami option is handled via callback and will exit before reaching here
    ctx.ensure_object(dict)
    ctx.obj["developer_metadata"] = developer_metadata


@cli.command()
@click.argument("project_name")
@click.option(
    "--templates",
    default="",
    help="Comma separated templates to include (default: based on --type)",
)
@click.option(
    "--type",
    "project_type",
    type=click.Choice(["python-cli", "python-lib", "node-api", "react-app"]),
    default=None,
    help="Project type; used to choose default templates",
)
@click.option(
    "--license",
    "license_id",
    default=None,
    help="License identifier to include (e.g., MIT, Apache-2.0)",
)
@click.option("--author", default=None)
@click.option("--email", default=None)
@click.option(
    "--github-username", default=None, help="GitHub username to populate templates"
)
@click.option(
    "--meta",
    multiple=True,
    help="Additional metadata as KEY=VAL; can be passed multiple times",
)
@click.option("--force", is_flag=True)
@click.option(
    "--dry-run",
    "dry_run",
    is_flag=True,
    help="Show planned actions but do not write files",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output machine-readable JSON when used with --dry-run",
)
@click.option(
    "--merge",
    "merge_strategy",
    type=click.Choice(["append", "prepend", "marker", "patch"]),
    default=None,
    help="Merge strategy to use when target file exists",
)
@click.option(
    "--only",
    "only_files",
    default=None,
    help="Comma-separated list of relative template file paths to include (default: all)",
)
@click.option(
    "--except",
    "exclude_files",
    default=None,
    help="Comma-separated list of relative template file paths to exclude",
)
@click.option(
    "--verify",
    "verify_integrity",
    is_flag=True,
    help="Verify template integrity using bldrx-manifest.json before applying",
)
@click.pass_context
def new(
    ctx,
    project_name,
    templates,
    project_type,
    author,
    email,
    github_username,
    meta,
    force,
    dry_run,
    as_json,
    merge_strategy,
    only_files,
    exclude_files,
    verify_integrity,
    license_id,
):
    """Scaffold a new project"""
    engine = Engine()
    dest = Path(project_name)
    if dest.exists() and not force:
        click.echo(f"Destination {dest} already exists. Use --force to override.")
        raise SystemExit(1)
    # Determine templates: explicit --templates takes precedence; otherwise derive from project_type
    if templates:
        templates = [t.strip() for t in templates.split(",") if t.strip()]
    else:
        mapping = {
            "python-cli": ["python-cli"],
            "python-lib": ["python-cli"],
            "node-api": ["node-api"],
            "react-app": ["react-app"],
        }
        if project_type is None:
            # interactive prompt fallback
            project_type = click.prompt(
                "Project type",
                type=click.Choice(list(mapping.keys())),
                default="python-cli",
            )
        templates = mapping.get(project_type, ["python-cli"])
    # Build metadata
    metadata = {
        "project_name": project_name,
        "author_name": author or "",
        "email": email or "",
        "github_username": github_username or "",
    }
    # Attach developer metadata if global flag set
    if ctx.obj.get("developer_metadata"):
        metadata["developer"] = True
        metadata["bldrx_version"] = __version__
        metadata["dev_timestamp"] = datetime.utcnow().isoformat() + "Z"
    # parse extra metadata KEY=VAL
    for item in meta:
        if "=" in item:
            k, v = item.split("=", 1)
            metadata[k.strip()] = v.strip()
    all_actions = []

    # parse only/exclude lists
    def _parse_csv(s):
        if not s:
            return None
        return [p.strip().replace("\\", "/") for p in s.split(",") if p.strip()]

    only_list = _parse_csv(only_files)
    exclude_list = _parse_csv(exclude_files)

    # Inject license template if requested
    if license_id:
        lic_template = f"licenses/{license_id}"
        # Validate and try fuzzy matches
        # Gather actual license subtemplates from user templates and package templates
        license_roots = []
        if (engine.user_templates_root / "licenses").exists():
            license_roots.append(engine.user_templates_root / "licenses")
        if (engine.package_templates_root / "licenses").exists():
            license_roots.append(engine.package_templates_root / "licenses")
        available = []
        for root in license_roots:
            for child in root.iterdir():
                if child.is_dir():
                    available.append(f"licenses/{child.name}")
        available = sorted(set(available))
        # Replace any placeholder in `templates` with the resolved `lic_template` and de-duplicate
        placeholder = f"licenses/{license_id}"
        templates = [(lic_template if t == placeholder else t) for t in templates]
        seen = set()
        new_templates = []
        for t in templates:
            if t not in seen:
                new_templates.append(t)
                seen.add(t)
        templates = new_templates
        if lic_template not in available:
            lname = license_id.lower()
            matches = [
                t
                for t in available
                if t.startswith("licenses/") and lname in t.split("/", 1)[1].lower()
            ]
            if len(matches) >= 1:
                if len(matches) > 1:
                    click.echo(
                        f"Multiple license templates match '{license_id}'; choosing first match: {matches[0]}"
                    )
                lic_template = matches[0]
                click.echo(f"Using license template: {lic_template}")
            else:
                license_names = [
                    t.split("/", 1)[1] for t in available if t.startswith("licenses/")
                ]
                click.echo(
                    f"License '{license_id}' not found. Available licenses: {', '.join(license_names)}"
                )
                raise SystemExit(1)
        if lic_template not in templates:
            templates.append(lic_template)

    # Final sanity: resolve missing templates (e.g., unresolved license placeholders) before applying
    cleaned = []
    for t in templates:
        try:
            engine._find_template_src(t, None)
            cleaned.append(t)
        except FileNotFoundError:
            # try to resolve license placeholders to an actual sub-template
            if t.startswith("licenses/"):
                lname = t.split("/", 1)[1].lower()
                license_roots = []
                if (engine.user_templates_root / "licenses").exists():
                    license_roots.append(engine.user_templates_root / "licenses")
                if (engine.package_templates_root / "licenses").exists():
                    license_roots.append(engine.package_templates_root / "licenses")
                matches = []
                for root in license_roots:
                    for child in root.iterdir():
                        if child.is_dir() and lname in child.name.lower():
                            matches.append(f"licenses/{child.name}")
                if matches:
                    cleaned.append(matches[0])
                    click.echo(f"Resolved '{t}' to '{matches[0]}'")
                    continue
            click.echo(
                f"Template '{t}' not found in provided templates dir, user templates, or package templates"
            )
            raise SystemExit(1)

    for t in cleaned:
        click.echo(f"Applying template: {t}")
        try:
            if dry_run and as_json:
                preview = engine.preview_apply(
                    t, dest, metadata, force=force, templates_dir=None
                )
                all_actions.extend(preview)
                for e in preview:
                    click.echo(f"  {e['action']}: {e['path']}")
            else:
                for path, status in engine.apply_template(
                    t,
                    dest,
                    metadata,
                    force=force,
                    dry_run=dry_run,
                    atomic=True,
                    merge=merge_strategy,
                    verify=verify_integrity,
                    only_files=only_list,
                    except_files=exclude_list,
                ):
                    click.echo(f"  {status}: {path}")
        except FileNotFoundError as e:
            click.echo(str(e))
            raise SystemExit(1)
        except Exception as e:
            click.echo(f"ERROR applying template {t}: {e}")
            raise SystemExit(1)
    if dry_run and as_json:
        import json

        click.echo(json.dumps(all_actions))
        return
    click.echo("Done.")


@cli.command("list-templates")
@click.option("--json", "as_json", is_flag=True, help="Output templates as JSON array")
@click.option(
    "--templates-dir", default=None, help="Optional templates root to include"
)
@click.option(
    "--details", is_flag=True, help="Show subfiles contained in each template"
)
def list_templates(as_json, templates_dir, details):
    """List available templates"""
    engine = Engine()
    if templates_dir:
        engine = Engine(user_templates_root=templates_dir)
    info = engine.list_templates_info()
    ts = [name for name, src in info]
    if as_json:
        import json

        click.echo(json.dumps(ts))
        return
    click.echo("Available templates:")
    for i, (name, src) in enumerate(info, start=1):
        marker = "(user)" if src == "user" else ""
        click.echo(f"  {i}. {name} {marker}")
        if details:
            try:
                files = engine.get_template_files(name)
                for f in files:
                    click.echo(f"      - {f}")
            except Exception:
                click.echo("      (could not list files)")


@cli.command("add-templates")
@click.argument("project_path")
@click.option(
    "--templates", default="", help="Comma separated templates to add (default: prompt)"
)
@click.option(
    "--templates-dir",
    default=None,
    help="Optional templates root to use for this command",
)
@click.option(
    "--license",
    "license_id",
    default=None,
    help="License identifier to include (e.g., MIT, Apache-2.0)",
)
@click.option("--author", default=None)
@click.option("--email", default=None)
@click.option(
    "--github-username", default=None, help="GitHub username to populate templates"
)
@click.option(
    "--meta",
    multiple=True,
    help="Additional metadata as KEY=VAL; can be passed multiple times",
)
@click.option("--force", is_flag=True)
@click.option(
    "--dry-run",
    "dry_run",
    is_flag=True,
    help="Show planned actions but do not write files",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output machine-readable JSON when used with --dry-run",
)
@click.option(
    "--merge",
    "merge_strategy",
    type=click.Choice(["append", "prepend", "marker", "patch"]),
    default=None,
    help="Merge strategy to use when target file exists",
)
@click.option(
    "--only",
    "only_files",
    default=None,
    help="Comma-separated list of relative template file paths to include (default: all)",
)
@click.option(
    "--except",
    "exclude_files",
    default=None,
    help="Comma-separated list of relative template file paths to exclude",
)
@click.option(
    "--verify",
    "verify_integrity",
    is_flag=True,
    help="Verify template integrity using bldrx-manifest.json before applying",
)
@click.pass_context
def add_templates(
    ctx,
    project_path,
    templates,
    templates_dir,
    author,
    email,
    github_username,
    meta,
    force,
    dry_run,
    as_json,
    merge_strategy,
    only_files,
    exclude_files,
    verify_integrity,
    license_id,
):
    """Inject templates into existing project"""
    engine = Engine()
    dest = Path(project_path)
    if not dest.exists():
        click.echo(f"Destination {dest} does not exist")
        raise SystemExit(1)
    if not templates:
        # If a license is provided, use it as the chosen template to avoid interactive prompt
        if license_id:
            templates = f"licenses/{license_id}"
        else:
            available = engine.list_templates()
            click.echo("Available templates:")
            for i, t in enumerate(available, start=1):
                click.echo(f"  {i}. {t}")
            chosen = click.prompt(
                "Select a comma-separated list of templates by name", default=""
            )
            templates = chosen
    templates = [t.strip() for t in templates.split(",") if t.strip()]
    metadata = {
        "project_name": dest.name,
        "author_name": author or "",
        "email": email or "",
        "github_username": github_username or "",
    }
    # Attach developer metadata if global flag set
    if ctx.obj.get("developer_metadata"):
        metadata["developer"] = True
        metadata["bldrx_version"] = __version__
        metadata["dev_timestamp"] = datetime.utcnow().isoformat() + "Z"
    # parse extra metadata
    for item in meta:
        if "=" in item:
            k, v = item.split("=", 1)
            metadata[k.strip()] = v.strip()
    all_actions = []

    def _parse_csv(s):
        if not s:
            return None
        return [p.strip().replace("\\", "/") for p in s.split(",") if p.strip()]

    only_list = _parse_csv(only_files)
    exclude_list = _parse_csv(exclude_files)

    # Inject license template if requested
    if license_id:
        lic_template = f"licenses/{license_id}"
        # validate and fuzzy match against available templates when necessary
        # gather actual license subtemplates from templates dir, user templates, and package templates
        license_roots = []
        if templates_dir:
            td_licenses = Path(templates_dir) / "licenses"
            if td_licenses.exists():
                license_roots.append(td_licenses)
        if (engine.user_templates_root / "licenses").exists():
            license_roots.append(engine.user_templates_root / "licenses")
        if (engine.package_templates_root / "licenses").exists():
            license_roots.append(engine.package_templates_root / "licenses")
        available = []
        for root in license_roots:
            for child in root.iterdir():
                if child.is_dir():
                    available.append(f"licenses/{child.name}")
        available = sorted(set(available))
        # Replace any placeholder in `templates` with the resolved `lic_template` and de-duplicate
        placeholder = f"licenses/{license_id}"
        templates = [(lic_template if t == placeholder else t) for t in templates]
        seen = set()
        new_templates = []
        for t in templates:
            if t not in seen:
                new_templates.append(t)
                seen.add(t)
        templates = new_templates
        if lic_template not in available:
            lname = license_id.lower()
            matches = [
                t
                for t in available
                if t.startswith("licenses/") and lname in t.split("/", 1)[1].lower()
            ]
            if len(matches) >= 1:
                if len(matches) > 1:
                    click.echo(
                        f"Multiple license templates match '{license_id}'; choosing first match: {matches[0]}"
                    )
                lic_template = matches[0]
                click.echo(f"Using license template: {lic_template}")
            else:
                license_names = [
                    t.split("/", 1)[1] for t in available if t.startswith("licenses/")
                ]
                click.echo(
                    f"License '{license_id}' not found. Available licenses: {', '.join(license_names)}"
                )
                raise SystemExit(1)
        if lic_template not in templates:
            templates.append(lic_template)

    # Final sanity: resolve missing templates (e.g., unresolved license placeholders) before applying
    cleaned = []
    for t in templates:
        try:
            engine._find_template_src(t, templates_dir)
            cleaned.append(t)
        except FileNotFoundError:
            # try to resolve license placeholders to an actual sub-template
            if t.startswith("licenses/"):
                lname = t.split("/", 1)[1].lower()
                license_roots = []
                if templates_dir:
                    td_licenses = Path(templates_dir) / "licenses"
                    if td_licenses.exists():
                        license_roots.append(td_licenses)
                if (engine.user_templates_root / "licenses").exists():
                    license_roots.append(engine.user_templates_root / "licenses")
                if (engine.package_templates_root / "licenses").exists():
                    license_roots.append(engine.package_templates_root / "licenses")
                matches = []
                for root in license_roots:
                    for child in root.iterdir():
                        if child.is_dir() and lname in child.name.lower():
                            matches.append(f"licenses/{child.name}")
                if matches:
                    cleaned.append(matches[0])
                    click.echo(f"Resolved '{t}' to '{matches[0]}'")
                    continue
            click.echo(
                f"Template '{t}' not found in provided templates dir, user templates, or package templates"
            )
            raise SystemExit(1)

    for t in cleaned:
        click.echo(f"Applying template: {t}")
        try:
            if dry_run and as_json:
                preview = engine.preview_apply(
                    t, dest, metadata, force=force, templates_dir=templates_dir
                )
                all_actions.extend(preview)
                for e in preview:
                    click.echo(f"  {e['action']}: {e['path']}")
            else:
                for path, status in engine.apply_template(
                    t,
                    dest,
                    metadata,
                    force=force,
                    dry_run=dry_run,
                    templates_dir=templates_dir,
                    atomic=True,
                    merge=merge_strategy,
                    only_files=only_list,
                    except_files=exclude_list,
                ):
                    click.echo(f"  {status}: {path}")
        except FileNotFoundError as e:
            click.echo(str(e))
            raise SystemExit(1)
        except Exception as e:
            click.echo(f"ERROR applying template {t}: {e}")
            raise SystemExit(1)
    if dry_run and as_json:
        import json

        click.echo(json.dumps(all_actions))
        return
    click.echo("Done.")


@cli.command("remove-template")
@click.argument("project_path")
@click.argument("template_name")
@click.option(
    "--templates-dir",
    default=None,
    help="Optional templates root to use for this command",
)
@click.option(
    "--yes", is_flag=True, help="Confirm removal without prompt (implies removal)"
)
@click.option(
    "--force",
    is_flag=True,
    help="Actually delete files (must be used or --yes to perform removal)",
)
@click.option(
    "--dry-run",
    "dry_run",
    is_flag=True,
    help="Show planned removal without deleting files",
)
def remove_template(project_path, template_name, templates_dir, yes, force, dry_run):
    """Remove a template's files from a project (dangerous; uses --yes or --force to proceed)"""
    engine = Engine()
    dest = Path(project_path)
    if not dest.exists():
        click.echo(f"Destination {dest} does not exist")
        raise SystemExit(1)
    # if --yes provided, treat it as confirmation to remove (implies --force)
    if yes:
        force = True
    if not yes and not force and not dry_run:
        confirm = click.confirm(
            f"Are you sure you want to remove template '{template_name}' from {dest}?"
        )
        if not confirm:
            click.echo("Aborted.")
            raise SystemExit(1)
    for path, status in engine.remove_template(
        template_name, dest, force=force, dry_run=dry_run, templates_dir=templates_dir
    ):
        click.echo(f"  {status}: {path}")
    click.echo("Done.")


@cli.command("install-template")
@click.argument("src_path")
@click.option(
    "--name",
    default=None,
    help="Name to install the template as (default: directory name)",
)
@click.option(
    "--wrap",
    "wrap_root",
    is_flag=True,
    help="Preserve the source top-level folder when installing (wrap contents in that folder)",
)
@click.option("--force", is_flag=True, help="Overwrite if the template exists")
def install_template(src_path, name, wrap_root, force):
    """Install a template into the user templates directory. If `--name` is omitted an interactive prompt will ask for a name.

    By default the contents of `src_path` are installed as the template (content-only). Use `--wrap` to preserve the top-level folder
    from `src_path` as the root inside the installed template (useful when installing a `.github` directory and wanting to keep it at apply time).
    """
    engine = Engine()
    src = Path(src_path)
    if not src.exists() or not src.is_dir():
        click.echo(f"Source template path '{src}' not found or is not a directory")
        raise SystemExit(1)
    # Interactive name prompt if not provided
    if not name:
        default_name = src.name
        name = click.prompt("Template name to install as", default=default_name)
    dest = engine.user_templates_root / name
    if dest.exists() and not force:
        click.echo(f"Template '{name}' already exists in user templates")
        if not click.confirm("Overwrite existing template?"):
            # allow user to provide a different name
            new_name = click.prompt(
                "Provide a new name (leave blank to cancel)", default=""
            )
            if not new_name:
                click.echo("Aborted.")
                raise SystemExit(1)
            name = new_name
    try:
        dest = engine.install_user_template(
            Path(src_path), name=name, force=True, wrap=wrap_root
        )
        click.echo(f"Installed template to: {dest}")
    except Exception as e:
        click.echo(str(e))
        raise SystemExit(1)


@cli.command("uninstall-template")
@click.argument("name")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def uninstall_template(name, yes):
    """Remove a template from the user templates directory"""
    engine = Engine()
    if not yes:
        confirm = click.confirm(
            f"Are you sure you want to remove the user template '{name}'?"
        )
        if not confirm:
            click.echo("Aborted.")
            raise SystemExit(1)
    try:
        engine.uninstall_user_template(name)
        click.echo(f"Removed user template: {name}")
    except Exception as e:
        click.echo(str(e))
        raise SystemExit(1)


@cli.group("plugin")
def plugin_group():
    """Plugin management: install/list/remove plugins"""
    pass


@cli.group("telemetry")
def telemetry_group():
    """Telemetry opt-in controls"""
    pass


@telemetry_group.command("enable")
def telemetry_enable():
    from .telemetry import enable

    enable()
    click.echo("Telemetry enabled (BLDRX_ENABLE_TELEMETRY=1)")


@telemetry_group.command("disable")
def telemetry_disable():
    from .telemetry import disable

    disable()
    click.echo("Telemetry disabled")


@telemetry_group.command("status")
def telemetry_status():
    import json

    from .telemetry import status

    click.echo(json.dumps(status(), indent=2))


@plugin_group.command("install")
@click.argument("src_path")
@click.option("--name", default=None, help="Optional name to install the plugin as")
@click.option("--force", is_flag=True, help="Overwrite existing plugin")
def plugin_install(src_path, name, force):
    engine = Engine()
    try:
        dest = engine.plugin_manager.install_plugin(
            Path(src_path), name=name, force=force
        )
        click.echo(f"Installed plugin: {dest}")
    except Exception as e:
        click.echo(str(e))
        raise SystemExit(1)


@plugin_group.command("list")
def plugin_list():
    engine = Engine()
    pls = engine.plugin_manager.list_plugins()
    for p in pls:
        click.echo(p)


@plugin_group.command("remove")
@click.argument("name")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def plugin_remove(name, yes):
    engine = Engine()
    if not yes:
        confirm = click.confirm(f"Are you sure you want to remove plugin '{name}'?")
        if not confirm:
            click.echo("Aborted.")
            raise SystemExit(1)
    try:
        engine.plugin_manager.remove_plugin(name)
        click.echo(f"Removed plugin: {name}")
    except Exception as e:
        click.echo(str(e))
        raise SystemExit(1)


@cli.group("manifest")
def manifest_group():
    """Manifest generation and registry helpers"""
    pass


@manifest_group.command("create")
@click.argument("template_name")
@click.option(
    "--templates-dir",
    default=None,
    help="Optional templates root to use for this command",
)
@click.option(
    "--output",
    default=None,
    help="Path to write manifest (defaults to template root `bldrx-manifest.json`)",
)
@click.option(
    "--sign",
    "do_sign",
    is_flag=True,
    help="Include HMAC-SHA256 signature using BLDRX_MANIFEST_KEY or provided --key",
)
@click.option("--key", default=None, help="Explicit HMAC key to use for signing")
def manifest_create(template_name, templates_dir, output, do_sign, key):
    """Create a `bldrx-manifest.json` for the given template"""
    engine = Engine()
    try:
        manifest = engine.generate_manifest(
            template_name,
            templates_dir=templates_dir,
            write=bool(output is None),
            out_path=Path(output) if output else None,
            sign=do_sign,
            key=key,
        )
        click.echo("Manifest generated:")
        import json

        click.echo(json.dumps(manifest, indent=2))
    except Exception as e:
        click.echo(str(e))
        raise SystemExit(1)


@cli.group("catalog")
def catalog_group():
    """Template catalog (publish/search/info/remove)"""
    pass


@catalog_group.command("publish")
@click.argument("src")
@click.option("--name", default=None)
@click.option("--version", default="0.0.0")
@click.option("--description", default="")
@click.option("--tags", default="", help="Comma-separated tags")
@click.option(
    "--sign",
    "do_sign",
    is_flag=True,
    help="Sign manifest with HMAC using BLDRX_MANIFEST_KEY or --key",
)
@click.option("--key", default=None, help="Explicit HMAC key to use for signing")
@click.option("--force", is_flag=True, help="Overwrite existing catalog entry")
def catalog_publish(src, name, version, description, tags, do_sign, key, force):
    from .registry import Registry

    r = Registry()
    try:
        meta = r.publish(
            Path(src),
            name=name,
            version=version,
            description=description,
            tags=[t for t in tags.split(",") if t],
            force=force,
            sign=do_sign,
            key=key,
        )
        import json

        click.echo("Published:")
        click.echo(json.dumps(meta, indent=2))
    except Exception as e:
        import traceback

        click.echo(f"ERROR: {type(e).__name__}: {e}")
        click.echo("".join(traceback.format_exception(e, e, e.__traceback__)))
        raise SystemExit(1)


@catalog_group.command("search")
@click.argument("query", default="", required=False)
def catalog_search(query):
    from .registry import Registry

    r = Registry()
    res = r.search(query)
    import json

    click.echo(json.dumps(res, indent=2))


@catalog_group.command("info")
@click.argument("name")
@click.option("--version", default=None)
def catalog_info(name, version):
    from .registry import Registry

    r = Registry()
    try:
        e = r.get(name, version=version)
        import json

        click.echo(json.dumps(e, indent=2))
    except KeyError as ke:
        click.echo(str(ke))
        raise SystemExit(1)


@catalog_group.command("remove")
@click.argument("name")
@click.option("--version", default=None)
@click.option("--yes", is_flag=True, help="Skip confirmation")
def catalog_remove(name, version, yes):
    if not yes:
        confirm = click.confirm(
            f"Are you sure you want to remove catalog entry '{name}'{' version '+version if version else ''}?"
        )
        if not confirm:
            click.echo("Aborted.")
            raise SystemExit(1)
    from .registry import Registry

    r = Registry()
    try:
        removed = r.remove(name, version=version)
        import json

        click.echo(json.dumps(removed, indent=2))
    except KeyError as ke:
        click.echo(str(ke))
        raise SystemExit(1)


@cli.command("preview-template")
@click.argument("template_name")
@click.option(
    "--file",
    "file_path",
    default=None,
    help="Relative template file path to preview (e.g., README.md.j2)",
)
@click.option(
    "--render",
    "do_render",
    is_flag=True,
    help="Render the template with provided metadata",
)
@click.option(
    "--diff", "show_diff", is_flag=True, help="Show unified diffs of what would change"
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output machine-readable JSON for automation",
)
@click.option("--meta", multiple=True, help="Metadata KEY=VAL to use when rendering")
@click.option(
    "--templates-dir",
    default=None,
    help="Optional templates root to use for this command",
)
@click.option(
    "--templates-root", default=None, help="(deprecated) alias for --templates-dir"
)
@click.option(
    "--only",
    "only_files",
    default=None,
    help="Comma-separated list of relative template file paths to include (default: all)",
)
@click.option(
    "--except",
    "exclude_files",
    default=None,
    help="Comma-separated list of relative template file paths to exclude",
)
def preview_template(
    template_name,
    file_path,
    do_render,
    show_diff,
    as_json,
    meta,
    templates_dir,
    templates_root,
    only_files,
    exclude_files,
):
    """Preview template file contents or rendered output"""
    engine = Engine()
    # allow overriding templates dir for this command
    td = templates_dir or templates_root
    if td:
        engine = Engine(user_templates_root=td)
    try:
        metadata = {}
        for item in meta:
            if "=" in item:
                k, v = item.split("=", 1)
                metadata[k.strip()] = v.strip()

        def _parse_csv(s):
            if not s:
                return None
            return [p.strip().replace("\\", "/") for p in s.split(",") if p.strip()]

        only_list = _parse_csv(only_files)
        exclude_list = _parse_csv(exclude_files)

        if do_render and show_diff:
            # show diffs for the target project root (default: current dir)
            # Use apply_template with dry_run to respect filters (only/except)
            preview = list(
                engine.apply_template(
                    template_name,
                    Path("."),
                    metadata,
                    force=False,
                    dry_run=True,
                    templates_dir=td,
                    atomic=False,
                    merge=None,
                    only_files=only_list,
                    except_files=exclude_list,
                )
            )
            if as_json:
                import json

                # convert to preview style
                out = []
                for p, status in preview:
                    entry = {"path": p, "action": status}
                    out.append(entry)
                click.echo(json.dumps(out))
            else:
                for p, status in preview:
                    click.echo(f"{status}: {p}")
            return
        if not file_path:
            files = engine.get_template_files(
                template_name, templates_dir=templates_dir
            )
            click.echo("Files in template:")
            for f in files:
                click.echo(f"  - {f}")
            return
        if do_render:
            rendered = engine.render_template_file(
                template_name, file_path, metadata, templates_dir=templates_dir
            )
            click.echo(rendered)
        else:
            # show raw content
            src = engine._find_template_src(template_name, templates_dir)
            target = src / file_path
            if not target.exists():
                click.echo(f"File not found: {file_path}")
                raise SystemExit(1)
            click.echo(target.read_text(encoding="utf-8"))
    except Exception as e:
        click.echo(str(e))
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
