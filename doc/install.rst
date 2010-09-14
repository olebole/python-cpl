Installation
============

Released version
----------------

There is still no released package available :-) We have plans to build the
following packages:

* Python egg <http://peak.telecommunity.com/DevCenter/EasyInstall>
* Ubuntu package <https://launchpad.net/~olebole/+archive/astro>
* Tar source ball

To install and run this package, you need the following prequisites:

* CPL 5 <http://www.eso.org/sci/data-processing/software/cpl/>
  (:program:`Esorex` is not needed)
* Python 2.6 <http://www.python.org/>
* pyfits <http://www.pyfits.org/>

These packages are checked when used the binary installation. However, for the
source file you need to install them on your own.

Developer version
-----------------

Currently, python-cpl is only available from its code repository. You need to
checkout from http://github.com/olebole/python-cpl . The easiest way of this
is::

    git clone git://github.com/olebole/python-cpl.git

This gives you the current version in the subdirectory :file:`python-cpl`.
To update to the current version of an existing repository, do a 
``git pull`` in the :file:`python-cpl` directory.

For more detailed information, check the manual page of :program:`git` and the
github page of the project.

Compile and install the source
------------------------------

Additionally to the software mentioned above, a C compiler is needed.

Determine where you want to install the compiled python package. Standard is
:file:`/usr/local`. In the source directory of cpl-python, run::

   python setup.py install --prefix=PREFIX

where :file:`{PREFIX}` is the installation path for the package. The package
will be installed in the subdir :file:`lib/python2.6/site-packages/`
(:file:`lib64/python2.6/site-packages/` on 64 bit systems) of :file:`{PREFIX}`

Add the directory :file:`{PREFIX}/lib[64]/python2.6/site-packages/` to your
environment variable :envvar:`PYTHONPATH`.
