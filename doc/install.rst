Installation
============

Prequisites
-----------

* `Python <http://www.python.org/>`_ 2.6 or 2.7, 
* `Pyfits <http://packages.python.org/pyfits/>`_

Binary packages
---------------

* `Ubuntu repository <https://launchpad.net/~olebole/+archive/astro-quantal>`_
  (12.10). 
* Debian package in "Wheezy" (Testing)
  `<http://packages.debian.org/wheezy/python-cpl>`_
* `Python egg <http://peak.telecommunity.com/DevCenter/EasyInstall>`_ planned

Source code
-----------

* Current release `python-cpl-0.4.tar.gz <http://www.aip.de/~oles/python-cpl/python-cpl-0.4.tar.gz>`_
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

In the source directory of cpl-python, run::

  python setup.py install --prefix=PREFIX

There are other options available as well; use the :option:`--help` option to
list them.

Test suite
----------

The test suite can be downloaded as tar file `python-cpl-test-0.4.tar.gz <http://www.aip.de/~oles/python-cpl/python-cpl-test-0.4.tar.gz>`_.
There are a number of tests defined in :file:`test/TestRecipe.py`. To run
them, you need first to compile the recipe in :file:`test/iiinstrumentp/`::

  cd test/iiinstrumentp/
  ./bootstrap
  ./configure
  make
  cd ..
  python TestRecipe.py

Compiling the test recipe needs an installed CPL development environment.
The tests may print a memory corruption detection by glibc. This is normal,
since the tests also check this behaviour in the recipe.
