# -*- coding: utf-8 -*-
"""
    Folio is an static website generator using jinja2 template engine.
"""

import os
import shutil
import fnmatch

from jinja2 import Environment, FileSystemLoader

def log(message):
    print(' * %s' % (message, ))

class Folio(object):
    def __init__(self, build_path='build', template_path='templates',
                 static_path='static', encoding='utf-8', extensions=None):
        if extensions is None:
            extensions = []

        self.build_path = os.path.abspath(build_path)
        self.template_path = os.path.abspath(template_path)
        self.static_path = os.path.abspath(static_path)
        self.encoding = encoding

        self.contexts = {}
        self.builders = [('*.html', self._default_builder)]

        loader = FileSystemLoader(searchpath=template_path)
        self.env = Environment(loader=loader, extensions=extensions)

    def build(self):
        def _remove_build():
            if os.path.exists(self.build_path):
                for path, dirs, files in os.walk(self.build_path,
                                                 topdown=False):
                    for file in files:
                        os.remove(os.path.join(path, file))
                    os.rmdir(path)
        _remove_build()

        if os.path.exists(self.static_path):
            shutil.copytree(self.static_path, self.build_path)
        else:
            os.mkdir(self.build_path)

        def _filter_templates(filename):
            _, tail = os.path.split(filename)
            return not (tail.startswith('.') or tail.startswith('_'))

        templates = self.env.list_templates(filter_func=_filter_templates)
        for template_name in templates:
            self.build_template(template_name)

    def build_template(self, template_name):
        context = {}
        if template_name in self.contexts:
            context = self.contexts[template_name](self.env)

        log('Building %s' % (template_name, ))

        for pattern, builder in self.builders:
            if fnmatch.fnmatch(template_name, pattern):
                builder(self.env, template_name, context)
                break

    def _default_builder(self, env, template_name, context):
        destination = os.path.join(self.build_path, template_name)
        head, tail = os.path.split(template_name)
        if head:
            head = os.path.join(self.build_path, head)
            if not os.path.exists(head):
                os.makedirs(head)

        template = env.get_template(template_name)
        template.stream(**context).dump(destination, encoding=self.encoding)

    def context(self, template_name):
        def wrapper(func):
            self.contexts[template_name] = func
        return wrapper

    def builder(self, pattern):
        def wrapper(func):
            self.builders.append((pattern, func))
        return wrapper
