# -*- coding: utf-8 -*-
"""
    Folio is an static website generator using jinja2 template engine.
"""

import os
import shutil
import fnmatch
import logging

from jinja2 import Environment, FileSystemLoader

__all__ = ['Folio']
__version__ = '0.1-dev'

class Folio(object):
    """
    :param name: Projects's name.
    :param build_path: Destination directory where the final HTML will be
                       generated. Defaults to ``'build'`` in the project's root.
    :param template_path: Source directory that contains the templates to be
                          processed. Defaults to ``'templates'`` in the
                          project's root.
    :param static_path: Source for the static content that will be copied to
                        the build directory as first action. Defaults to
                        ``'static'`` in the project's root.
    :param encoding: The template's encoding. Defaults to utf-8.
    :param jinja_extensions: Jinja2 extensions.
    """
    def __init__(self, name, build_path='build', template_path='templates',
                 static_path='static', encoding='utf-8',
                 jinja_extensions=()):

        #: The name of the project. It's used for logging and can improve
        #: debugging information.
        self.name = name

        #: The project logger, an instance of the :class: `logging.Logger`.
        self.logger = logging.getLogger(self.name)

        #: The destination directory to copy the static content and create the
        #: builded templates.
        self.build_path = os.path.abspath(build_path)

        #: The source directory from where the templates will be parsed.
        self.template_path = os.path.abspath(template_path)

        #: It contains files that will be copied at first to the build
        #: directory unmodified.
        self.static_path = os.path.abspath(static_path)

        #: The source encoding for templates. Default to utf-8.
        self.encoding = encoding

        #: The context generators per template. The template name is store as
        #: key and the callback as value. It will call the function, with the
        #: jinja2 environment as first parameters, for the template in the
        #: build process. The function must return a dictionary to be used in
        #: the template.
        #:
        #: Context functions are registered like this::
        #:
        #:     @proj.context('index.html')
        #:     def index_context(jinja2_env):
        #:         return {'files': jinja2_env.list_templates(),
        #:                 'author': 'Me'}
        #:
        #: Then in the template you could use it as normal variables.
        self.contexts = {}

        #: Builders are the core of folio, this will link a filename match with
        #: a build function that will be responsible of translating templates
        #: into final HTML files.
        #:
        #: The default builder is given, this will treat all *.html files as
        #: jinja2 templates and process them, generating the same template name
        #: as output file in the build directory.
        self.builders = [('*.html', self._default_builder)]

        loader = FileSystemLoader(searchpath=self.template_path)

        self.env = Environment(loader=loader, extensions=jinja_extensions)

    def build(self):
        def _remove_build():
            if os.path.exists(self.build_path):
                for path, _, files in os.walk(self.build_path, topdown=False):
                    for f in files:
                        os.remove(os.path.join(path, f))
                    os.rmdir(path)
        _remove_build()

        if os.path.exists(self.static_path):
            shutil.copytree(self.static_path, self.build_path)
        else:
            os.mkdir(self.build_path)

        templates = self.env.list_templates(filter_func=self.is_template)
        for template_name in templates:
            self.build_template(template_name)

    def build_template(self, template_name):
        context = {}
        if template_name in self.contexts:
            context = self.contexts[template_name](self.env)

        self.logger.info('Building %s', template_name)

        for pattern, builder in self.builders.__reversed__():
            if fnmatch.fnmatch(template_name, pattern):
                builder(self.env, template_name, context)
                break

    def is_template(self, filename):
        _, tail = os.path.split(filename)
        return not (tail.startswith('.') or tail.startswith('_'))

    def _default_builder(self, env, template_name, context):
        head, _ = os.path.split(template_name)
        if head:
            head = os.path.join(self.build_path, head)
            if not os.path.exists(head):
                os.makedirs(head)

        destination = os.path.join(self.build_path, template_name)
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

    def run(self, host='127.0.0.1', port=8080):
        import thread

        from SimpleHTTPServer import SimpleHTTPRequestHandler
        from BaseHTTPServer import HTTPServer

        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        os.chdir(self.build_path)

        def serve():
            server = HTTPServer((host, port), SimpleHTTPRequestHandler)
            server.serve_forever()

        self.logger.info('Serving at %s:%d', host, port)

        thread.start_new_thread(serve, ())

        def watch():
            def handler(event):
                if event.is_directory:
                    return

                template_name = event.src_path[len(self.template_path) + 1:]

                if not self.is_template(template_name):
                    return

                self.logger.info('File %s %s', template_name, event.event_type)
                self.build_template(template_name)

            EventHandler = type('EventHandler', (FileSystemEventHandler, ),
                                {'on_any_event': lambda self, e: handler(e)})

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

        watch()