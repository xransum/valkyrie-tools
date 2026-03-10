"""Sphinx configuration."""

from datetime import datetime

project = "valkyrie-tools"
author = "Kevin Haas"
copyright = f"{datetime.now().year}, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
autodoc_member_order = "bysource"
# Prefix autosection labels with the document name to avoid conflicts
autosectionlabel_prefix_document = True
# Only label top-level (=) and second-level (-) headings to avoid duplicate
# label collisions from repeated sub-section names like "Global Options".
autosectionlabel_maxdepth = 2
html_theme = "furo"
html_favicon = "images/favicon.png"
html_logo = "images/logo.png"
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
    "click": ("https://click.palletsprojects.com/en/stable/", None),
    "nox": ("https://nox.thea.codes/en/stable", None),
    "pip": ("https://pip.pypa.io/en/stable", None),
}
