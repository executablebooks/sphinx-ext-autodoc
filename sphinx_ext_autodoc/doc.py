from importlib_resources import files
from jinja2 import Template

from sphinx_ext_autodoc import templates


def document_directive(data: dict, template: str = None):
    if template is None:
        template = files(templates).joinpath("directive.rst.j2").read_text()
    _template = Template(template)
    return _template.render(**data)
