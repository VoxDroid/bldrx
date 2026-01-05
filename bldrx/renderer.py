from __future__ import annotations

from typing import Any, Dict, Iterable, Union

from jinja2 import Environment, FileSystemLoader, StrictUndefined


class Renderer:
    """Thin wrapper around a Jinja2 Environment to render templates from one or more search paths."""

    def __init__(self, template_searchpath: Union[str, Iterable[str]]):
        """Initialize the renderer.

        Parameters:
        - template_searchpath: a single path string or an iterable of path strings to use as Jinja2 search paths.
        """
        if isinstance(template_searchpath, (list, tuple)):
            self.env = Environment(
                loader=FileSystemLoader([str(p) for p in template_searchpath]),
                undefined=StrictUndefined,
            )
        else:
            self.env = Environment(
                loader=FileSystemLoader(str(template_searchpath)),
                undefined=StrictUndefined,
            )

    def render_text(self, template_path: str, context: Dict[str, Any]) -> str:
        """Render `template_path` using `context` and return the rendered text."""
        tmpl = self.env.get_template(template_path)
        return tmpl.render(**context)
