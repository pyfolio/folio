# -*- coding: utf-8 -*-
"""
    Builders for Folio.
"""


import shutil


def static_builder(env, template_name, context, src, dst, encoding):
    shutil.copy(src, dst)


def template_builder(env, template_name, context, src, dst, encoding):
    template = env.get_template(template_name)
    template.stream(**context).dump(dst, encoding=encoding)
