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
__version__ = '0.5'


class Folio(object):
    """The project. This is the main (and only?) object for creating a Folio.

    The basic example is::

        from folio import Folio
        proj = Folio(__name__)
        proj.build()

    You could also call the run method to start a local web server and watch
    for modified files.

    :param name: Projects's name.
    :param source_path: Source directory that contains the templates to be
                        processed and the static files to be copied to the
                        build directory. Defaults to ``'src'`` in the project's
                        root.
    :param build_path: Destination directory where the final HTML will be
                       generated. Defaults to ``'build'`` in the project's
                       root.
    :param encoding: The template's encoding. Defaults to utf-8.
    :param jinja_extensions: Jinja2 extensions.
    """
    def __init__(self, name, source_path='src', build_path='build',
                 encoding='utf-8', extensions=(), jinja_extensions=()):

        #: The name of the project. It's used for logging and can improve
        #: debugging information.
        self.name = name

        #: The project logger, an instance of the :class: `logging.Logger`.
        self.logger = logging.getLogger(self.name)

        #: The destination directory to copy the static content and create the
        #: builded templates.
        self.build_path = os.path.abspath(build_path)

        #: The source directory from where the templates will be parsed.
        self.source_path = os.path.abspath(source_path)

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
        self.builders = [('*', _static_builder), ('*.html', _template_builder)]

        #: The jinja environment is used to make a list of the templates, and
        #: it's used by the builders to dump output files.
        self.env = self._create_jinja_environment(jinja_extensions)

        #: Define the Folio extensions registry.
        self.extensions = {}
        for extension in extensions:
            self.add_extension(extension)

    def _create_jinja_loader(self):
        """Create a Jinja loader."""
        return FileSystemLoader(searchpath=self.source_path)

    def _create_jinja_environment(self, extensions):
        """Create a Jinja environment."""
        return Environment(loader=self._create_jinja_loader(),
                           extensions=extensions)

    def add_extension(self, extension):
        """Registers a new extension.

        Extensions can be used to add extra functionality to Folio. As they
        are created by this instance they cannot accept any arguments for
        configuration.

        If the extension is an string, it will try to load it from the buildin
        extension package, or as folio_<extname>.

        The extension could have an `register` function that will be called
        with the Folio project instance as first argument.

        :param extension: The extension itself or an string of the extension
                          name that could be found inside the buildin package
                          or as folio_<extname>.
        """
        if isinstance(extension, basestring):
            for modnameformat in ('folio.ext.%s', 'folio_%s'):
                modname = modnameformat % extension
                try:
                    module = __import__(modname, None, None, [extension])
                except ImportError:
                    continue
                # Consider the module as an extension. Use the first one to
                # prioritize buildin extensions.
                extension = module
                break

        # Everything that has a register function can be consider as an
        # extension.
        if hasattr(extension, 'register'):
            extension.register(self)
        self.extensions[extension.__name__] = extension

    def build(self):
        """Build templates to the build directory."""
        # If the build directory does exits, create it.
        if not os.path.exists(self.build_path):
            os.mkdir(self.build_path)

        # Get a list of the templates to be builded. For the moment is all the
        # files in the templates directory, except for the ones that start with
        # a dot or an underscore.
        templates = self.list_templates()

        # A set of builded files. This will be returned by the method so you
        # could do something with the new modified templates. The format is a
        # touple with source path, destination path, and the result of the
        # builder.
        builded = set()

        for template_name in templates:
            rv = self.build_template(template_name)

            if rv:
                # Add the response to the builded list if is not False.
                builded.add(rv)

        return builded

    def build_template(self, template_name):
        """Build a template with it's corresponding builder.

        The builder is responsible of generating the destination file in the
        destination path. It won't be checked for that the file was really
        created.

        The builder will be called with the jinja environment, the template
        name, a dictionary with the context, the source and destination paths
        and the output encoding.

        :param template_name: The template name to build.
        """
        self.logger.info('Building %s', template_name)

        #: Retrieve the builder for this template, normally this will never be
        #: empty, because the static builder is as a "catch all".
        builder = self.get_builder(template_name)

        #: This is the fullpath of the template. This is usefull if the file is
        #: not actually a jinja template but another format that you need to
        #: open and process.
        src = os.path.join(self.source_path, template_name)

        try:
            # Maybe the builder is an instance of class and has a method for
            # translating the template name into the destination name.
            dstname = builder.translate_template_name(template_name)
        except AttributeError:
            dstname = self.translate_template_name(template_name)

        #: This is the fullpath destination.
        dst = os.path.join(self.build_path, dstname)

        # If the destination directory doesn't exists, create it.
        dstdir = os.path.join(self.build_path, os.path.dirname(dst))
        if not os.path.exists(dstdir):
            os.makedirs(dstdir)

        #: Retrieve the context. Will call all the context functions and merge
        #: the results together. If no context are found, an empty dictionary
        #: is returned.
        context = self.get_context(template_name)

        # Call the real builder. For the moment, don't care what the retuned
        # value is, if any. But, in case that it return something, we grab it
        # and return it again.
        rv = builder(self.env, template_name, context, src, dst, self.encoding)

        # If no exception was raised, assume that the build was made.
        return (src, dst, rv)

    def add_builder(self, pattern, builder):
        """Adds a new builder related with the given file pattern. If the
        pattern is a iterable, will add several times the same builder.

        :param pattern: One or more file patterns.
        :param builder: The builder to be related with the file pattern(s).
        """
        if not callable(builder):
            raise TypeError('Invalid builder. Must be a callable.')
        if isinstance(pattern, basestring):
            self.builders.append((pattern, builder))
        else:
            try:
                iterator = iter(pattern)
            except TypeError:
                raise TypeError('The pattern is not a string, nor iterable.')
            for item in iterator:
                self.builders.append((item, builder))

    def get_builder(self, template_name):
        """Returns the builder for the given template name or None if there are
        not related builders.

        :param template_name: The template name to lookup the builder for.
        """
        for pattern, builder in reversed(self.builders):
            if fnmatch.fnmatch(template_name, pattern):
                return builder
        return None

    def translate_template_name(self, template_name):
        """Translate the template name to a destination filename. For the
        moment this will return the same filename.

        Because is used by the static builder, this will not try to change the
        template name extension to HTML.

        :param template_name: The input template name.
        """
        return template_name

    def is_template(self, filename):
        """Return true if a file is considered a template. The default
        behaviour is to ignore all hidden files and the ones that start with
        and underscore.

        :param filename: The (possible) template filename.
        """
        _, tail = os.path.split(filename)
        ignored = tail.startswith('.') or tail.startswith('_')
        return not ignored

    def list_templates(self):
        """Returns a list of templates."""
        return self.env.list_templates(filter_func=self.is_template)

    def add_context(self, template_name, context):
        """Add a new context to the given template name. Could add several
        contexts to the same template, this will be merged into one.

        :param template_name: The template name to add the context on.
        :param context: The context itself or a function that will accept the
                        jinja environment as first parameter and return the
                        context for the template.
        """
        if not self.is_template(template_name):
            raise ValueError('Invalid template')
        if not template_name in self.contexts:
            self.contexts[template_name] = []
        self.contexts[template_name].append(context)

    def get_context(self, template_name):
        """Returns a context for the given template. If more that one context
        are assigned to the template name, there are going to be merged all
        together in the order that has been added. If a context is a callable
        it will be called with the jinja environment as first argument.

        A basic example::

            proj.add_context('index.html', {'name': 'Juan', 'files': [])
            proj.add_context('index.html', lambda env: {'name': 'Flor'})
            proj.get_context('index.html')
            # Returns {'name': 'Flor', 'files': [])

        :param template_name: The template name to retrieve the context.
        """
        context = {}
        if not template_name in self.contexts:
            return context
        for ctx in self.contexts[template_name]:
            if callable(ctx):
                ctx = ctx(self.env)
            context.update(ctx)
        return context

    def context(self, template_name):
        """A decorator that is used to register a context function for a given
        template. This make the same thing as the method `add_context` passed
        with a function.

        A basic example::

            @proj.context('articles/index.html')
            def articles_context(env):
                return {'articles': [
                    ('2012-12-31', 'Happy New Year', 'articles/2013.html'),
                    ('2012-10-11', 'Hello World', 'articles/helloworld.html')
                ]}

        :param template_name: The template name to make a context.
        """
        def wrapper(func):
            self.add_context(template_name, func)
            return func
        return wrapper


def _static_builder(env, template_name, context, src, dst, encoding):
    shutil.copy(src, dst)


def _template_builder(env, template_name, context, src, dst, encoding):
    template = env.get_template(template_name)
    template.stream(**context).dump(dst, encoding=encoding)
