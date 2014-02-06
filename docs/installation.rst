Installation
============

Dependencies
------------

Folio depends on `Jinja2 <http://jinja.pocoo.org/2/>`_ for rendering templates.

Some extensions need aditional packages.

Official release
----------------

The simplest installation is to use `pip`. If you are not inside a
`virtualenv`, you will do a system-wide installation, so you need to run it
with root privileges::

    $ pip install Folio

Manual installation
-------------------

Download the latest release from the download_ page. The file will be named
as `Folio-X.Y.tar.gz` where `X.Y` is the release version. Then you need to
untar it and move the the created directory.

::

    $ tar xvzf Folio-X.Y.tar.gz
    $ cd Folio-X.Y.tar.gz

If you are in Windows, you could use `7-zip`_. Then you need to open a command
shell with administrator privileges and `cd` to the uncompressed directory.

Finally you run this command with root privileges::

    $ python setup.py install

.. _download: https://pypi.python.org/pypi/Folio
.. _`7-zip`: http://www.7-zip.org/

Latest development version
--------------------------

To checkout the development version you will need to have `git` installed. Test
that you have it installed by executing `git --version` from the command line.
Is recommended to use `virtualenv` for all the testing/developing proposes.

The main repository lives in *momo.guide42.com*, but a `Github mirror`_ is
provided.

::

    $ git clone git://github.com/guide42/folio.git
    Cloning into 'folio'...
    $ cd folio
    $ virtualenv venv --distribute
    New python executable in venv/bin/python
    $ . venv/bin/activate
    $ python setup.py develop

.. _`Github mirror`: https://github.com/guide42/folio
