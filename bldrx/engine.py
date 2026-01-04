import shutil
from pathlib import Path
from datetime import datetime
import os
import shutil
from .renderer import Renderer


def _default_user_templates_dir() -> Path:
    # Platform-aware default user templates location
    if os.name == 'nt':
        appdata = os.getenv('APPDATA') or Path.home()
        return Path(appdata) / 'bldrx' / 'templates'
    else:
        return Path.home() / '.bldrx' / 'templates'


class Engine:
    def __init__(self, templates_root: Path = None, user_templates_root: Path = None):
        # packaged templates root (inside the package)
        self.package_templates_root = templates_root or (Path(__file__).parent / "templates")
        # user templates root (outside the package)
        env = os.getenv('BLDRX_TEMPLATES_DIR')
        if user_templates_root:
            self.user_templates_root = Path(user_templates_root)
        elif env:
            self.user_templates_root = Path(env).expanduser()
        else:
            self.user_templates_root = _default_user_templates_dir()

        # Ensure user templates dir exists (but do NOT create it by default). It will be created on install-template.
        self.renderer = Renderer([str(self.user_templates_root), str(self.package_templates_root)])
        # backwards-compatible alias for older code/tests
        self.templates_root = self.package_templates_root

    def _find_template_src(self, template_name: str, templates_dir: Path = None) -> Path:
        """Resolve which template source to use (templates_dir override > user > package). Returns Path to template directory."""
        if templates_dir:
            candidate = Path(templates_dir) / template_name
            if candidate.exists():
                return candidate
            # if not found, continue to other sources
        candidate = self.user_templates_root / template_name
        if candidate.exists():
            return candidate
        candidate = self.package_templates_root / template_name
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f"Template '{template_name}' not found in provided templates dir, user templates, or package templates")

    def list_templates(self):
        """List template names available (user templates first)."""
        names = set()
        if self.user_templates_root.exists():
            for p in self.user_templates_root.iterdir():
                if p.is_dir():
                    names.add(p.name)
        if self.package_templates_root.exists():
            for p in self.package_templates_root.iterdir():
                if p.is_dir():
                    names.add(p.name)
        return sorted(names)

    def list_templates_info(self):
        """Return list of (name, source) pairs where source is 'user' or 'package'."""
        info = []
        if self.user_templates_root.exists():
            for p in self.user_templates_root.iterdir():
                if p.is_dir():
                    info.append((p.name, 'user'))
        if self.package_templates_root.exists():
            for p in self.package_templates_root.iterdir():
                if p.is_dir():
                    info.append((p.name, 'package'))
        # dedupe preserving user first
        seen = set()
        out = []
        for name, src in info:
            if name not in seen:
                out.append((name, src))
                seen.add(name)
        return out

    def get_template_files(self, template_name: str, templates_dir: Path = None):
        """Return a sorted list of file relative paths (strings) for a template."""
        src = self._find_template_src(template_name, templates_dir)
        files = []
        for p in src.rglob("*"):
            if p.is_file():
                files.append(str(p.relative_to(src)).replace('\\', '/'))
        return sorted(files)

    def render_template_file(self, template_name: str, file_path: str, metadata: dict, templates_dir: Path = None):
        """Render a single template file and return the rendered text. """
        src = self._find_template_src(template_name, templates_dir)
        target = src / file_path
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(f"Template file '{file_path}' not found in template '{template_name}'")
        # if it's a jinja template, render it, otherwise return raw text
        if target.suffix == '.j2':
            from jinja2 import Environment, FileSystemLoader, StrictUndefined
            rel_template_path = str(Path(file_path)).replace('\\', '/')
            env = Environment(loader=FileSystemLoader(str(src)), undefined=StrictUndefined)
            tmpl = env.get_template(rel_template_path)
            return tmpl.render(**{**metadata, 'year': datetime.now().year})
        else:
            return target.read_text(encoding='utf-8')

    def apply_template(self, template_name: str, dest: Path, metadata: dict, force: bool = False, dry_run: bool = False, templates_dir: Path = None, backup: bool = False, git_commit: bool = False, git_message: str = None):
        """Apply the named template into `dest`.

        New options:
        - backup: if True, save overwritten files into `dest/.bldrx/backups/<timestamp>/...` before writing.
        - git_commit: if True and `dest` is a git repo, stage & commit changes after apply with `git_message`.
        """
        import subprocess

        src = self._find_template_src(template_name, templates_dir)
        dest.mkdir(parents=True, exist_ok=True)

        # prepare backups root if requested
        backups_root = None
        if backup:
            ts = datetime.now().strftime("%Y%m%d%H%M%S")
            backups_root = dest / ".bldrx" / "backups" / f"{template_name}-{ts}"
            backups_root.mkdir(parents=True, exist_ok=True)

        made_changes = False

        # Walk files
        for p in src.rglob("*"):
            rel = p.relative_to(src)
            target = dest / rel
            if p.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            # if it's a template file
            if p.suffix == ".j2":
                out_path = target.with_suffix("")
                if out_path.exists() and not force:
                    yield (str(out_path), "skipped")
                    continue
                # Render using the selected template src as the loader root so that
                # template resolution uses the chosen source (user or package) rather than the global loader order
                from jinja2 import Environment, FileSystemLoader, StrictUndefined
                rel_template_path = str(rel).replace('\\', '/')
                env = Environment(loader=FileSystemLoader(str(src)), undefined=StrictUndefined)
                tmpl = env.get_template(rel_template_path)
                text = tmpl.render(**{**metadata, "year": datetime.now().year})
                if dry_run:
                    yield (str(out_path), "would-render")
                    continue
                # backup existing
                if out_path.exists() and backup:
                    bpath = backups_root / out_path.relative_to(dest)
                    bpath.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(out_path, bpath)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(text, encoding="utf-8")
                made_changes = True
                yield (str(out_path), "rendered")
            else:
                # raw file
                if target.exists() and not force:
                    yield (str(target), "skipped")
                    continue
                if dry_run:
                    yield (str(target), "would-copy")
                    continue
                # backup existing
                if target.exists() and backup:
                    bpath = backups_root / target.relative_to(dest)
                    bpath.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target, bpath)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, target)
                made_changes = True
                yield (str(target), "copied")

        # After all files applied, optionally commit to git
        if git_commit and made_changes:
            # Only attempt to commit if this appears to be a git repo
            git_dir = Path(dest) / ".git"
            if git_dir.exists():
                try:
                    subprocess.run(["git", "add", "-A"], cwd=str(dest), check=True, capture_output=True)
                    msg = git_message or f"bldrx: apply template {template_name}"
                    subprocess.run(["git", "commit", "-m", msg], cwd=str(dest), check=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    # surface a helpful error
                    raise RuntimeError(f"git commit failed: {e.stderr.decode() if hasattr(e, 'stderr') else e}")
            else:
                raise RuntimeError("git_commit requested but destination is not a git repository")

    def remove_template(self, template_name: str, dest: Path, force: bool = False, dry_run: bool = False, templates_dir: Path = None):
        """Remove files from dest that correspond to files in the template.
        By default does not delete files unless force=True. If dry_run is True, report would-remove without deleting."""
        src = self._find_template_src(template_name, templates_dir)
        for p in src.rglob("*"):
            if p.is_dir():
                continue
            rel = p.relative_to(src)
            target = dest / rel
            if p.suffix == ".j2":
                out_path = target.with_suffix("")
                if not out_path.exists():
                    yield (str(out_path), "missing")
                    continue
                if not force:
                    yield (str(out_path), "skipped")
                    continue
                if dry_run:
                    yield (str(out_path), "would-remove")
                    continue
                out_path.unlink()
                yield (str(out_path), "removed")
            else:
                if not target.exists():
                    yield (str(target), "missing")
                    continue
                if not force:
                    yield (str(target), "skipped")
                    continue
                if dry_run:
                    yield (str(target), "would-remove")
                    continue
                target.unlink()
                yield (str(target), "removed")

    def install_user_template(self, src_path: Path, name: str = None, force: bool = False, wrap: bool = False):
        """Copy a template folder into the user templates directory.

        If `wrap` is False (default) the contents of `src_path` are copied into `user_templates/name`.
        If `wrap` is True the entire `src_path` folder is preserved under `user_templates/name/<src_basename>`.
        """
        src = Path(src_path)
        if not src.exists() or not src.is_dir():
            raise FileNotFoundError(f"Source template path '{src}' not found or is not a directory")
        name = name or src.name
        base_dest = self.user_templates_root / name
        base_dest.parent.mkdir(parents=True, exist_ok=True)
        if base_dest.exists() and not force:
            raise FileExistsError(f"Template '{name}' already exists in user templates; use force=True to overwrite")
        # remove existing if force
        if base_dest.exists() and force:
            shutil.rmtree(base_dest)
        if wrap:
            dest = base_dest / src.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dest)
        else:
            # copy contents of src into base_dest
            base_dest.mkdir(parents=True, exist_ok=True)
            for p in src.iterdir():
                target = base_dest / p.name
                if p.is_dir():
                    shutil.copytree(p, target)
                else:
                    shutil.copy2(p, target)
        return base_dest

    def uninstall_user_template(self, name: str, force: bool = False):
        dest = self.user_templates_root / name
        if not dest.exists():
            raise FileNotFoundError(f"User template '{name}' not found")
        shutil.rmtree(dest)
        return True
