"""Sphinx configuration. """

from datetime import datetime

project = "ArgComb"
copyright = f"{datetime.now().year}, Jacob Unna"
author = "Jacob Unna"
release = "0.1"
extensions = ["sphinx.ext.autodoc"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "alabaster"
html_static_path = ["_static"]
html_sidebars = {
    "**": ["about.html", "navigation.html",],
}
html_theme_options = {
    "description": "Validate argument combinations",
    "github_user": "jacobunna",
    "github_repo": "argcomb",
}
