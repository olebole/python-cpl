Installation
============

Prequisites
-----------

* `CPL <http://www.eso.org/sci/software/cpl/>`_ 5
  (:program:`Esorex` is not needed),
* `Python <http://www.python.org/>`_ 2.6 or 2.7, 
* `Pyfits <http://www.pyfits.org/>`_

Binary packages
---------------

* `Ubuntu repository <https://launchpad.net/~olebole/+archive/astro>`_ (10.04
  LTS, 10.10, and 11.04). This repository also contains the required packages
  that are not in the standard distribution (CPL etc.)
* Debian package planned
* `Python egg <http://peak.telecommunity.com/DevCenter/EasyInstall>`_ planned

Source code
-----------

* `Current release 0.3.5 
   <http://www.aip.de/~ole/python-cpl/python-cpl-0.3.5.tar.gz>`_
* `Git repository <http://github.com/olebole/python-cpl>`_. To access, do a::

    git clone git://github.com/olebole/python-cpl.git

  This gives you the current version in the subdirectory :file:`python-cpl`.
  To update to the current version of an existing repository, do a 
  ``git pull`` in the :file:`python-cpl` directory.

  For more detailed information, check the manual page of :manpage:`git(1)` 
  and the `github <http://github.com/olebole/python-cpl>`_ page of the project.

Compilation
-----------

Additionally to the software mentioned above, a C compiler is needed.

Define the installation path of the package. On default, this is
:file:`/usr/local`. If using a non-standard installation path, add the
directory :file:`{PREFIX}/lib/python2.7/site-packages/`
(:file:`lib64/python2.7/site-packages/` on 64 bit systems) to your environment
variable :envvar:`PYTHONPATH` where where :file:`{PREFIX}` is the installation
path for the package.

In the source directory of cpl-python, run::

  python setup.py install --prefix=PREFIX

Test suite
----------

There are a number of tests defined in :file:`test/TestRecipe.py`. To run
them, you need first to compile the recipe in :file:`test/iiinstrumentp/`::

  cd test/iiinstrumentp/
  ./bootstrap
  ./configure
  make
  cd ..
  python TestRecipe.py

The tests may print a memory corruption detection by glibc. This is normal,
since the tests also check the behaviour of this behaviour in the recipe.
