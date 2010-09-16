'''This module contains some limited support for reading esorex SOF and
configuration files.

Esorex is a standard execution environment for CPL recipes provided by
ESO. See http://www.eso.org/sci/data-processing/software/cpl/esorex.html for
details.
'''

import os
import cpl

def load_sof(source):
    '''Read an esorex sof file. 

    :param source: SOF file object or string with sof file content.
    :type source: :class:`str` or :class:`file`

    These files contain the raw and calibration files for a recipe.  The
    content of the file is returned as a map with the tag as key and the list
    of file names as value.

    The result of this function may directly set as :attr:`Recipe.calib`
    attribute::
    
      import cpl
      myrecipe = cpl.Recipe('muse_bias')
      myrecipe.calib = cpl.esorex.read_sof(file('muse_bias.sof'))

    .. note:: The raw data frame is silently ignored wenn setting
      :attr:`Recipe.calib` for MUSE recipes. Other recipes ignore ths raw data
      frame only if it was set manually as :attr:`Recipe.tag` or in
      :attr:`Recipe.tags` since there is no way to automatically distinguish
      between them.

    '''
    if isinstance(source, str):
        return load_sof(source.split('\n'))
    elif isinstance(source, (file, list)):
        res = dict()
        for line in source:
            if not line or line.startswith('#'):
                continue
            ls = line.split()
            fn = ls[0]
            key = ls[1]
            if key not in  res:
                res[key] = fn
            elif isinstance(res[key], list):
                res[key].append(fn)
            else:
                res[key] = [ res[key], fn ]
        return res
    else:
        raise ValueError('Cannot assign type %s to framelist' % 
                         source.__class__.__name__)

def load_rc(source = None):
    '''Read an esorex configuration file.

    :param source: Configuration file object, or string with file content. 
                   If not set, the esorex config file
                   :file:`~/.esorex/esorex.rc` is used.
    :type source: :class:`str` or :class:`file`

    These files contain configuration parameters for esorex or recipes. The
    content of the file is returned as a map with the (full) parameter name as
    key and its setting as string value.

    The result of this function may directly set as :attr:`Recipe.param`
    attribute::
    
      import cpl
      myrecipe = cpl.Recipe('muse_bias')
      myrecipe.param = cpl.esorex.load_rc('muse_bias.rc')

    .. note:: Unknown parameters are silently ignored wenn setting
              :attr:`Recipe.param`.

    '''
    if source is None:
        source = file(os.path.expanduser('~/.esorex/esorex.rc'))
    if isinstance(source, str):
        return load_rc(source.split('\n'))
    elif isinstance(source, (file, list)):
        res = dict()
        for line in source:
            if not line or not line.strip() or line.startswith('#'):
                continue
            name = line.split('=', 1)[0]
            value = line.split('=', 1)[1]
            if name and value:
                res[name.strip()] = value.strip()
        return res
    else:
        raise ValueError('Cannot assign type %s to parameter list' % 
                         source.__class__.__name__)

def init(source = None):
    '''Set the message verbosity and recipe search path from the
    :file:`esorex.rc` file.

    :param source: Configuration file object, or string with file content. 
        If not set, the esorex config file :file:`~/.esorex/esorex.rc` is used.
    :type source: :class:`str` or :class:`file`
    '''

    rc = cpl.esorex.load_rc(source)
    if rc.has_key('esorex.caller.recipe-dir'):
        cpl.Recipe.path = rc['esorex.caller.recipe-dir'].split(':')
    if rc.has_key('esorex.caller.msg-level'):
        cpl.msg.level = rc['esorex.caller.msg-level']
