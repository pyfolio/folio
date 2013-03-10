# -*- coding: utf-8 -*-


# -- General configuration ----------------------------------------------------

project = u'Folio'
copyright = u'2013, Juan M Martínez'
version = '0.1' # The short X.Y version.
release = '0.1' # The full version, including alpha/beta/rc tags.

extensions = ['sphinx.ext.autodoc']
#templates_path = ['_templates']
#exclude_patterns = ['_build']
master_doc = 'index'
source_suffix = '.rst'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None


# -- Options for HTML output --------------------------------------------------

html_theme = 'folio'
html_theme_options = {}
html_theme_path = ['_themes']
#html_static_path = ['_static']
html_sidebars = {
    '**': ['navigation.html', 'sourcelink.html', 'searchbox.html']
}

# Output file base name for HTML help builder.
htmlhelp_basename = 'Foliodoc'


# -- Options for LaTeX output -------------------------------------------------

latex_documents = [
  ('index', 'Folio.tex', u'Folio Documentation',
   u'Juan M Martínez', 'manual'),
]


# -- Options for manual page output -------------------------------------------

man_pages = [
    ('index', 'folio', u'Folio Documentation',
     [u'Juan M Martínez'], 1)
]


# -- Options for Texinfo output -----------------------------------------------

texinfo_documents = [
  ('index', 'Folio', u'Folio Documentation',
   u'Juan M Martínez', 'Folio', 'One line description of project.',
   'Miscellaneous'),
]