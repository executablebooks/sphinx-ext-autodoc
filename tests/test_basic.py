from sphinx_ext_autodoc.sphinx_env import mock_sphinx_env
from sphinx_ext_autodoc import extract, doc


def test_get_roles(data_regression):
    with mock_sphinx_env() as app:
        roles = extract.get_roles(app)
    data_regression.check(sorted(list(roles)))


def test_get_directives(data_regression):
    with mock_sphinx_env() as app:
        directives = extract.get_directives(app)
    data_regression.check(sorted(list(directives)))


def test_get_registered_nodes(data_regression):
    with mock_sphinx_env() as app:
        nodes = extract.get_registered_nodes(app)
    data_regression.check(sorted(list(nodes)))


def test_format_event_listeners(data_regression):
    with mock_sphinx_env() as app:
        events = extract.format_event_listeners(app)
    data_regression.check(events)


def test_extract_role_info(data_regression):
    with mock_sphinx_env() as app:
        roles = extract.get_roles(app)
    data = extract.extract_role_info("acronym", roles["acronym"])
    data_regression.check(data)


def test_extract_directive_info(data_regression):
    with mock_sphinx_env() as app:
        directives = extract.get_directives(app)
    data = extract.extract_directive_info("figure", directives["figure"])
    data_regression.check(data)


def test_doc_directive(file_regression):
    with mock_sphinx_env() as app:
        directives = extract.get_directives(app)
    data = extract.extract_directive_info("figure", directives["figure"])
    file_regression.check(doc.document_directive(data), extension=".rst")
