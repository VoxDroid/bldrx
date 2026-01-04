from jinja2 import Environment, FileSystemLoader, StrictUndefined
from pathlib import Path

class Renderer:
    def __init__(self, template_searchpath):
        # template_searchpath can be a single path string or a list of paths
        if isinstance(template_searchpath, (list, tuple)):
            self.env = Environment(loader=FileSystemLoader([str(p) for p in template_searchpath]), undefined=StrictUndefined)
        else:
            self.env = Environment(loader=FileSystemLoader(str(template_searchpath)), undefined=StrictUndefined)

    def render_text(self, template_path, context):
        # template_path is relative to the loader(s)
        tmpl = self.env.get_template(template_path)
        return tmpl.render(**context)
