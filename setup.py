import os
try:
    from setuptools import setup, Extension
except:
    from distutils.core import setup, Extension

def get_version():
    changelog = os.path.join('debian', 'changelog')
    if os.path.exists(changelog):
        vline = open(changelog).readline()
        cpl_version = vline.split('(', 1)[1].split('-')[0]
    else:
        cpl_version = '0.3.4'
    vfile = open(os.path.join('cpl', 'version.py'), 'w')
    vfile.write("__version__ = '%s'\n" % cpl_version)
    vfile.close()
    return cpl_version

module1 = Extension('cpl.CPL_recipe',
                    include_dirs = [ '/store/01/MUSE/oles/include/',
                                     '/store/01/MUSE/oles/include/cext'],
                    libraries = [ 'cplcore', 'cpldfs', 'cplui', 'cpldrs', 'gomp' ],
                    library_dirs = ['/store/01/MUSE/oles/lib'],
                    sources = ['cpl/CPL_recipe.c'])

setup (name = 'cpl',
       version = get_version(),
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

