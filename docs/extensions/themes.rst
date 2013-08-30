.. themes:

Themes
======

Add theme support for a Folio project.

Configuration
-------------

:THEMES_PATHS: A list where the themes should be located. By default is a
               folder called *themes* at the root of your project. But this
               could be changed to use a cascade system of paths.
:THEME:        The current theme. Because it can only be one theme selected at
               the time.

Usage
-----

First you should enable and configure the extension::

    proj = Folio(__name__, extensions=['themes'])
    proj.config.update({'THEME': 'simplewater'})

Then you will have a :func:`theme` function available in your templates. This
could be used to use a file located in the current selected theme.

Here is an example you could find in your template:

.. sourcecode:: html+jinja

    {% extends theme("_base.html") %}
    {% block title %}Hello from Folio{% endblock %}
    {% block body %}Hello {{ name | default('World') }}!{% endblock %}

And then you define `themes/simplewater/_base.html` file:

.. sourcecode:: html+jinja

    <!doctype html>
    <title>{% block title %}{% endblock %}</title>
    {% block body %}{% endblock %}
