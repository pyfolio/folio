# -*- coding: utf-8 -*-
"""
    Folio extension that uses python markdown to parse templates.

    This extension add a builder that parse text files using markdown_ package
    and generate a given template with the `content` variable filled with the
    generated HTML.

    .. _markdown: https://pypi.python.org/pypi/Markdown/

    :param MARKDOWN_TEMPLATE: The template to generate with the `content`
                              variable. Defaults to "_markdown.html".
    :param MARKDOWN_VARIABLE: The variable name.
s    :param MARKDOWN_BUILDER_PATTERNS: Filename patterns that will be assigned
                                       to the builder.
"""


try:
    import markdown
except ImportError:
    markdown = False

from folio.builders import Wrapper
from folio.helpers import lazy_property


DEFAULT_TEMPLATE = '_markdown.html'
DEFAULT_VARIABLE = 'content'
DEFAULT_PATTERNS = ('*.md', '*.mdwn', '*.markdown')


class MarkdownBuilder(Wrapper):
    """A simple Markdown builder. Read files as markdown, parse them and pass
    a content variable with the generated HTML to the template base.

    For use it, add it as builder to your project::

        from folio.ext.mdwnbuilder import MarkdownBuilder
        proj.add_builder('*.md', MarkdownBuilder('_base.html'))

    This module serves as a extension, you could register it in your project
    and the builder will be added::

        from folio import Folio
        proj = Folio(__name__, extensions=['mdwnbuilder'])

    :param template: Base template to pass the generated HTML to. The default
                     is "_markdown.html".
    :param variable: Variable name to set.
    """

    #: False if the import of python markdown failed.
    enable = bool(markdown)

    def __init__(self, template=DEFAULT_TEMPLATE, variable=DEFAULT_VARIABLE):
        super().__init__(template, variable, self.parse)

    @lazy_property
    def markdown(self):
        return markdown.Markdown()

    def parse(self, content):
        return self.markdown.convert(content)


def register(folio):
    # Retrieve configuration.
    template = folio.config.get('MARKDOWN_TEMPLATE', DEFAULT_TEMPLATE)
    variable = folio.config.get('MARKDOWN_VARIABLE', DEFAULT_VARIABLE)
    patterns = folio.config.get('MARKDOWN_PATTERNS', DEFAULT_PATTERNS)

    # Add the builder.
    folio.add_builder(patterns, Wrapper(template, variable))
