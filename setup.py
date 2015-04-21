import os
from distutils.core import setup, Extension
from pkg_resources import require, DistributionNotFound

author = 'Ole Streicher'
email = 'python-cpl@liska.ath.cx'
license_ = 'GPL'
cpl_version = '0.7~pre'
with open('README.rst') as readme:
    description = readme.read().splitlines()
    long_description = "\n".join(description[2:])
    description = description[0]

doc = '%s\n%s' % (description, 
                  long_description[:long_description.find('Build instructions')])
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
Topic :: Scientific/Engineering :: Astronomy
'''.splitlines()


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
