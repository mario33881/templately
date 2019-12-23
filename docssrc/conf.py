# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../templately/'))


# -- Project information -----------------------------------------------------

project = 'templately'
copyright = '2019, mario33881'
author = 'mario33881'

# The full version, including alpha/beta/rc tags
release = '01_01'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.coverage'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


def remove_module_docstring(app, what, name, obj, options, lines):
    '''
    This function removes the docstring of the module "templately"

    This is done because the docopt docstring format is poorely formatted
    by sphinx.

    The docstring is added manually with these lines inside the index.rst file

    .. literalinclude:: ../../templately.py
       :start-after: """
       :end-before: """
    '''
    if what == "module" and name == "templately":
        del lines[:]


def setup(app):
    '''
    This function determines custom configurations:
    - a new stylesheet is added to use more width for the documentation page
    - tell autodoc to not import the docstring of "templately" by calling
    the remove_module_docstring() function.
    '''
    app.add_stylesheet('style.css')
    app.connect("autodoc-process-docstring", remove_module_docstring)
