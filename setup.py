import os
try:
    from setuptools import setup, Extension
except:
    from distutils.core import setup, Extension

module1 = Extension('cpl.CPL_recipe',
                    libraries = [ 'cplcore', 'cpldfs', 'cplui', 'cpldrs', 'gomp' ],
                    sources = ['cpl/CPL_recipe.c'])

vline = open(os.path.join('debian', 'changelog')).readline()
cpl_version = vline.split('(', 1)[1].split('-')[0]
vfile = open(os.path.join('cpl', 'version.py'), 'w')
vfile.write("__version__ = '%s'\n" % cpl_version)
vfile.close()

setup (name = 'cpl',
       version = cpl_version,
       author = 'Ole Streicher',
       author_email = 'python-cpl@liska.ath.cx',
       description = 'Python interface for the Common Pipeline Library',
       long_description = \
           '''Non-official library to access CPL modules via Python. 
              It is not meant as part of the MUSE pipeline software, but 
              may be useful for testing''',
       license = 'Gnu Public License',
       packages = [ 'cpl'],
       ext_modules = [module1])

