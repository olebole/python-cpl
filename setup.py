import os
from distutils.core import setup, Extension

author = 'Ole Streicher'
email = 'python-cpl@liska.ath.cx'
license_ = 'GPL'
cpl_version = '0.4'
doc = '''Python interface for the Common Pipeline Library.

This module can list, configure and execute CPL-based recipes from Python.
The input, calibration and output data can be specified as FITS files
or as pyfits objects in memory.

The Common Pipeline Library (CPL) comprises a set of ISO-C libraries that
provide a comprehensive, efficient and robust software toolkit. It forms a
basis for the creation of automated astronomical data-reduction tasks.

One of the features provided by the CPL is the ability to create
data-reduction algorithms that run as plugins (dynamic libraries). These are
called "recipes" and are one of the main aspects of the CPL data-reduction
development environment.

The interface may be used to run ESO pipeline recipes linked to CPL 
versions 4.0 to 6.1.1.'''
description = doc.splitlines()
long_description = "\n".join(description[2:])
description = description[0]
pkgname = 'python-cpl'
baseurl = 'http://www.aip.de/~oles/%s' % pkgname
classifiers = [ 
    'Development Status :: 4 - Beta',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Topic :: Scientific/Engineering :: Astronomy',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]

def create_version_file(cpl_version = cpl_version):
    vfile = open(os.path.join('cpl', 'version.py'), 'w')
    vfile.write("version = %s\n" % repr(cpl_version))
    vfile.write("author = %s\n" % repr(author))
    vfile.write("email = %s\n" % repr(email))
    vfile.write("license_ = %s\n" % repr(license_))
    vfile.write("doc = %s\n" % repr(doc))
    vfile.close()

create_version_file()

module1 = Extension('cpl.CPL_recipe',
                    sources = ['cpl/CPL_recipe.c', 'cpl/CPL_library.c'])

setup(
    name = pkgname,
    version = cpl_version, 
    author = author, 
    author_email = email, 
    description = description, 
    long_description = long_description,  
    license = license_, 
    url = baseurl,
    download_url = '%s/%s-%s.tar.gz' % (baseurl, pkgname, cpl_version),
    classifiers = classifiers, 
    requires = ['pyfits'],
    provides = ['cpl'],
    packages = ['cpl'], 
    ext_modules = [module1]
    )
