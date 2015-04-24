Installation
============

Prequisites
-----------

* `Python <http://www.python.org/>`_ 2.6 or higher, 
* `Astropy <http://www.astropy.org/>`_ or 
  `Pyfits <http://packages.python.org/pyfits/>`_

Binary packages
---------------

On Debian and debian-based systems (Ubuntu, Mint), python-cpl can be installed with the command

.. code-block:: sh

  apt-get install python-cpl

Python CPL comes with the Ubuntu distribution since 12.04.
Debian packages are in `Wheezy (Debian 7) <http://packages.debian.org/wheezy/python-cpl>`_, 
`Wheezy (Debian 8) <http://packages.debian.org/jessie/python-cpl>`_, and 
`Testing <http://packages.debian.org/testing/python-cpl>`_

Source code
-----------

* `Python Package Index <http://pypi.python.org/pypi/python-cpl/>`_

* `Git repository <http://github.com/olebole/python-cpl>`_. To access, do a::

    git clone git://github.com/olebole/python-cpl.git

  This gives you the current version in the subdirectory :file:`python-cpl`.
  To update to the current version of an existing repository, do a 
  ``git pull`` in the :file:`python-cpl` directory.

  For more detailed information, check the manual page of :manpage:`git(1)` 
  and the `github <http://github.com/olebole/python-cpl>`_ page of the project.

Compilation
-----------

For compilation, a C compiler is needed additionally to the software mentioned
above.

The installation follows the standard procedure used in python. On default,
the installation path :file:`/usr/local`. If using a non-standard installation
path, add the directory :file:`{PREFIX}/lib/python2.7/site-packages/`
(:file:`lib64/python2.7/site-packages/` on 64 bit systems) to your environment
variable :envvar:`PYTHONPATH` where where :file:`{PREFIX}` is the installation
path for the package.

In the source directory of python-cpl, run

.. code-block:: sh

  python setup.py install --prefix=PREFIX

There are other options available as well; use the :option:`--help` option to
list them.

Test suite
----------

There are a number of tests defined in :file:`test/TestRecipe.py`:

.. code-block:: sh

  python TestRecipe.py

The test recipe needs an installed CPL development environment.
The tests may print a memory corruption detection by glibc. This is normal,
since the tests also check this behaviour in the recipe.

Tests are also automatically buils by
`Travis CI <https://travis-ci.org/olebole/python-cpl>`_.
