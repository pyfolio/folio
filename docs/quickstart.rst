Quickstart
==========

This page gives a quick introduction to Folio. It assumes you have Folio
installed. If is not, head over to the installation section.

A minimal project
-----------------

To begin with, you need to create a simple file `myfolio.py`, and add the
barebones of what it will became you project::

    from folio import Folio
    
    proj = Folio(__name__)
    
    if __name__ == "__main__":
        proj.build()

What this code do?

0. It will import a class `Folio` from the `folio` package. This class will be
   used as a central registry for all your project.
1. We create a instance of this class in the variable `proj` and pass it the
   package/module name. This will be used to locate your files and log for
   errors.
2. Finally it will build your files if this module is executed directly.

Now you need to create your source directory where all the files to build will
be. In there you will have your static files and your templates mixed. This
will be, basically, how you hierarchy will look after it's builded, but with
the source files. By default, this directory will be called *src*, but you
can change it by passing the :attr:`folio.Folio.source_path` parameter.

So, go ahead and create an *src* directory and a `hello.html` template inside:

.. sourcecode:: html+jinja

    <!doctype html>
    <title>Hello from Folio</title>
    Hello {{ name | default('World') }}!

And run you project with your Python interpreter::

    $ python myfolio.py

Nothing happened? Checkout the `build` directory, it has a `hello.html`. If you
open it with a browser, you will see that is a compiled version of the original
source we just created.
