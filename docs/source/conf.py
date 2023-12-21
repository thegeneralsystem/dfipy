"""Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options. For a full
list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
# pylint: skip-file

# -- Path setup --------------------------------------------------------------
import sys
from pathlib import Path

sys.path.append(str(Path(".").resolve()))

# -- Project information -----------------------------------------------------

project = "DFI-py"
copyright = "2023, General System"
author = "General System"
# release = "1.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autosummary",  # Generate autodoc summaries
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.duration",
    "sphinx.ext.napoleon",
    # "autoapi.extension",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",  # adds links to highlighted source code
    "sphinx_copybutton",  # adds copy button to code snippets
    "sphinx_favicon",
    "autodoc2",  # we use autodoc2 extension because it's compatible with myst (markdown)
    "myst_parser",
    # "myst_nb", # for notebooks
    # "jupyterlite-sphinx", # https://jupyterlite-sphinx.readthedocs.io/en/latest/
]

todo_include_todos = True
myst_enable_extensions = ["colon_fence", "fieldlist"]
autodoc2_packages = ["../../dfi"]
autodoc2_render_plugin = "myst"
autodoc2_sort_names = True
autodoc2_hidden_objects = ["dunder", "private"]  # "undoc"

templates_path = ["_templates"]
exclude_patterns = []


# -- autosummary -------------------------------------------------------------

autosummary_generate = True

# # -- Options for autoapi -------------------------------------------------------
# autoapi_type = "python"
# autoapi_dirs = ["../../dfi"]
# autoapi_keep_files = True
# autoapi_root = "api"
# autoapi_member_order = "groupwise"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_logo = "_static/gs_logo.png"
html_theme_options = {
    "logo": {
        "text": "General System",
        "alt text": "General System",
        "link": "https://dfipy.docs.generalsystem.com/",
    },
    "header_links_before_dropdown": 4,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/thegeneralsystem",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "Binder",
            "url": "https://mybinder.org/v2/gh/thegeneralsystem/dfipy-examples.git/HEAD",
            "icon": "_static/binder-favicon.png",
            "type": "local",
            # "icon": "_static/binder-favicon.png",
        },
        {
            "name": "General System",
            "url": "https://www.generalsystem.com/",
            "icon": "_static/gs-favicon-32x32.png",
            "type": "local",
        },
    ],
    "show_toc_level": 2,
    "navbar_align": "left",  # [left, content, right] For testing that the navbar items align properly
}
favicons = [
    {"href": "gs-favicon-32x32.png"},  # => use `_static/icon.svg`
]
html_static_path = ["_static"]
