import click
from pathlib import Path
from .engine import Engine

@click.group()
def cli():
    """bldrx - project scaffold & template injector"""
    pass

@cli.command()
@click.argument('project_name')
@click.option('--templates', default='', help='Comma separated templates to include (default: based on --type)')
@click.option('--type', 'project_type', type=click.Choice(['python-cli','python-lib','node-api','react-app']), default=None, help='Project type; used to choose default templates')
@click.option('--author', default=None)
@click.option('--email', default=None)
@click.option('--github-username', default=None, help='GitHub username to populate templates')
@click.option('--meta', multiple=True, help='Additional metadata as KEY=VAL; can be passed multiple times')
@click.option('--force', is_flag=True)
@click.option('--dry-run', 'dry_run', is_flag=True, help='Show planned actions but do not write files')
def new(project_name, templates, project_type, author, email, github_username, meta, force, dry_run):
    """Scaffold a new project"""
    engine = Engine()
    dest = Path(project_name)
    if dest.exists() and not force:
        click.echo(f"Destination {dest} already exists. Use --force to override.")
        raise SystemExit(1)
    # Determine templates: explicit --templates takes precedence; otherwise derive from project_type
    if templates:
        templates = [t.strip() for t in templates.split(',') if t.strip()]
    else:
        mapping = {
            'python-cli': ['python-cli'],
            'python-lib': ['python-cli'],
            'node-api': ['node-api'],
            'react-app': ['react-app']
        }
        if project_type is None:
            # interactive prompt fallback
            project_type = click.prompt('Project type', type=click.Choice(list(mapping.keys())), default='python-cli')
        templates = mapping.get(project_type, ['python-cli'])
    # Build metadata
    metadata = {
        'project_name': project_name,
        'author_name': author or '',
        'email': email or '',
        'github_username': github_username or ''
    }
    # parse extra metadata KEY=VAL
    for item in meta:
        if '=' in item:
            k, v = item.split('=', 1)
            metadata[k.strip()] = v.strip()
    for t in templates:
        click.echo(f"Applying template: {t}")
        for path, status in engine.apply_template(t, dest, metadata, force=force, dry_run=dry_run):
            click.echo(f"  {status}: {path}")
    click.echo('Done.')

@cli.command('list-templates')
@click.option('--json', 'as_json', is_flag=True, help='Output templates as JSON array')
@click.option('--templates-dir', default=None, help='Optional templates root to include')
@click.option('--details', is_flag=True, help='Show subfiles contained in each template')
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
    click.echo('Available templates:')
    for i, (name, src) in enumerate(info, start=1):
        marker = '(user)' if src == 'user' else ''
        click.echo(f"  {i}. {name} {marker}")
        if details:
            try:
                files = engine.get_template_files(name)
                for f in files:
                    click.echo(f"      - {f}")
            except Exception:
                click.echo('      (could not list files)')

@cli.command('add-templates')
@click.argument('project_path')
@click.option('--templates', default='', help='Comma separated templates to add (default: prompt)')
@click.option('--templates-dir', default=None, help='Optional templates root to use for this command')
@click.option('--author', default=None)
@click.option('--email', default=None)
@click.option('--github-username', default=None, help='GitHub username to populate templates')
@click.option('--meta', multiple=True, help='Additional metadata as KEY=VAL; can be passed multiple times')
@click.option('--force', is_flag=True)
@click.option('--dry-run', 'dry_run', is_flag=True, help='Show planned actions but do not write files')
def add_templates(project_path, templates, templates_dir, author, email, github_username, meta, force, dry_run):
    """Inject templates into existing project"""
    engine = Engine()
    dest = Path(project_path)
    if not dest.exists():
        click.echo(f"Destination {dest} does not exist")
        raise SystemExit(1)
    if not templates:
        available = engine.list_templates()
        click.echo('Available templates:')
        for i, t in enumerate(available, start=1):
            click.echo(f"  {i}. {t}")
        chosen = click.prompt('Select a comma-separated list of templates by name', default='')
        templates = chosen
    templates = [t.strip() for t in templates.split(',') if t.strip()]
    metadata = {
        'project_name': dest.name,
        'author_name': author or '',
        'email': email or '',
        'github_username': github_username or ''
    }
    # parse extra metadata
    for item in meta:
        if '=' in item:
            k, v = item.split('=', 1)
            metadata[k.strip()] = v.strip()
    for t in templates:
        click.echo(f"Applying template: {t}")
        for path, status in engine.apply_template(t, dest, metadata, force=force, dry_run=dry_run, templates_dir=templates_dir):
            click.echo(f"  {status}: {path}")
    click.echo('Done.')

