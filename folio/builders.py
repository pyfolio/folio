# -*- coding: utf-8 -*-
"""
    Builders for Folio.
"""


from __future__ import with_statement

import os
import shutil


def static_builder(env, template_name, context, src, dst, encoding):
    shutil.copy(src, dst)


def template_builder(env, template_name, context, src, dst, encoding):
    template = env.get_template(template_name)
    template.stream(**context).dump(dst, encoding=encoding)


class Wrapper(object):
    """Simple template decorator builder.

    This will read a template, transform it (if provided) and pass it as a
    normal variable to a base template.

    :param template: The decorator template.
    :param variable: The variable name that will be passed to the decorator
                     template.
    :param transformer: The callable transformer. Will be called with the
                        content as first argument.
    """

    def __init__(self, template, variable='content', transformer=None):
        self.template = template
        self.variable = variable

        self.transformer = transformer

    def __call__(self, env, template_name, context, src, dst, encoding):
        with open(src, 'r') as f:
            content = f.read()

        if callable(self.transformer):
            content = self.transformer(content)

        context[self.variable] = content

        template = env.get_template(self.template)
        template.stream(**context).dump(dst, encoding=encoding)

    def translate_template_name(self, filename):
        """Always replace the original extension with HTML.

        :param filename: File name to translate.
        """
        name, _ = os.path.splitext(filename)
        return '.'.join([name, 'html'])
