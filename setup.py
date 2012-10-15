import os
from distutils.core import setup, Extension

author = 'Ole Streicher'
email = 'python-cpl@liska.ath.cx'
license_ = 'GPL'
cpl_version = '0.3.8'
doc = '''Python interface for the Common Pipeline Library.

Non-official library to access CPL modules via Python. 
It is not meant as part of the MUSE pipeline software, but 
may be useful for testing.'''
description = doc.splitlines()
long_description = "\n".join(description[2:])
description = description[0]

def create_version_file(cpl_version = cpl_version):
    vfile = open(os.path.join('cpl', 'version.py'), 'w')
    vfile.write("version = %s\n" % repr(cpl_version))
    vfile.write("author = %s\n" % repr(author))
    vfile.write("email = %s\n" % repr(email))
    vfile.write("license_ = %s\n" % repr(license_))
    vfile.write("doc = %s\n" % repr(doc))
    vfile.close()
include_dirs = os.environ.get('INCLUDE_PATH', '.').split(':') 
library_dirs = os.environ.get('LIBRARY_PATH', '.').split(':') 
module1 = Extension('cpl.CPL_recipe',
                    include_dirs = include_dirs,
                    library_dirs = library_dirs,
                    libraries = [ 'cplcore', 'cpldfs', 'cplui', 'cpldrs', 
                                  'gomp', 'mcheck' ],
                    sources = ['cpl/CPL_recipe.c'])

create_version_file()
setup (name = 'python-cpl',
       version = cpl_version, author = author, author_email = email, 
       description = description, long_description = long_description,  
       license = license_, url = 'http://www.aip.de/~oles/python-cpl/',
       packages = ['cpl'],
       ext_modules = [module1])

