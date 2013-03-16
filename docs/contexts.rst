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
