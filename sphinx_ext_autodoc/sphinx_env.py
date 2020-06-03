from contextlib import contextmanager
import copy
import tempfile

from docutils.parsers.rst import directives, roles

from sphinx.application import builtin_extensions, Sphinx
from sphinx.config import Config
from sphinx.environment import BuildEnvironment
from sphinx.events import EventManager
from sphinx.project import Project
from sphinx.registry import SphinxComponentRegistry
from sphinx.util.docutils import additional_nodes, sphinx_domains, unregister_node
from sphinx.util.tags import Tags


def minimal_sphinx_app(configuration=None, sourcedir=None):
    """Create a minimal Sphinx environment; loading sphinx roles, directives, etc.
    """

    class MockSphinx(Sphinx):
        """Minimal sphinx init to load roles and directives."""

        def __init__(self, confoverrides=None, srcdir=None):
            self.extensions = {}
            self.registry = SphinxComponentRegistry()
            self.html_themes = {}
            self.events = EventManager(self)
            self.tags = Tags(None)
            self.config = Config({}, confoverrides or {})
            self.config.pre_init_values()
            self._init_i18n()
            for extension in builtin_extensions:
                self.registry.load_extension(self, extension)
            # fresh env
            self.doctreedir = None
            self.srcdir = srcdir
            self.confdir = None
            self.outdir = None
            self.project = Project(srcdir=srcdir, source_suffix=".md")
            self.project.docnames = ["mock_docname"]
            self.env = BuildEnvironment()
            self.env.setup(self)
            self.env.temp_data["docname"] = "mock_docname"
            self.builder = None

            if not confoverrides:
                return

            # this code is only required for more complex parsing with extensions
            for extension in self.config.extensions:
                self.setup_extension(extension)
            buildername = "dummy"
            self.preload_builder(buildername)
            self.config.init_values()
            self.events.emit("config-inited", self.config)

            with tempfile.TemporaryDirectory() as tempdir:
                # creating a builder attempts to make the doctreedir
                self.doctreedir = tempdir
                self.builder = self.create_builder(buildername)
            self.doctreedir = None

    app = MockSphinx(confoverrides=configuration, srcdir=sourcedir)
    return app


@contextmanager
def mock_sphinx_env(conf=None, srcdir=None, document=None):
    """Set up an environment, to parse sphinx roles/directives,
    outside of a `sphinx-build`.

    :param conf: a dictionary representation of the sphinx `conf.py`
    :param srcdir: a path to a source directory
        (for example, can be used for `include` statements)

    This primarily copies the code in `sphinx.util.docutils.docutils_namespace`
    and `sphinx.util.docutils.sphinx_domains`.
    """
    # store currently loaded roles/directives, so we can revert on exit
    _directives = copy.copy(directives._directives)
    _roles = copy.copy(roles._roles)
    # Monkey-patch directive and role dispatch,
    # so that sphinx domain-specific markup takes precedence.
    app = minimal_sphinx_app(configuration=conf, sourcedir=srcdir)
    _sphinx_domains = sphinx_domains(app.env)
    _sphinx_domains.enable()
    if document is not None:
        document.settings.env = app.env
    try:
        yield app
    finally:
        # revert loaded roles/directives
        directives._directives = _directives
        roles._roles = _roles
        # TODO unregister nodes (see `sphinx.util.docutils.docutils_namespace`)
        for node in list(additional_nodes):
            unregister_node(node)
            additional_nodes.discard(node)
        # revert directive/role function (see `sphinx.util.docutils.sphinx_domains`)
        _sphinx_domains.disable()
