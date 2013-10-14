# -*- coding: utf-8 -*-
"""
    Folio is an static website generator using jinja2 template engine.
"""

import os
import sys
import fnmatch
import logging

if sys.version > '3':
    basestring = str

from jinja2 import Environment, ChoiceLoader, FileSystemLoader

from .builders import static_builder, template_builder
from .helpers import lazy_property

__all__ = ['Folio']
__version__ = '0.4'


class Folio(object):
    """The project. This is the main (and only?) object for creating a Folio.

    The basic example is::

        from folio import Folio
        proj = Folio(__name__)
        proj.build()

    You could also call the run method to start a local web server and watch
    for modified files.

    :param import_name: Projects's name.
    :param source_path: Source directory that contains the templates to be
                        processed and the static files to be copied to the
                        build directory. Defaults to ``'src'`` in the project's
                        root.
    :param build_path: Destination directory where the final HTML will be
                       generated. Defaults to ``'build'`` in the project's
                       root.
    :param encoding: The template's encoding. Defaults to utf-8.
    :param extensions: List of Folio extensions to load and register.
    :param jinja_extensions: Jinja2 extensions.
    """

    #: The default configuration dictionary.
    default_config = {
        'DEBUG':                                False,
        'TESTING':                              False,
        'EXTENSIONS':                           [],
        'JINJA_EXTENSIONS':                     [],

        'STATIC_BUILDER_PATTERN':               '*',
        'TEMPLATE_BUILDER_PATTERN':             '*.html',
    }

    def __init__(self, import_name, source_path='src', build_path='build',
                 encoding='utf-8', extensions=(),
                 jinja_extensions=()):

        #: The name of the project. It's used for logging and can improve
        #: debugging information.
        self.import_name = import_name

        #: Make the configuration dictionary.
        self.config = self._create_config()
        self.config_initialized = False

        #: The destination directory to copy the static content and create the
        #: builded templates.
        self.build_path = self._make_abspath(build_path)

        #: The source directory from where the templates will be parsed.
        self.source_path = self._make_abspath(source_path)

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
        #:
        #: The template name passed to the context can be a list of patterns
        #: for a filename, so you could apply the same context to series of
        #: templates::
        #:
        #:     @proj.context(['feed.atom', '*.rss'])
        #:     def feed(jinja2_env):
        #:         return {'desc': 'A site about nothing'}
        #:
        #: Only the jinja environment is passed to the context function. If
        #: you need more control, you should write an extension.
        self.contexts = []

        #: Builders are the core of folio, this will link a filename match with
        #: a build function that will be responsible of translating templates
        #: into final HTML files.
        #:
        #: The default builder is given, this will treat all HTML files as
        #: jinja2 templates and process them, generating the same template name
        #: as output file in the build directory.
        self.builders = []

        #: The jinja environment is used to make a list of the templates, and
        #: it's used by the builders to dump output files.
        self.env = self._create_jinja_environment(jinja_extensions)

        #: Define the Folio extensions registry.
        self.extensions = {}
        for extension in extensions:
            self.add_extension(extension)

    @lazy_property
    def import_path(self):
        """Retrieve the import path (or root path) from the import name module
        file.

        The module has to be already loaded as this function doesn't support
        loaders/finders. If the module is not already loaded, the current
        working directory will be used instead.
        """
        module = sys.modules[self.import_name]
        if module is not None and hasattr(module, '__file__'):
            return os.path.abspath(os.path.dirname(module.__file__))
        return os.getcwd()

    @lazy_property
    def logger(self):
        """The project logger, an instance of the :class: `logging.Logger`.

        The default configuration is to log to stderr if the application is
        in debug mode.
        """
        logger = logging.getLogger(self.import_name)

        if self.config['DEBUG']:
            logger.setLevel(logging.DEBUG)
            logger.addHandler(logging.StreamHandler())

        return logger

    def _make_abspath(self, path):
        """Make a path absolute. If the given path is relative, it will be
        from the root path of the project.

        :param path: The path to make absolute.
        """
        if not os.path.isabs(path):
            path = os.path.join(self.import_path, path)
        return path

    def _create_config(self):
        """Create the configuration dictionary based on the default
        configuration."""
        new_config = {}
        new_config.update(self.default_config)
        return new_config

    def init_config(self):
        """Initialize the configuration."""

        if self.config_initialized:
            return

        if not self.builders:
            self.add_builder(self.config['STATIC_BUILDER_PATTERN'],
                             static_builder)
            self.add_builder(self.config['TEMPLATE_BUILDER_PATTERN'],
                             template_builder)

        # Register extensions.
        for extension in self.config.get('EXTENSIONS', []):
            self.register_extension(extension)

        # Register Jinja extensions.
        for jinja_extension in self.config.get('JINJA_EXTENSIONS', []):
            self.env.add_extension(jinja_extension)

        self.config_initialized = True

    @lazy_property
    def jinja_loader(self):
        """Create a Jinja loader."""
        return ChoiceLoader([
            FileSystemLoader(searchpath=self.source_path)
        ])

    def _create_jinja_environment(self, extensions):
        """Create a Jinja environment."""
        env = Environment(loader=self.jinja_loader,
                          extensions=extensions)
        env.globals.update({
            'config': self.config,
            'version': __version__,
        })

        return env

    def add_extension(self, extension):
        """Add an extension to the registry."""
        self.config.get('EXTENSIONS', []).append(extension)

        # If the configuration was already initialized, we register the
        # extension automatically.
        if self.config_initialized:
            self.register_extension(extension)

    def register_extension(self, extension):
        """Registers a new extension.

        Extensions can be used to add extra functionality to Folio. As they
        are created by this instance they cannot accept any arguments for
        configuration.

        If the extension is an string, it will try to load it from the buildin
        extension package, or as folio_<extname>.

        The extension could have an `register` function that will be called
        with the Folio project instance as first argument.

        :param extension: The extension itself or an string of the extension
                          name that could be found inside the build-in package
                          or as folio_<extname>.
        """
        if isinstance(extension, basestring):
            for modnameformat in ('folio.ext.%s', 'folio_%s'):
                modname = modnameformat % extension
                try:
                    module = __import__(modname, None, None, [extension])
                except ImportError:
                    continue

                self.logger.debug("Extension '%s' found." % extension)

                # Consider the module as an extension. Use the first one to
                # prioritize build-in extensions.
                extname, extension = extension, module
                break

            # If it's still an string, the extension was not found.
            if isinstance(extension, basestring):
                raise LookupError("Extension '%s' not found." % extension)
        else:
            try:
                extname = extension.__name__
            except AttributeError:
                raise ValueError("Extension name not found.")

            # Use only the last part as the extension name. For example, if the
            # full module name is `myproj.ext.archive_things`, the extension
            # name will become `archive_things`.
            extname = extname.split('.')[-1]

            # If the extension is `folio_<extname>`, keep only the `<extname>`
            # part as extension name.
            if extname.startswith('folio_'):
                extname = extname[6:]

        if extname in self.extensions:
            raise LookupError("The '%s' extension has already been"
                              " registered." % extname)

        # Add the found extension to the registry.
        self.extensions[extname] = extension

        # Everything that has a register function can be consider as an
        # extension.
        if hasattr(extension, 'register'):
            extension.register(self)

    def build(self):
        """Build templates to the build directory. It will create the build
        path if not exists, and build all matched templates."""

        # Initialize the configuration.
        self.init_config()

        # If the build directory does exits, create it.
        if not os.path.exists(self.build_path):
            os.mkdir(self.build_path)

        # Get a list of the templates to be builded. For the moment is all the
        # files in the templates directory, except for the ones that start with
        # a dot or an underscore.
        templates = self.list_templates()

        # A set of builded files. This will be returned by the method so you
        # could do something with the new modified templates. The format is a
        # tuple with source path, destination path, and the result of the
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

        #: This is the full path of the template. This is useful if the file is
        #: not actually a jinja template but another format that you need to
        #: open and process.
        src = os.path.join(self.source_path, template_name)

        # If the template is not in the src directory, it has to be inside a
        # theme. So we tried to load it from the ChoiceLoader.
        if not os.path.exists(src):
            src = self.jinja_loader.get_source(self.env, template_name)[1]

        try:
            # Maybe the builder is an instance of class and has a method for
            # translating the template name into the destination name.
            dstname = builder.translate_template_name(template_name)
        except AttributeError:
            dstname = self.translate_template_name(template_name)

        #: This is the full path destination.
        dst = os.path.join(self.build_path, dstname)

        # If the destination directory doesn't exists, create it.
        dstdir = os.path.join(self.build_path, os.path.dirname(dst))
        if not os.path.exists(dstdir):
            os.makedirs(dstdir)

        #: Retrieve the context. Will call all the context functions and merge
        #: the results together. If no context are found, an empty dictionary
        #: is returned.
        context = self.get_context(template_name)

        # Call the real builder. For the moment, don't care what the returned
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
            try:
                enabled = builder.enabled
            except AttributeError:
                enabled = True
            if not enabled:
                self.logger.warning('Builder %s disabled', repr(builder))
            self.builders.append((pattern, builder))
        else:
            try:
                iterator = iter(pattern)
            except TypeError:
                raise TypeError('The pattern is not a string, nor iterable.')
            for item in iterator:
                self.add_builder(item, builder)

    def get_builder(self, template_name):
        """Returns the builder for the given template name or None if there are
        not related builders.

        :param template_name: The template name to lookup the builder for.
        """
        for pattern, builder in reversed(self.builders):
            if fnmatch.fnmatch(template_name, pattern):
                try:
                    enabled = builder.enabled
                except AttributeError:
                    enabled = True
                if enabled:
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
        behavior is to ignore all hidden files and the ones that start with
        and underscore.

        .. versionadded:: 0.2
            Will ignore files inside directories that starts with a dot or an
            underscore.

        :param filename: The (possible) template filename.
        """
        ignored = ('%s_' % os.path.sep in filename or
                   '%s.' % os.path.sep in filename or
                   filename.startswith('.') or
                   filename.startswith('_'))
        return not ignored

    def list_templates(self):
        """Returns a list of templates."""
        return self.env.list_templates(filter_func=self.is_template)

    def add_context(self, pattern, context):
        """Add a new context to the given pattern of a template name. If the
        pattern is a iterable, will add several times the same context.

        :param pattern: One or more template name patterns to add the context.
        :param context: The context itself or a function that will accept the
                        jinja environment as first parameter and return the
                        context for the template.
        """
        if isinstance(pattern, basestring):
            self.contexts.append((pattern, context))
        else:
            try:
                iterator = iter(pattern)
            except TypeError:
                raise TypeError('The pattern is not a string, nor iterable.')
            for item in iterator:
                self.add_context(item, context)

    def get_context(self, template_name):
        """Returns a context for the given template. If more that one context
        are assigned to the template name, there are going to be merged all
        together in the order that has been added. If a context is a callable
        it will be called with the jinja environment as first argument.

        A basic example::

            proj.add_context('index.html', {'name': 'Juan', 'files': [])
            proj.add_context('index.html', lambda env: {'name': 'Flor'})
            proj.get_context('index.html')
            # Returns {'name': 'Flor', 'files': []}

        :param template_name: The template name to retrieve the context.
        """
        context = {}
        for pattern, ctx in self.contexts:
            if fnmatch.fnmatch(template_name, pattern):
                if callable(ctx):
                    ctx = ctx(self.env)
                context.update(ctx)
        return context

    def context(self, pattern):
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

        :param pattern: The template name pattern (or more than one) to make a
                        context.
        """
        def wrapper(func):
            self.add_context(pattern, func)
            return func
        return wrapper