@cli.command('remove-template')
@click.argument('project_path')
@click.argument('template_name')
@click.option('--templates-dir', default=None, help='Optional templates root to use for this command')
@click.option('--yes', is_flag=True, help='Confirm removal without prompt (implies removal)')
@click.option('--force', is_flag=True, help='Actually delete files (must be used or --yes to perform removal)')
@click.option('--dry-run', 'dry_run', is_flag=True, help='Show planned removal without deleting files')
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
        confirm = click.confirm(f"Are you sure you want to remove template '{template_name}' from {dest}?")
        if not confirm:
            click.echo('Aborted.')
            raise SystemExit(1)
    for path, status in engine.remove_template(template_name, dest, force=force, dry_run=dry_run, templates_dir=templates_dir):
        click.echo(f"  {status}: {path}")
    click.echo('Done.')

@cli.command('install-template')
@click.argument('src_path')
@click.option('--name', default=None, help='Name to install the template as (default: directory name)')
@click.option('--wrap', 'wrap_root', is_flag=True, help='Preserve the source top-level folder when installing (wrap contents in that folder)')
@click.option('--force', is_flag=True, help='Overwrite if the template exists')
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
        name = click.prompt('Template name to install as', default=default_name)
    dest = engine.user_templates_root / name
    if dest.exists() and not force:
        click.echo(f"Template '{name}' already exists in user templates")
        if not click.confirm('Overwrite existing template?'):
            # allow user to provide a different name
            new_name = click.prompt('Provide a new name (leave blank to cancel)', default='')
            if not new_name:
                click.echo('Aborted.')
                raise SystemExit(1)
            name = new_name
    try:
        dest = engine.install_user_template(Path(src_path), name=name, force=True, wrap=wrap_root)
        click.echo(f"Installed template to: {dest}")
    except Exception as e:
        click.echo(str(e))
        raise SystemExit(1)

@cli.command('uninstall-template')
@click.argument('name')
@click.option('--yes', is_flag=True, help='Skip confirmation')
def uninstall_template(name, yes):
    """Remove a template from the user templates directory"""
    engine = Engine()
    if not yes:
        confirm = click.confirm(f"Are you sure you want to remove the user template '{name}'?")
        if not confirm:
            click.echo('Aborted.')
            raise SystemExit(1)
    try:
        engine.uninstall_user_template(name)
        click.echo(f"Removed user template: {name}")
    except Exception as e:
        click.echo(str(e))
        raise SystemExit(1)

@cli.command('preview-template')
@click.argument('template_name')
@click.option('--file', 'file_path', default=None, help='Relative template file path to preview (e.g., README.md.j2)')
@click.option('--render', 'do_render', is_flag=True, help='Render the template with provided metadata')
@click.option('--diff', 'show_diff', is_flag=True, help='Show unified diffs of what would change')
@click.option('--json', 'as_json', is_flag=True, help='Output machine-readable JSON for automation')
@click.option('--meta', multiple=True, help='Metadata KEY=VAL to use when rendering')
@click.option('--templates-dir', default=None, help='Optional templates root to use for this command')
def preview_template(template_name, file_path, do_render, show_diff, as_json, meta, templates_dir):
    """Preview template file contents or rendered output"""
    engine = Engine()
    # allow overriding templates dir for this command
    if templates_dir:
        engine = Engine(user_templates_root=templates_dir)
    try:
        metadata = {}
        for item in meta:
            if '=' in item:
                k, v = item.split('=', 1)
                metadata[k.strip()] = v.strip()
        if do_render and show_diff:
            # show diffs for the target project root (default: current dir)
            preview = engine.preview_template(template_name, Path('.'), metadata, templates_dir=templates_dir, diff=True)
            if as_json:
                import json
                click.echo(json.dumps(preview))
            else:
                for e in preview:
                    click.echo(f"{e['action']}: {e['path']}")
                    if 'diff' in e:
                        click.echo(e['diff'])
            return
        if not file_path:
            files = engine.get_template_files(template_name, templates_dir=templates_dir)
            click.echo('Files in template:')
            for f in files:
                click.echo(f"  - {f}")
            return
        if do_render:
            rendered = engine.render_template_file(template_name, file_path, metadata, templates_dir=templates_dir)
            click.echo(rendered)
        else:
            # show raw content
            src = engine._find_template_src(template_name, templates_dir)
            target = src / file_path
            if not target.exists():
                click.echo(f"File not found: {file_path}")
                raise SystemExit(1)
            click.echo(target.read_text(encoding='utf-8'))
    except Exception as e:
        click.echo(str(e))
        raise SystemExit(1)
if __name__ == '__main__':
    cli()