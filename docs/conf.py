import os
import sys

sys.path.insert(0, os.path.abspath('..'))

project = 'CDE Harmonization'
copyright = '2025, CDE Harmonization Contributors'
author = 'CDE Harmonization Contributors'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.githubpages',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'myst_parser',
    'sphinx_design',
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'README.md']

html_theme = 'furo'
html_title = 'CDE Harmonization Documentation'

html_static_path = ['_static']

html_css_files = [
    'css/custom.css',
]

autosectionlabel_prefix_document = True

napoleon_google_docstring = True
napoleon_use_admonition_for_examples = True

myst_heading_anchors = 3
myst_enable_extensions = [
    "attrs_inline",
    "attrs_block",
    "fieldlist",
    "colon_fence"
]
