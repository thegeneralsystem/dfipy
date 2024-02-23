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

project = "dfipy"
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
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",  # adds links to highlighted source code
    "sphinxext.opengraph",  # adds Open Graph meta tags to your site’s generated HTML
    "autodoc2",  # we use autodoc2 extension because it's compatible with myst (markdown)
    # "autoapi.extension",    # supposedly has support for auto API generation of other languages
    "sphinx_copybutton",  # adds copy button to code snippets
    "sphinx_favicon",
    # "sphinx_thebe",  # live running of code and links to Colab, MyBinder, etc (https://daobook.github.io/sphinx-book-theme/reference/thebe.html)
    "myst_parser",
    "sphinx_design",  # adds tabs
    "sphinx_togglebutton",  # adds toggles
    # "myst_nb", # for notebooks
    # "jupyterlite-sphinx", # https://jupyterlite-sphinx.readthedocs.io/en/latest/
]

todo_include_todos = True
autodoc2_packages = ["../../dfi"]
autodoc2_render_plugin = "myst"
autodoc2_sort_names = True
autodoc2_hidden_objects = ["dunder", "private"]  # "undoc"

# autoapi_dirs = ["../../dfi"]

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
# html_theme = "furo"
html_title = "dfipy"
html_static_path = ["_static"]
html_css_files = ["_static/css/custom.css"]
html_sidebars = {"**": ["sidebar-nav-bs", "sidebar-ethical-ads"]}
html_logo = "_static/gs_logo.svg"
html_theme_options = {
    "logo": {
        "text": "",
        "alt text": "General System",
        "link": "https://dfipy.docs.generalsystem.com/",
    },
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/thegeneralsystem/dfipy",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "Binder",
            "url": "https://mybinder.org/v2/gh/thegeneralsystem/dfipy-examples.git/HEAD",
            "icon": "_static/binder-favicon.png",
            "type": "local",
        },
        {
            "name": "General System",
            "url": "https://www.generalsystem.com/",
            "icon": "_static/gs-favicon-32x32.png",
            "type": "local",
        },
    ],
    "content_footer_items": ["last-updated"],
    "pygment_light_style": "default",
    "pygment_dark_style": "github-dark",
}
html_css_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/fontawesome.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/solid.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/brands.min.css",
]

favicons = [
    {"href": "gs-favicon-32x32.png"},  # => use `_static/icon.svg`
]
myst_enable_extensions = ["colon_fence", "fieldlist"]

# -- Furo Options ------------
pygments_style = "sphinx"
pygments_dark_style = "monokai"


def setup(app):
    app.add_css_file("css/custom.css")
