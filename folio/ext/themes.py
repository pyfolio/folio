# -*- coding: utf-8 -*-
"""
    Theming support for Folio.

    :param THEME: The active theme name. Defaults to 'basic'.
    :param THEMES_PATHS: A list of directories where the themes could be
                         defined.
"""

import os
import sys

if sys.version > '3':
    basestring = str

from jinja2 import BaseLoader, FileSystemLoader

from folio.helpers import lazy_property


__all__ = ['Theme', 'ThemeManager', 'ThemeTemplateLoader']

THEME = 'basic'
THEMES_PATHS = ['themes']


class Theme(object):
    """An instance of a theme. It has a name, path, some settings and a jinja
    loader."""

    def __init__(self, name, path, **settings):
        self.name = name
        self.path = os.path.join(path, name)
        self.settings = settings

    @lazy_property
    def jinja_loader(self):
        return FileSystemLoader(self.path)


class ThemeManager(object):
    """Controls all themes."""

    #: A list of paths where the themes can be found in.
    paths = []

    #: Cache for the instances of the class:class:`folio.ext.themes.Theme` of
    #: every theme which was used. Each instance is created by the method
    #: :meth:`folio.ext.themes.ThemeManager.get_theme`.
    themes = {}

    #: The current theme.
    theme = None

    def __init__(self, folio=None):
        if folio is not None:
            self.bind_proj(folio)

    def bind_proj(self, folio):
        self.folio = folio

    def get_theme(self, name, path=None):
        if name in self.themes:
            return self.themes[name]

        # Where to lookup the theme.
        paths = self.paths if path is None else [path]

        for path in paths:
            if os.path.exists(os.path.join(path, name)):
                theme = Theme(name, path)
                self.themes[name] = theme
                return theme

        raise LookupError('Theme %s not found.' % name)

    def get_template(self, template_name, theme=None):
        if theme is None:
            theme = self.theme
        elif isinstance(theme, basestring):
            theme = self.themes[theme]

        return '_themes/%s/%s' % (theme.name, template_name)


class ThemeTemplateLoader(BaseLoader):
    """Load templates of the themes controlled by the given theme manager."""

    def __init__(self, manager):
        BaseLoader.__init__(self)

        #: One theme manager to rule them all.
        self.manager = manager

    def get_source(self, environment, template):
        if template.startswith('_themes/'):
            theme_name, template = template[8:].split('/', 1)
            theme = self.manager.themes[theme_name]
        else:
            theme = self.manager.theme

        return theme.jinja_loader.get_source(environment, template)

    def list_templates(self):
        found = set()
        for theme in self.manager.themes.itervalues():
            found.update(theme.jinja_loader.list_templates())
        return sorted(found)


def register(folio):
    #: The theme manager is the own to controls every theme in the system.
    manager = ThemeManager(folio)

    #: List of themes paths.
    for themes_path in folio.config.get('THEMES_PATHS', THEMES_PATHS):
        manager.paths.append(folio._make_abspath(themes_path))

    #: Current theme.
    manager.theme = manager.get_theme(folio.config.get('THEME', THEME))

    #: The theme template loader it's for loading specific templates in a
    #: theme. This is useful for example when you have a file `src/style.css`
    #: that inside you want to include the `themes/basic/style.css`. You need
    #: to use the method :meth:`folio.ext.themes.ThemeManager.get_template`
    #: that is available as `theme` in jinja.
    loader = ThemeTemplateLoader(manager)

    # Add the theme template loader to the list of loaders. This is possible
    # because the :attr:`folio.Folio.jinja_loader` is an instance of the Jinja
    # loader `ChoiceLoader`.
    folio.jinja_loader.loaders.append(loader)

    # Add a global function to be called within the templates.
    folio.env.globals.update({
        'theme': manager.get_template,
    })
