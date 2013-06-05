# -*- coding: utf-8 -*-
"""
    Folio extension that uses python markdown to parse templates.
    
    This extension add a builder that parse text files using markdown_ package
    and generate a given template with the `content` variable filled with the
    generated HTML.
    
    .. _markdown: https://pypi.python.org/pypi/Markdown/
    
    :param MARKDOWN_TEMPLATE: The template to generate with the `content`
                              variable. Defaults to "_markdown.html".
    :param MARKDOWN_EXTENSIONS: Extra extensions to be passed to markdown.
    :param MARKDOWN_BUILDER_PATTERNS: Filename patterns that will be assigned
                                      to the builder.
"""

from __future__ import with_statement

import os
import markdown


__all__ = ['MarkdownBuilder']

DEFAULT_TEMPLATE = '_markdown.html'
DEFAULT_EXTENSIONS = ()


class MarkdownBuilder(object):
    """A simple Markdown builder. Read files as markdown, parse them and pass
    a content variable with the generated HTML to the template base.

    For use it, add it as builder to your project::

        from folio.ext.mdown import MarkdownBuilder
        proj.add_builder('*.md', MarkdownBuilder('_base.html'))

    This module serves as a extension, you could register it in your project
    and the builder will be added::

        from folio import Folio
        proj = Folio(__name__, extensions=['mdown'])

    :param template_base: The base template to pass the generated HTML to. The
                          default is "_markdown.html".
    :param markdown_extensions: List of extensions for the markdown module.
    """
    def __init__(self, template_base=DEFAULT_TEMPLATE,
                 markdown_extensions=DEFAULT_EXTENSIONS):

        #: This will be the template base for creating the HTML files.
        self.template_base = template_base

        #: Instance of Markdown.
        self.markdown = markdown.Markdown(extensions=markdown_extensions)

    def __call__(self, env, template_name, context, src, dst, encoding):
        content = self.parse(src)
        context['content'] = content

        template = env.get_template(self.template_base)
        template.stream(**context).dump(dst, encoding=encoding)

    def translate_template_name(self, filename):
        """Make the same filename as the template, but HTML instead of the
        markdown extension.

        :param filename: File name to translate."""
        name, _ = os.path.splitext(filename)
        return '.'.join([name, 'html'])

    def parse(self, filename):
        """Parse the given filename with markdown and return a tuple with the
        content HTML.

        :param filename: The file to parse."""
        with open(filename) as f:
            markdown = f.read()

        return self.markdown.convert(markdown)


def register(folio):
    # Get parameters from the project configuration dictionary.
    template = folio.config.get('MARKDOWN_TEMPLATE', DEFAULT_TEMPLATE)
    extensions = folio.config.get('MARKDOWN_EXTENSIONS', DEFAULT_EXTENSIONS)
    patterns = folio.config.get('MARKDOWN_BUILDER_PATTERNS', '*.md')

    # Add builder.
    folio.add_builder(patterns, MarkdownBuilder(template, extensions))
