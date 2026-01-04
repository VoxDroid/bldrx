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

    def validate_template(self, template_name: str, templates_dir: Path = None):
        """Validate the template files for syntax errors and report undefined variables.

        Returns: {
            'syntax_errors': { relative_path: message },
            'undefined_variables': { relative_path: [varnames] }
        }
        """
        from jinja2 import Environment, FileSystemLoader, StrictUndefined, exceptions, meta
        src = self._find_template_src(template_name, templates_dir)
        res = {'syntax_errors': {}, 'undefined_variables': {}}
        env = Environment(loader=FileSystemLoader(str(src)), undefined=StrictUndefined)
        for p in src.rglob("*"):
            if p.is_dir():
                continue
            rel = p.relative_to(src)
            if p.suffix != '.j2':
                # raw files are not validated other than existence
                continue
            rel_path = str(rel).replace('\\', '/')
            text = p.read_text(encoding='utf-8')
            try:
                # parse to detect syntax errors
                parsed = env.parse(text)
            except exceptions.TemplateSyntaxError as e:
                res['syntax_errors'][rel_path] = str(e)
                continue
            # find undeclared variables used in template
            undef = meta.find_undeclared_variables(parsed)
            res['undefined_variables'][rel_path] = sorted(list(undef))
        return res

    def preview_template(self, template_name: str, dest: Path, metadata: dict, templates_dir: Path = None, diff: bool = False):
        """Return a preview list describing what would happen if the template were applied to `dest`.

        Each entry is a dict: {path: str, action: 'would-render'|'would-copy'|'skipped', diff: optional unified diff}
        """
        from difflib import unified_diff
        src = self._find_template_src(template_name, templates_dir)
        dest.mkdir(parents=True, exist_ok=True)
        out = []
        for p in src.rglob("*"):
            if p.is_dir():
                continue
            rel = p.relative_to(src)
            target = dest / rel
            if p.suffix == '.j2':
                out_path = target.with_suffix("")
                # render
                from jinja2 import Environment, FileSystemLoader, StrictUndefined
                rel_template_path = str(rel).replace('\\', '/')
                env = Environment(loader=FileSystemLoader(str(src)), undefined=StrictUndefined)
                tmpl = env.get_template(rel_template_path)
                new_text = tmpl.render(**{**metadata, 'year': datetime.now().year})
                if out_path.exists():
                    old_text = out_path.read_text(encoding='utf-8')
                    if old_text == new_text:
                        out.append({'path': str(out_path), 'action': 'skipped'})
                        continue
                    else:
                        entry = {'path': str(out_path), 'action': 'would-render'}
                        if diff:
                            d = '\n'.join(list(unified_diff(old_text.splitlines(), new_text.splitlines(), fromfile=str(out_path), tofile='(rendered)', lineterm='')))
                            entry['diff'] = d
                        out.append(entry)
                else:
                    entry = {'path': str(out_path), 'action': 'would-render'}
                    if diff:
                        d = '\n'.join(list(unified_diff([], new_text.splitlines(), fromfile='(empty)', tofile=str(out_path), lineterm='')))
                        entry['diff'] = d
                    out.append(entry)
            else:
                # raw file copy
                if target.exists():
                    old_text = target.read_text(encoding='utf-8')
                    new_text = p.read_text(encoding='utf-8')
                    if old_text == new_text:
                        out.append({'path': str(target), 'action': 'skipped'})
                        continue
                    else:
                        entry = {'path': str(target), 'action': 'would-copy'}
                        if diff:
                            d = '\n'.join(list(unified_diff(old_text.splitlines(), new_text.splitlines(), fromfile=str(target), tofile=str(p), lineterm='')))
                            entry['diff'] = d
                        out.append(entry)
                else:
                    entry = {'path': str(target), 'action': 'would-copy'}
                    if diff:
                        d = '\n'.join(list(unified_diff([], p.read_text(encoding='utf-8').splitlines(), fromfile='(empty)', tofile=str(target), lineterm='')))
                        entry['diff'] = d
                    out.append(entry)
        return out

    def preview_apply(self, template_name: str, dest: Path, metadata: dict, force: bool = False, templates_dir: Path = None):
        """Return a structured preview of applying the template (non-destructive).

        Each entry: {'path': str, 'action': 'would-render'|'would-copy'|'skipped'}
        """
        out = []
        for path, status in self.apply_template(template_name, dest, metadata, force=force, dry_run=True, templates_dir=templates_dir):
            out.append({'path': path, 'action': status})
        return out

    def verify_template(self, template_name: str, templates_dir: Path = None):
        """Verify template integrity based on a manifest file `bldrx-manifest.json`.

        Manifest format: {"files": {"rel/path": "sha256hex", ...},
                          "hmac": "hexhmac" (optional - HMAC-SHA256 over canonical files object)
                         }
        Returns: {
            'ok': bool,
            'mismatches': [relpaths],
            'missing': [relpaths],
            'manifest_missing': bool,
            'signature_present': bool,
            'signature_valid': True|False|None
        }
        """
        import json, hashlib, hmac, os
        src = self._find_template_src(template_name, templates_dir)
        manifest_path = src / 'bldrx-manifest.json'
        if not manifest_path.exists():
            return {'ok': True, 'mismatches': [], 'missing': [], 'manifest_missing': True, 'signature_present': False, 'signature_valid': None}
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        files = manifest.get('files', {})
        mismatches = []
        missing = []
        for rel, expected in files.items():
            fpath = src / rel
            if not fpath.exists():
                missing.append(rel)
                continue
            h = hashlib.sha256()
            h.update(fpath.read_bytes())
            actual = h.hexdigest()
            if actual != expected:
                mismatches.append(rel)
        # Optional HMAC signature verification (HMAC-SHA256)
        signature = manifest.get('hmac') or manifest.get('signature')
        signature_present = bool(signature)
        signature_valid = None
        if signature_present:
            key = os.getenv('BLDRX_MANIFEST_KEY')
            if not key:
                signature_valid = False
            else:
                canonical = json.dumps({'files': files}, sort_keys=True, separators=(',', ':')).encode('utf-8')
                expected_sig = hmac.new(key.encode('utf-8'), canonical, hashlib.sha256).hexdigest()
                signature_valid = hmac.compare_digest(expected_sig, signature)
        ok = (not mismatches) and (not missing) and (signature_valid is not False if signature_present else True)
        return {'ok': ok, 'mismatches': mismatches, 'missing': missing, 'manifest_missing': False, 'signature_present': signature_present, 'signature_valid': signature_valid}

    def apply_template(self, template_name: str, dest: Path, metadata: dict, force: bool = False, dry_run: bool = False, templates_dir: Path = None, backup: bool = False, git_commit: bool = False, git_message: str = None, atomic: bool = False, merge: str = None, verify: bool = False):
        """Apply the named template into `dest`.

        New options:
        - backup: if True, save overwritten files into `dest/.bldrx/backups/<timestamp>/...` before writing.
        - git_commit: if True and `dest` is a git repo, stage & commit changes after apply with `git_message`.
        - atomic: if True, perform per-file atomic replace with rollback on failure.
        - merge: optional strategy to handle existing files (append|prepend|marker|patch). If None, default behavior applies (skip or overwrite with force).
        - verify: if True, verify checksums using `bldrx-manifest.json` before applying; raise on mismatch.
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

        # Keep global state for atomic replacements so we can rollback across multiple files
        global_replaced = []  # list of (final_path, backup_path or None)
        global_new_created = []

        # Verify manifest if requested
        if verify:
            vres = self.verify_template(template_name, templates_dir=templates_dir)
            if not vres.get('ok'):
                raise RuntimeError(f"Template verification failed: mismatches={vres.get('mismatches')}, missing={vres.get('missing')}, signature_present={vres.get('signature_present')}, signature_valid={vres.get('signature_valid')}")

        # Walk files
        BINARY_SIZE_THRESHOLD = 1_000_000  # bytes; files larger than this are considered large and skipped unless forced
        for p in src.rglob("*"):
            rel = p.relative_to(src)
            target = dest / rel
            if p.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            # if it's a template file
            if p.suffix == ".j2":
                out_path = target.with_suffix("")
                # detect binary/non-utf8 template file
                raw = p.read_bytes()
                try:
                    raw.decode('utf-8')
                except Exception:
                    if dry_run:
                        yield (str(out_path), "would-skip-binary")
                    else:
                        yield (str(out_path), "skipped-binary")
                    continue
                if out_path.exists() and not force and not merge:
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

                # Merge handling: if merge strategy provided and target exists, compute merged text
                if merge and out_path.exists():
                    existing_text = out_path.read_text(encoding='utf-8')
                    if merge == 'append':
                        merged_text = existing_text.rstrip('\r\n') + '\n' + text
                    elif merge == 'prepend':
                        merged_text = text + '\n' + existing_text
                    elif merge == 'marker':
                        # use target filename (without .j2) as marker identifier
                        marker_name = out_path.name
                        start = f"<!-- bldrx:start:{marker_name} -->"
                        end = f"<!-- bldrx:end:{marker_name} -->"
                        if start in existing_text and end in existing_text:
                            pre, rest = existing_text.split(start, 1)
                            _, post = rest.split(end, 1)
                            merged_text = pre + start + '\n' + text + '\n' + end + post
                        else:
                            # fallback to append if no markers found
                            merged_text = existing_text.rstrip('\r\n') + '\n' + text
                    else:
                        # unknown merge strategy: fall back to overwrite
                        merged_text = text
                else:
                    merged_text = text

                # perform atomic write/replace if requested
                if atomic:
                    ts = datetime.now().strftime("%Y%m%d%H%M%S")
                    tmp_name = out_path.name + f".bldrx.tmp.{ts}"
                    tmp_path = out_path.parent / tmp_name
                    # write to temp file in same dir (ensures os.replace is atomic)
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    # write merged text if merge applied
                    tmp_path.write_text(merged_text, encoding="utf-8")
                    replaced = []  # list of tuples (final_path, backup_path or None)
                    new_created = []
                    try:
                        # backup existing if needed
                        if out_path.exists() and backup:
                            bpath = backups_root / out_path.relative_to(dest)
                            bpath.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(out_path, bpath)
                            replaced.append((out_path, bpath))
                            global_replaced.append((out_path, bpath))
                        else:
                            if out_path.exists():
                                replaced.append((out_path, None))
                                global_replaced.append((out_path, None))
                            else:
                                new_created.append(out_path)
                                global_new_created.append(out_path)
                        # atomic replace
                        os.replace(str(tmp_path), str(out_path))
                        made_changes = True
                        yield (str(out_path), "rendered")
                    except Exception as e:
                        # rollback across all files replaced so far
                        for fpath, bpath in global_replaced:
                            try:
                                if bpath is not None and bpath.exists():
                                    os.replace(str(bpath), str(fpath))
                            except Exception:
                                pass
                        for fpath in global_new_created:
                            try:
                                if fpath.exists():
                                    fpath.unlink()
                            except Exception:
                                pass
                        # cleanup temp
                        try:
                            if tmp_path.exists():
                                tmp_path.unlink()
                        except Exception:
                            pass
                        raise RuntimeError(f"Atomic replace failed for {out_path}: {e}")
                    finally:
                        # cleanup any leftover tmp files
                        try:
                            if tmp_path.exists():
                                tmp_path.unlink()
                        except Exception:
                            pass
                else:
                    # non-atomic path
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
                if target.exists() and not force and not merge:
                    yield (str(target), "skipped")
                    continue
                # detect large or binary raw files
                size = p.stat().st_size
                is_binary = False
                try:
                    with p.open('rb') as fh:
                        head = fh.read(1024)
                        if b"\x00" in head:
                            is_binary = True
                except Exception:
                    is_binary = True
                if (is_binary or size > BINARY_SIZE_THRESHOLD) and not force:
                    if dry_run:
                        yield (str(target), "would-skip-large" if size > BINARY_SIZE_THRESHOLD else "would-skip-binary")
                    else:
                        yield (str(target), "skipped-large" if size > BINARY_SIZE_THRESHOLD else "skipped-binary")
                    continue
                if dry_run:
                    yield (str(target), "would-copy")
                    continue
                if atomic:
                    ts = datetime.now().strftime("%Y%m%d%H%M%S")
                    tmp_name = target.name + f".bldrx.tmp.{ts}"
                    tmp_path = target.parent / tmp_name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, tmp_path)
                    replaced = []
                    new_created = []
                    try:
                        if target.exists() and backup:
                            bpath = backups_root / target.relative_to(dest)
                            bpath.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(target, bpath)
                            replaced.append((target, bpath))
                        else:
                            if target.exists():
                                replaced.append((target, None))
                            else:
                                new_created.append(target)
                        os.replace(str(tmp_path), str(target))
                        made_changes = True
                        yield (str(target), "copied")
                    except Exception as e:
                        for fpath, bpath in replaced:
                            try:
                                if bpath is not None and bpath.exists():
                                    os.replace(str(bpath), str(fpath))
                            except Exception:
                                pass
                        for fpath in new_created:
                            try:
                                if fpath.exists():
                                    fpath.unlink()
                            except Exception:
                                pass
                        try:
                            if tmp_path.exists():
                                tmp_path.unlink()
                        except Exception:
                            pass
                        raise RuntimeError(f"Atomic replace failed for {target}: {e}")
                    finally:
                        try:
                            if tmp_path.exists():
                                tmp_path.unlink()
                        except Exception:
                            pass
                else:
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

    def _acquire_lock(self, lock_path: Path, timeout: float = 5.0):
        """Acquire a simple file lock by creating a lockfile using O_EXCL.

        Raises RuntimeError on timeout.
        """
        import time, os
        deadline = time.time() + timeout if timeout is not None else None
        while True:
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                return
            except FileExistsError:
                if deadline is not None and time.time() > deadline:
                    raise RuntimeError(f"Could not acquire lock {lock_path} within {timeout} seconds")
                time.sleep(0.05)

    def _release_lock(self, lock_path: Path):
        try:
            if lock_path.exists():
                lock_path.unlink()
        except Exception:
            pass

    def install_user_template(self, src_path: Path, name: str = None, force: bool = False, wrap: bool = False, lock_timeout: float = 5.0):
        """Copy a template folder into the user templates directory.

        If `wrap` is False (default) the contents of `src_path` are copied into `user_templates/name`.
        If `wrap` is True the entire `src_path` folder is preserved under `user_templates/name/<src_basename>`.

        New option:
        - lock_timeout: seconds to wait to acquire a per-template install lock to avoid concurrent installs.
        """
        src = Path(src_path)
        if not src.exists() or not src.is_dir():
            raise FileNotFoundError(f"Source template path '{src}' not found or is not a directory")
        name = name or src.name
        base_dest = self.user_templates_root / name
        base_dest.parent.mkdir(parents=True, exist_ok=True)

        lock_path = base_dest.parent / f".{name}.lock"
        # acquire per-template lock
        self._acquire_lock(lock_path, timeout=lock_timeout)
        try:
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
        finally:
            # release lock always
            self._release_lock(lock_path)

    def uninstall_user_template(self, name: str, force: bool = False):
        dest = self.user_templates_root / name
        if not dest.exists():
            raise FileNotFoundError(f"User template '{name}' not found")
        shutil.rmtree(dest)
        return True

    def fetch_remote_template(self, url: str, name: str = None, force: bool = False, verify: bool = True):
        """Fetch a remote template archive or directory and install it into user templates.

        Supported sources for this MVP: local file paths and file:// URLs pointing to a directory, .tar.gz/.tgz or .zip archive.
        The archive is extracted into a sandbox (tempdir) and checked for path traversal attempts before installation.

        Params:
        - url: location to fetch (file:// or local path)
        - name: name to install the template as (defaults to archive/dir basename)
        - force: pass to `install_user_template` to overwrite existing
        - verify: if True, run manifest verification inside the sandbox before installing

        Returns: Path to installed template folder
        """
        import tempfile, tarfile, zipfile, urllib.parse
        src_path = None
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme == 'file':
            import urllib.request
            pathstr = urllib.request.url2pathname(parsed.path)
            src_path = Path(pathstr)
        else:
            # treat as local path fallback for now
            p = Path(url)
            if p.exists():
                src_path = p
            else:
                raise ValueError("Unsupported URL scheme or path not found: %s" % url)

        with tempfile.TemporaryDirectory() as td:
            tdpath = Path(td)
            # if it's a directory, copy its contents to temp dir
            if src_path.is_dir():
                # copytree to td/extracted
                dest_ex = tdpath / src_path.name
                shutil.copytree(src_path, dest_ex)
            else:
                # file: decide based on suffix
                if src_path.suffix in ('.gz', '.tgz') or src_path.name.endswith('.tar.gz'):
                    # extract tar safely
                    with tarfile.open(src_path, 'r:gz') as tf:
                        # safety check for path traversal
                        for member in tf.getmembers():
                            member_path = Path(member.name)
                            if member_path.is_absolute() or '..' in member_path.parts:
                                raise RuntimeError('Unsafe archive: path traversal detected')
                        tf.extractall(path=tdpath)
                elif src_path.suffix == '.zip':
                    with zipfile.ZipFile(src_path, 'r') as zf:
                        for fn in zf.namelist():
                            fpath = Path(fn)
                            if fpath.is_absolute() or '..' in fpath.parts:
                                raise RuntimeError('Unsafe archive: path traversal detected')
                        zf.extractall(path=tdpath)
                else:
                    raise ValueError('Unsupported archive format for: %s' % src_path)

            # Locate the extracted root dir (single child assumed or use tdpath itself)
            children = [p for p in tdpath.iterdir() if p.exists()]
            if len(children) == 1 and children[0].is_dir():
                extracted = children[0]
            else:
                # either multiple entries or a flat archive, use tdpath as root
                extracted = tdpath

            # Optionally verify manifest (perform local manifest checks inside the extracted sandbox)
            if verify:
                manifest_path = extracted / 'bldrx-manifest.json'
                if manifest_path.exists():
                    import json, hashlib
                    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
                    files = manifest.get('files', {})
                    mismatches = []
                    missing = []
                    for rel, expected in files.items():
                        fpath = extracted / rel
                        if not fpath.exists():
                            missing.append(rel)
                            continue
                        h = hashlib.sha256()
                        h.update(fpath.read_bytes())
                        actual = h.hexdigest()
                        if actual != expected:
                            mismatches.append(rel)
                    if mismatches or missing:
                        raise RuntimeError(f"Remote template verification failed: mismatches={mismatches}, missing={missing}")
                # if no manifest present we allow installation (but user may opt to require manifests later)

            # Install into user templates
            install_name = name or extracted.name
            # Use install_user_template to perform the copy into user templates
            dest = self.install_user_template(extracted, name=install_name, force=force)
            return dest
