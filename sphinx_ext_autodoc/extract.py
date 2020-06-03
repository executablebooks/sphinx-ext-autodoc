from importlib import import_module
from inspect import getdoc
from typing import Callable

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.application import Sphinx
from sphinx.util.docutils import additional_nodes

# from sphinx.events import core_events


def get_roles(app: Sphinx):
    """Return all roles available within the current application."""
    from docutils.parsers.rst.roles import _roles, _role_registry

    all_roles = {}
    all_roles.update(_role_registry)
    all_roles.update(_roles)

    for domain_name in app.env.domains:
        domain = app.env.get_domain(domain_name)
        prefix = "" if domain.name == "std" else f"{domain.name}:"
        for role_name, role in domain.roles.items():
            all_roles[f"{prefix}{role_name}"] = role

    return all_roles


def get_directives(app: Sphinx):
    """Return all directives available within the current application."""
    from docutils.parsers.rst.directives import _directives, _directive_registry

    all_directives = {}
    all_directives.update(_directive_registry)
    all_directives.update(_directives)

    for key, (modulename, classname) in _directive_registry.items():
        if key not in all_directives:
            try:
                module = import_module(f"docutils.parsers.rst.directives.{modulename}")
                all_directives[key] = getattr(module, classname)
            except (AttributeError, ModuleNotFoundError):
                pass

    for domain_name in app.env.domains:
        domain = app.env.get_domain(domain_name)
        prefix = "" if domain.name == "std" else f"{domain.name}:"
        # TODO 'default_domain' is also looked up by
        # sphinx.util.docutils.sphinx_domains.lookup_domain_element
        for direct_name, direct in domain.directives.items():
            all_directives[f"{prefix}{direct_name}"] = direct

    return all_directives


def get_registered_nodes(app: Sphinx):
    """List all node types which have been registered. """
    # see sphinx.util.docutils.register_node
    node_dict = {
        attr[6:]: getattr(nodes, attr[6:], None)
        for attr in dir(nodes.GenericNodeVisitor)
        if attr.startswith("visit_")
    }
    node_dict.update({n.__name__: n for n in additional_nodes})
    return node_dict


def format_event_listeners(app: Sphinx):
    def _format_handler(handler):
        return {
            "name": handler.__name__,
            "description": getdoc(handler) or "",
            "module": f"{handler.__module__}",
        }

    events = {}
    for name, values in app.events.listeners.items():
        if isinstance(values, dict):
            # sphinx < 3
            for id, handler in values.items():
                events.setdefault(name, []).append(_format_handler(handler))
        else:
            for _, handler, _ in sorted(
                app.events.listeners.get(name, []), key=lambda l: l.priority
            ):
                events.setdefault(name, []).append(_format_handler(handler))

    # TODO sort by order of core_events

    return events


# TODO config options (+ defaults)


def extract_role_info(name: str, role_func: Callable) -> dict:
    """Extract JSONable information about a role."""
    return {
        "name": name,
        "description": getdoc(role_func) or "",
        "module": f"{role_func.__module__}",
    }


def extract_directive_info(name, direct_klass: Directive) -> dict:
    """Extract JSONable information about a directive."""
    # TODO also get documentation from option validators
    options = (
        {k: str(v.__name__) for k, v in direct_klass.option_spec.items()}
        if direct_klass.option_spec
        else {}
    )
    data = {
        "name": name,
        # TODO this can also return base class docstrings, which are too verbose
        "description": getdoc(direct_klass) or "",
        "klass": f"{direct_klass.__module__}.{direct_klass.__name__}",
        "required_arguments": direct_klass.required_arguments,
        "optional_arguments": direct_klass.optional_arguments,
        "has_content": direct_klass.has_content,
        "options": options,
    }
    # if "Base class for " in data["description"]:
    #     data["description"] = ""
    return data
