from pathlib import Path
import json
from datetime import datetime
import shutil
import os


def _default_registry_dir() -> Path:
    if os.name == 'nt':
        appdata = os.getenv('APPDATA') or Path.home()
        return Path(appdata) / 'bldrx' / 'registry'
    else:
        return Path.home() / '.bldrx' / 'registry'


class Registry:
    def __init__(self, root: Path = None):
        env = os.getenv('BLDRX_REGISTRY_DIR')
        if root:
            self.root = Path(root)
        elif env:
            self.root = Path(env)
        else:
            self.root = _default_registry_dir()
        self.root.mkdir(parents=True, exist_ok=True)

    def _entry_path(self, name: str, version: str):
        safe_name = name.replace(' ', '_')
        return self.root / f"{safe_name}-{version}.json"

    def publish(self, src: Path, name: str = None, version: str = '0.0.0', description: str = '', tags: list = None, force: bool = False, sign: bool = False, key: str = None):
        src = Path(src)
        if not src.exists():
            raise FileNotFoundError(f"Source '{src}' not found")
        # compute manifest
        files = {}
        import hashlib, hmac
        for p in src.rglob('*'):
            if p.is_dir():
                continue
            rel = str(p.relative_to(src)).replace('\\', '/')
            h = hashlib.sha256()
            h.update(p.read_bytes())
            files[rel] = h.hexdigest()
        manifest = {'files': files}
        if sign:
            use_key = key or os.getenv('BLDRX_MANIFEST_KEY')
            if not use_key:
                raise RuntimeError('Signing requested but no key provided via `key` or BLDRX_MANIFEST_KEY')
            canonical = json.dumps({'files': files}, sort_keys=True, separators=(',', ':')).encode('utf-8')
            manifest['hmac'] = hmac.new(use_key.encode('utf-8'), canonical, hashlib.sha256).hexdigest()
        meta = {
            'name': (name or src.name),
            'version': version,
            'description': description,
            'tags': tags or [],
            'manifest': manifest,
            'source': str(src.resolve()),
            'published_at': datetime.utcnow().isoformat() + 'Z'
        }
        path = self._entry_path(meta['name'], version)
        if path.exists() and not force:
            raise FileExistsError(f"Catalog entry already exists: {path}")
        path.write_text(json.dumps(meta, indent=2), encoding='utf-8')
        return meta

    def list_entries(self):
        out = []
        for p in sorted(self.root.iterdir()):
            if p.suffix == '.json':
                out.append(json.loads(p.read_text(encoding='utf-8')))
        return out

    def search(self, q: str = None):
        q = q or ''
        ql = q.lower()
        res = []
        for e in self.list_entries():
            if ql in e.get('name', '').lower() or ql in e.get('description', '').lower() or any(ql in t.lower() for t in e.get('tags', [])):
                res.append(e)
        return res

    def get(self, name: str, version: str = None):
        # if version provided, exact match; else first matching name
        for e in self.list_entries():
            if e.get('name') == name and (version is None or e.get('version') == version):
                return e
        raise KeyError(f"Catalog entry '{name}' not found")

    def remove(self, name: str, version: str = None):
        # remove matching entries; if version is None, remove all versions of name
        removed = []
        for p in list(self.root.iterdir()):
            if p.suffix != '.json':
                continue
            try:
                e = json.loads(p.read_text(encoding='utf-8'))
            except Exception:
                continue
            if e.get('name') == name and (version is None or e.get('version') == version):
                p.unlink()
                removed.append(e)
        if not removed:
            raise KeyError(f"Catalog entry '{name}'{' version '+version if version else ''} not found")
        return removed
