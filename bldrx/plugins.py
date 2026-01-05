from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path
from typing import Any, Optional


def _default_user_plugins_dir() -> Path:
    """Return the platform-appropriate default plugins directory as a Path."""
    import os

    if os.name == "nt":
        appdata = os.getenv("APPDATA") or Path.home()
        return Path(appdata) / "bldrx" / "plugins"
    else:
        return Path.home() / ".bldrx" / "plugins"


class PluginManager:
    """Manage installed plugins (install, list, remove, and load at runtime)."""

    def __init__(self, engine: Any, plugins_root: Optional[Path] = None):
        """Create a PluginManager bound to an Engine instance.

        Parameters:
        - engine: the Engine instance to pass to plugins' `register(engine)` entrypoint
        - plugins_root: optional Path for user plugins directory
        """
        self.engine = engine
        self.plugins_root = (
            Path(plugins_root) if plugins_root else _default_user_plugins_dir()
        )
        self.plugins_root.mkdir(parents=True, exist_ok=True)

    def list_plugins(self) -> list[str]:
        """Return sorted list of available plugin names."""
        out = []
        for p in self.plugins_root.iterdir():
            if p.is_dir():
                out.append(p.name)
            elif p.suffix == ".py":
                out.append(p.stem)
            else:
                out.append(p.name)
        return sorted(out)

    def install_plugin(
        self, src_path: Path, name: Optional[str] = None, force: bool = False
    ) -> Path:
        """Install a plugin from `src_path` into the user plugins directory and return the installed path."""
        src = Path(src_path)
        if not src.exists():
            raise FileNotFoundError(f"Plugin source '{src}' not found")
        name = name or src.name
        dest = self.plugins_root / name
        if dest.exists() and not force:
            raise FileExistsError(
                f"Plugin '{name}' already exists; use force=True to overwrite"
            )
        if dest.exists() and force:
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            # copy single file and preserve extension
            dest_name = dest.name
            if not dest_name.endswith(".py") and src.suffix:
                dest = dest.with_name(dest_name + src.suffix)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        return dest

    def remove_plugin(self, name: str) -> bool:
        """Remove a plugin by name (directory or Python file) and return True on success."""
        dest = self.plugins_root / name
        if not dest.exists():
            # try .py extension
            py_candidate = self.plugins_root / (name + ".py")
            if py_candidate.exists():
                dest = py_candidate
            else:
                # try as directory
                dir_candidate = self.plugins_root / name
                if dir_candidate.exists():
                    dest = dir_candidate
                else:
                    raise FileNotFoundError(f"Plugin '{name}' not found")
        if dest.is_dir():
            shutil.rmtree(dest)
        else:
            dest.unlink()
        return True

    def load_plugins(self) -> None:
        """Load plugin modules from the plugins directory and call `register(engine)` if present."""
        for p in sorted(self.plugins_root.iterdir()):
            try:
                if p.is_dir():
                    # look for __init__.py or plugin.py
                    candidates = [p / "__init__.py", p / "plugin.py"]
                    mod_file = None
                    for c in candidates:
                        if c.exists():
                            mod_file = c
                            break
                    if not mod_file:
                        continue
                else:
                    mod_file = p
                spec = importlib.util.spec_from_file_location(
                    f"bldrx_plugin.{p.stem}", str(mod_file)
                )
                # Guard against None spec/loader (myPy safety and runtime checks)
                if spec is None or spec.loader is None:
                    continue
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "register"):
                    try:
                        mod.register(self.engine)
                    except Exception:
                        # do not allow a single plugin to crash engine load
                        continue
            except Exception:
                continue
