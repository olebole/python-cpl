import fnmatch
import os
import shutil
import subprocess
import tarfile

vline = open(os.path.join('debian', 'changelog')).readline()
cpl_version = vline.split('(', 1)[1].split('-')[0]
cpl_release = vline.split('(', 1)[1].split('-')[1].split(')')[0]

module = 'cpl'

vfile = open(os.path.join(module) + 'version.py', 'w')
vfile.write("__version__ = '%s'\n" % cpl_version)
vfile.close()

files = fnmatch.filter(os.listdir(module), '*.py') + ['CPL_recipe.c']

# 1. build common tar file
#tar = tarfile.open('python-cpl-%s.tar.gz' % cpl_version, mode='w:gz')
tar = tarfile.open('python-cpl.tar.gz', mode='w:gz')
tar.add('setup.py')
tar.add('README')
for fname in files:
    tar.add(os.path.join(module, fname))
tar.close()

# 2. Build distribution dependent files
for distrib in [ 'lucid', 'maverick' ]:
    basedir = os.path.abspath('debian_build_%s' % distrib)

    shutil.rmtree(basedir, ignore_errors= True)
    os.mkdir(basedir)
    os.mkdir(os.path.join(basedir, module))
    os.mkdir(os.path.join(basedir, 'debian'))

    shutil.copy('setup.py', basedir)
    shutil.copy('README', basedir)

    for fname in files:
        shutil.copy(os.path.join(module, fname), os.path.join(basedir, module))

    for fname in ['compat', 'control', 'copyright', 'docs', 'rules', ] :
        shutil.copy(os.path.join('debian', fname), 
                    os.path.join(basedir, 'debian'))

    changelog_orig = open(os.path.join('debian', 'changelog'))
    changelog_dist = open(os.path.join(basedir, 'debian', 'changelog'), 'w')
    for line in changelog_orig:
        changelog_dist.write(line.replace('$DISTRIB', distrib))
    changelog_orig.close()
    changelog_dist.close()

    os.chdir(basedir)
    subprocess.call(['dpkg-buildpackage', '-S'])

    os.chdir('..')
    subprocess.call([
            'dput', 'ppa:olebole/astro', 
            'python-cpl_%s-%s_source.changes' 
            % (cpl_version, cpl_release.replace('$DISTRIB', distrib))
            ])


