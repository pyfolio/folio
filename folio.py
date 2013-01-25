# -*- coding: utf-8 -*-
"""
    Folio is an static website generator using jinja2 template engine.
"""

import os
import shutil

from jinja2 import Environment, FileSystemLoader

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def log(message):
    print(' * %s' % (message, ))

class Folio(object):
    def __init__(self, build_path='build', template_path='templates',
                 static_path='static', encoding='utf-8'):
        self.build_path = os.path.abspath(build_path)
        self.template_path = os.path.abspath(template_path)
        self.static_path = os.path.abspath(static_path)
        self.encoding = encoding

        loader = FileSystemLoader(searchpath=template_path)

        self.contexts = {}
        self.env = Environment(loader=loader)

    def _remove_build(self):
        if os.path.exists(self.build_path):
            for path, dirs, files in os.walk(self.build_path, topdown=False):
                for file in files:
                    os.remove(os.path.join(path, file))
                os.rmdir(path)

    def watch(self):
        def wrapper(folio):
            def handler(self, event):
                if not event.is_directory:
                    template_name = event.src_path[len(folio.template_path)+1:]
                    log('Template "%s" %s' % (template_name, event.event_type))
                    folio.build_template(template_name)
            return handler

        EventHandler = type('EventHandler', (FileSystemEventHandler, ),
                            {'on_any_event': wrapper(self)})

        log('Watching for changes in "%s"' % (self.template_path, ))

        observer = Observer()
        observer.schedule(EventHandler(), path=self.template_path,
                          recursive=True)
        observer.start()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def build(self):
        self._remove_build()

        if os.path.exists(self.static_path):
            shutil.copytree(self.static_path, self.build_path)
        else:
            os.mkdir(self.build_path)

        templates = self.env.list_templates(filter_func=_filter_templates)
        for template_name in templates:
            self.build_template(template_name)

    def build_template(self, template_name):
        head, tail = os.path.split(template_name)
        if head:
            head = os.path.join(self.build_path, head)
            if not os.path.exists(head):
                os.makedirs(head)

        context = {}
        if template_name in self.contexts:
            context = self.contexts[template_name](self.env)

        log('Building %s' % (template_name, ))

        destination = os.path.join(self.build_path, template_name)
        template = self.env.get_template(template_name)
        template.stream(**context).dump(destination, encoding=self.encoding)

    def context(self, template_name):
        def wrapper(func):
            self.contexts[template_name] = func
        return wrapper

def _filter_templates(filename):
    _, tail = os.path.split(filename)
    nrender = tail.startswith('.') or tail.startswith('_')
    return not nrender
