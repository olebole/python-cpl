import os
from distutils.core import setup, Extension
from pkg_resources import require, DistributionNotFound

author = 'Ole Streicher'
email = 'python-cpl@liska.ath.cx'
license_ = 'GPL'
cpl_version = '0.7'
description = "Python interface for the ESO Common Pipeline Library"
long_description = '''This module can list, configure and execute CPL-based recipes from Python
(python2 and python3).  The input, calibration and output data can be
specified as FITS files or as ``astropy.io.fits`` objects in memory.

The ESO `Common Pipeline Library <http://www.eso.org/sci/software/cpl/>`_
(CPL) comprises a set of ISO-C libraries that provide a comprehensive,
efficient and robust software toolkit. It forms a basis for the creation of
automated astronomical data-reduction tasks. One of the features provided by
the CPL is the ability to create data-reduction algorithms that run as plugins
(dynamic libraries). These are called "recipes" and are one of the main
aspects of the CPL data-reduction development environment.
'''

pkgname = 'python-cpl'
baseurl = 'http://pypi.python.org/packages/source/%s/%s' % (pkgname[0], pkgname)
classifiers = '''Development Status :: 4 - Beta
Intended Audience :: Science/Research
License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)
Operating System :: MacOS :: MacOS X
Operating System :: POSIX
Operating System :: Unix
Programming Language :: C
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Topic :: Scientific/Engineering :: Astronomy
'''.splitlines()


def create_version_file(cpl_version = cpl_version):
    with open(os.path.join('cpl', 'version.py'), 'w') as vfile:
        vfile.write("version = %s\n" % repr(cpl_version))
        vfile.write("author = %s\n" % repr(author))
        vfile.write("email = %s\n" % repr(email))
        vfile.write("license_ = %s\n" % repr(license_))

try:
    create_version_file()
except IOError:
    pass

module1 = Extension('cpl.CPL_recipe',
                    sources = ['cpl/CPL_recipe.c', 'cpl/CPL_library.c'])
try:
    require('astropy')
    required='astropy'
except DistributionNotFound:
    required = 'pyfits'

setup(
    name = pkgname,
    version = cpl_version,
    author = author,
    author_email = email,
    description = description,
    long_description = long_description,
    license = license_,
    url = 'https://pypi.python.org/pypi/%s/%s' % (pkgname, cpl_version),
    download_url = '%s/%s-%s.tar.gz' % (baseurl, pkgname, cpl_version),
    classifiers = classifiers,
    requires = [ required ],
    provides = ['cpl'],
    packages = ['cpl'],
    ext_modules = [module1]
    )
