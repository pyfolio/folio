# -*- coding: utf-8 -*-
"""
    Folio extension that uses python markdown to parse templates.
"""

from __future__ import with_statement

import os
import markdown

__all__ = ['MarkdownBuilder']

class MarkdownBuilder(object):
    """A simple Markdown builder. Read files as markdown, parse them and pass
    a content variable with the generated HTML to the template base.

    :param template_base: The base template to pass the generated HTML to.
    :param markdown_extensions: A list of extensions for the markdown module.
    """
    def __init__(self, template_base='_markdown.html',
                 markdown_extensions=None):

        #: This will be the template base for creating the HTML files.
        self.template_base = template_base

        if markdown_extensions is None:
            markdown_extensions = ['meta']

        #: Instance of Markdown.
        self.markdown = markdown.Markdown(extensions=markdown_extensions)

    def __call__(self, env, template_name, context, src, dst, encoding):
        content, meta = self.parse(src)

        context['content'] = content
        context['meta'] = meta
        context.update(meta)

        template = env.get_template(self.template_base)
        template.stream(**context).dump(dst, encoding=encoding)

    def translate_template_name(self, filename):
        """Make the same filename as the template, but HTML instead of the
        markdown extension."""
        name, _ = os.path.splitext(filename)
        return '.'.join([name, 'html'])

    def parse(self, filename):
        """Parse the given filename with markdown and return a touple with the
        content HTML and the meta data."""
        with open(filename) as f:
            markdown = f.read()

        content = self.markdown.convert(markdown)
        meta = self.markdown.Meta or {}

        return (content, meta)