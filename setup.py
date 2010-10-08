try:
    from setuptools import setup, Extension
except:
    from distutils.core import setup, Extension

module1 = Extension('cpl.CPL_recipe',
                    libraries = [ 'cplcore', 'cpldfs', 'cplui', 'cpldrs', 'gomp' ],
                    sources = ['cpl/CPL_recipe.c'])

setup (name = 'cpl',
       version = '0.3.0',
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

