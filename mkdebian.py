import fnmatch
import os
import shutil
import subprocess
import tarfile
#from cpl.version import __version__ as cpl_version
cpl_version = '0.2.1'

basedir = 'debian_build'
module = 'cpl'

shutil.rmtree(basedir, ignore_errors= True)
os.mkdir(basedir)
os.mkdir(os.path.join(basedir, module))
os.mkdir(os.path.join(basedir, 'debian'))
#tar = tarfile.open('python-cpl-%s.tar.gz' % cpl_version, mode='w:gz')
tar = tarfile.open('python-cpl.tar.gz', mode='w:gz')

shutil.copy('setup.py', basedir)
tar.add('setup.py')
shutil.copy('README', basedir)
tar.add('README')

files = fnmatch.filter(os.listdir(module), '*.py') + ['CPL_recipe.c']
for fname in files:
    shutil.copy(os.path.join(module, fname), os.path.join(basedir, module))
    tar.add(os.path.join(module, fname))

tar.close()

for fname in ['compat', 'control', 'copyright', 'docs', 'rules', 'changelog' ] :
    shutil.copy(os.path.join('debian', fname), os.path.join(basedir, 'debian'))

os.chdir(basedir)
subprocess.call(['dpkg-buildpackage', '-S'])

os.chdir('..')
#subprocess.call(['dput', 'ppa:olebole/astro', 'python-cpl_%s-3_source.changes' % cpl_version])
