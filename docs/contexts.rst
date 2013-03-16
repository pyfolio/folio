.. _contexts:

Contexts
========

From the example of the :ref:`quickstart`, you might notice that in our
template, we use a variable that has a default value. What if we want to change
the value of the variable? Simple, we add a context to the template in the
project.

Modify `myfolio.py` file to look like this::

    from folio import Folio
    
    proj = Folio(__name__)
    
    @proj.context('hello.html')
    def hello_context(jinja_env):
        return {'name': 'Pachi'}
    
    if __name__ == "__main__":
        proj.build()

The new function :func:`hello_context` will be registered with the decorator
:meth:`folio.Folio.context` to add a new set of variables assigned to the
template `hello.html`.

Re-build your project as before and in the `build` directory, the `hello.html`
will say "Hello Pachi!" instead of "Hello World!".

Add a context
-------------

The decorator is a shortcut to use the :meth:`folio.Folio.add_context` method.
The previous example could be written as::

    def hello_context(jinja_env):
        return {'name': 'Pachi'}
    proj.add_context('hello.html', hello_context)

Or without a callback function::

    proj.add_context('hello.html', {'name': 'Pachi'})

The same context could be added to several templates, it's as simple as
passing a list to the first argument::

    proj.add_context(['index.html', 'hello.html'], {'name': 'Pachi'})

In the same way, several contexts could be added to the same template. At the
end they will merged into one dictionary in the same order as they were added.
For example:

.. sourcecode:: python

    proj.add_context('index.html', {'name': 'Juan', 'files': [])
    proj.add_context('index.html', lambda env: {'name': 'Flor'})

Will generate the context ``{'name': 'Flor', 'files': []}``.

The templates names could be matched with a file name pattern. This is very
useful, for example, to add a context to all the templates (that maybe is used
in the layout template and not in each template *per se*)::

    @proj.context('*')
    def add_nav(jinja_env):
        links = [('Home', 'index.html'),
                 ('Downloads', 'download.html')]
        return {'nav': links}

The matching is done by the module :mod:`fnmatch`.