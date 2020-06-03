# sphinx-ext-autodoc [IN-DEVELOPMENT]

[![Code style: black][black-badge]][black-link]

Auto-document sphinx extensions.

Ths package is intended to analyse a sphinx environment and extract documentable information,
regarding the elements loaded by each extension (and docutils/sphinx themselves), such as:

- roles
- directives
- nodes
- transforms
- event callbacks

Then optionally turn it into documentation pages (maybe similar to how [sphinx-apidoc](https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html) works).

[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-link]: https://github.com/ambv/black

(package originally created by [python-pkg-cookiecutter](https://github.com/executablebooks/python-pkg-cookiecutter))
