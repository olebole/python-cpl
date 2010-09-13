Installation
============

To install and run this package, you need the following prequisites:

* CPL 5 <http://www.eso.org/sci/data-processing/software/cpl/>
  (:program:`Esorex` is not needed)
* Python 2.6 <http://www.python.org/>
* pyfits <http://www.pyfits.org/>
* a C compiler (tested with :program:`gcc`)

Determine where you want to install the compiled python package. Standard is
:file:`/usr/local`. In the source directory of cpl-python, run::

   python setup.py install --prefix=PREFIX

where :file:`{PREFIX}` is the installation path for the package. The package
will be installed in the subdir :file:`lib/python2.6/site-packages/`
(:file:`lib64/python2.6/site-packages/` on 64 bit systems) of :file:`{PREFIX}`

Add the directory :file:`{PREFIX}/lib[64]/python2.6/site-packages/` to your environment
variable :envvar:`PYTHONPATH`. 
