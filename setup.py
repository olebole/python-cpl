import os
try:
    from setuptools import setup, Extension
except:
    from distutils.core import setup, Extension

author = 'Ole Streicher'
email = 'python-cpl@liska.ath.cx'
license_ = 'GPL'
cpl_version = '0.3.4'
doc = '''Python interface for the Common Pipeline Library.

Non-official library to access CPL modules via Python. 
It is not meant as part of the MUSE pipeline software, but 
may be useful for testing.'''
description = doc.splitlines()
long_description = "\n".join(description[2:])
description = description[0]

def create_version_file():
    changelog = os.path.join('debian', 'changelog')
    if os.path.exists(changelog):
        vline = open(changelog).readline()
        cpl_version = vline.split('(', 1)[1].split('-')[0]
    vfile = open(os.path.join('cpl', 'version.py'), 'w')
    vfile.write("version = '%s'\n" % cpl_version)
    vfile.write("author = '%s'\n" % author)
    vfile.write("email = '%s'\n" % email)
    vfile.write("license_ = '%s'\n" % license_)
    vfile.write("doc = '''%s'''\n" % doc)
    vfile.close()

module1 = Extension('cpl.CPL_recipe',
                    include_dirs = [ '/store/01/MUSE/oles/include/',
                                     '/store/01/MUSE/oles/include/cext'],
                    libraries = [ 'cplcore', 'cpldfs', 'cplui', 'cpldrs', 
                                  'gomp', 'mcheck' ],
                    library_dirs = ['/store/01/MUSE/oles/lib'],
                    sources = ['cpl/CPL_recipe.c'])

create_version_file()
setup (name = 'cpl',
       version = cpl_version, author = author, author_email = email, 
       description = description, long_description = long_description,  
       license = license_, url = 'http://www.aip.de/~oles/python-cpl/',
       packages = [ 'cpl'],
       ext_modules = [module1])

