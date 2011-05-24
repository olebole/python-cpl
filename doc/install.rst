Installation
============

Prequisites
-----------

* `CPL <http://www.eso.org/sci/data-processing/software/cpl/>`_ 5
  (:program:`Esorex` is not needed)
* `Python <http://www.python.org/>`_ 2.6 or 2.7, 
* `Pyfits <http://www.pyfits.org/>`_

Binary packages
---------------

* `Ubuntu repository <https://launchpad.net/~olebole/+archive/astro>`_ (10.04
  LTS, 10.10, and 11.04). This repository also contains the required packages
  that are not in the standard distribution (CPL etc.)
* `Python egg <http://peak.telecommunity.com/DevCenter/EasyInstall>`_ planned

Source code
-----------

* `Releases and prereleases <http://github.com/olebole/python-cpl/downloads>`_
* `Git repository <http://github.com/olebole/python-cpl>`_. To access, do a::

    git clone git://github.com/olebole/python-cpl.git

  This gives you the current version in the subdirectory :file:`python-cpl`.
  To update to the current version of an existing repository, do a 
  ``git pull`` in the :file:`python-cpl` directory.

  For more detailed information, check the manual page of :manpage:`git(1)` and the
  `github <http://github.com/olebole/python-cpl>`_ page of the project.

Compilation
-----------

* Additionally to the software mentioned above, a C compiler is needed.

* Determine where you want to install the compiled python package. Standard is
  :file:`/usr/local`. In the source directory of cpl-python, run::

    python setup.py install --prefix=PREFIX

  where :file:`{PREFIX}` is the installation path for the package. The package
  will be installed in the subdir :file:`lib/python2.6/site-packages/`
  (:file:`lib64/python2.6/site-packages/` on 64 bit systems) of :file:`{PREFIX}`

* Add the directory :file:`{PREFIX}/lib[64]/python2.6/site-packages/` to your
  environment variable :envvar:`PYTHONPATH`.
