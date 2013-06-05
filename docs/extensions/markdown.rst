.. markdown:

Markdown
========

Presents a builder that parse templates as markdown source and generate a given
jinja template with a `content` variable filled with the generated HTML.

Configuration
-------------

:MARKDOWN_TEMPLATE: The template to generate with the `content` variable.
:MARKDOWN_EXTENSIONS: Extra extensions to be passed to markdown.
:MARKDOWN_BUILDER_PATTERNS: Filename patterns that to be passed to the builder.

Builder
-------

The markdown builder can be registered as a normal builder. Just need to
make an instance the class :class:`folio.ext.mdown.MarkdownBuilder` with a base
template and assign it to a pattern in your project::

    from folio.ext.mdown import MarkdownBuilder
    proj.add_builder('*.md', MarkdownBuilder('_base.html'))

In this case, all the files with `md` extension will be parsed as a markdown
source. The generated HTML will be passed to the jinja template `_base.html`,
that will be found in the `src/` directory, as a `content` variable.

An minimal `_base.html` could be:

.. sourcecode:: html+jinja

    <!doctype html>
    <article>{{ content }}</article>

To enable some markdown extensions you can pass a list to `markdown_extensions`
in the :class:`folio.ext.mdown.MarkdownBuilder` class.

Dependencies
------------

It uses the python markdown_ package.

.. _markdown: https://pypi.python.org/pypi/Markdown/
