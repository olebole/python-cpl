'''This module contains support for reading input files and parameters from
the FITS header of a CPL processed file.

This is done through the FITS headers that were written by the DRS function
called within the preocessing recipe.

'''

import os
import pyfits

def _get_header(source):
    if isinstance(source, str):
        return pyfits.open(source)[0].header
    elif isinstance(source, pyfits.HDUList):
        return source[0].header
    elif isinstance(source, pyfits.PrimaryHDU):
        return source.header
    elif isinstance(source, (pyfits.Header, dict)):
        return source
    else:
        raise ValueError('Cannot assign type %s to header' % 
                         source.__class__.__name__)

def get_recipe_name(source, index = 1):
    '''Get the recipe name from a FITS file processed with CPL.

    :param source: Object pointing to the result file header
    :type source: :class:`str` or :class:`PyFits.HDUList` 
                  or :class:`PyFits.PrimaryHDU` or :class:`PyFits.Header` 
    :param index: Record index (optional).
    :type index: :class:`int`
    '''
    return _get_header(source)['HIERARCH ESO PRO REC%i ID' % index]

def get_recipe_version(source, index = 1):
    '''Get the recipe version from a FITS file processed with CPL as a string.

    :param source: Object pointing to the result file header
    :type source: :class:`str` or :class:`PyFits.HDUList` 
                  or :class:`PyFits.PrimaryHDU` or :class:`PyFits.Header` 
    :param index: Record index (optional).
    :type index: :class:`int`
    '''
    return _get_header(source)['HIERARCH ESO PRO REC%i PIPE ID' % index]\
        .split('/')[1]

def get_cpl_version(source, index = 1):
    '''Get the CPL version from a FITS file processed with CPL as a string.

    :param source: Object pointing to the result file header
    :type source: :class:`str` or :class:`PyFits.HDUList` 
                  or :class:`PyFits.PrimaryHDU` or :class:`PyFits.Header` 
    :param index: Record index (optional).
    :type index: :class:`int`
    '''
    return _get_header(source)['HIERARCH ESO PRO REC%i DRS ID' % index]

def get_pipeline(source, index = 1):
    '''Get the pipeline name from a FITS file processed with CPL as a string.

    :param source: Object pointing to the result file header
    :type source: :class:`str` or :class:`PyFits.HDUList` 
                  or :class:`PyFits.PrimaryHDU` or :class:`PyFits.Header` 
    :param index: Record index (optional).
    :type index: :class:`int`
    '''
    return _get_header(source)['HIERARCH ESO PRO REC%i PIPE ID' % index]\
        .split('/')[0]

def get_tag(source, index = 1):
    '''Get the pipeline name from a FITS file processed with CPL as a string.

    :param source: Object pointing to the result file header
    :type source: :class:`str` or :class:`PyFits.HDUList` 
                  or :class:`PyFits.PrimaryHDU` or :class:`PyFits.Header` 
    :param index: Record index (optional).
    :type index: :class:`int`
    '''
    return _get_header(source)['HIERARCH ESO PRO REC%i RAW1 CATG' % index]

def _get_rec_keys(header, key, name, value, index = 1):
    '''Get a dictionary of key/value pairs from the DRS section of the header.

    :param header: FITS header
    :type source: :class:`PyFits.Header` 
    :param key: Common keyword for the value. Usually 'PARAM' for parameters,
                'RAW' for raw frames, and 'CAL' for calibration frames.
    :type key: :class:`str`
    :param name: Header keyword (last part) for the name of each key
    :type name: :class:`str`
    :param value: Header keyword (last part) for the value of each key
    :type name: :class:`str`
    :param index: Record index (optional).
    :type index: :class:`int`

    When the header

      HIERARCH ESO PRO REC1 PARAM1 NAME = 'nifu'
      HIERARCH ESO PRO REC1 PARAM1 VALUE = '1'
      HIERARCH ESO PRO REC1 PARAM2 NAME = 'combine'
      HIERARCH ESO PRO REC1 PARAM2 VALUE = 'median'

    is called with

      _get_rec_keys(header, 'PARAM', 'NAME', 'VALUE', 1)
   
    the returned dictionary will contain the keys

      res['nifu'] = '1'
      res['combine'] = 'median'
    '''
    res = dict()
    for i in range(1, 2**16):
        try:
            prefix = 'HIERARCH ESO PRO REC%i %s%i' % (index, key, i)
            k = header['%s %s' % (prefix, name)]
            fn = header['%s %s' % (prefix, value)]
            if k not in  res:
                res[k] = fn
            elif isinstance(res[k], list):
                res[k].append(fn)
            else:
                res[k] = [ res[k], fn ]
        except KeyError:
            break
    return res

def get_calib(source, index = 1):
    '''Get the calibration frames from a FITS file processed with CPL.

    :param source: Object pointing to the result file header
    :type source: :class:`str` or :class:`PyFits.HDUList` 
                  or :class:`PyFits.PrimaryHDU` or :class:`PyFits.Header` 
    :param index: Record index (optional).
    :type index: :class:`int`

    The header contains the calibration files that was used to create it.  The
    content is returned as a map with the tag as key and the list of file
    names as value.

    The result of this function may directly set as :attr:`Recipe.calib`
    attribute::
    
      import cpl
      myrecipe = cpl.Recipe('muse_bias')
      myrecipe.calib = cpl.drs.get_calib('MASTER_BIAS_0.fits')

    .. note:: This will not work properly for files that had
    :attr:`pyfits.HDUlist` inputs since they have assigned a temporary file
    name only.
    '''
    return _get_rec_keys(_get_header(source), 'CAL', 'CATG', 'NAME', index)

def get_input(source, index = 1):
    '''Get the raw frames from a FITS file processed with CPL.

    :param source: Object pointing to the result file header
    :type source: :class:`str` or :class:`PyFits.HDUList` 
                  or :class:`PyFits.PrimaryHDU` or :class:`PyFits.Header` 
    :param index: Record index (optional).
    :type index: :class:`int`

    The content is returned as list of file names.

    .. note:: This will not work properly for files that had
    :attr:`pyfits.HDUlist` inputs since they have assigned a temporary file
    name only.
    '''
    header = _get_header(source)
    tag = get_tag(header)
    return _get_rec_keys(header, 'RAW', 'CATG', 'NAME', index)[tag]

def get_param(source, index = 1):
    '''Get the processing parameters from a FITS file processed with CPL.

    :param source: Object pointing to the result file header
    :type source: :class:`str` or :class:`PyFits.HDUList` 
                  or :class:`PyFits.PrimaryHDU` or :class:`PyFits.Header` 
    :param index: Record index (optional).
    :type index: :class:`int`

    These files contain configuration parameters that were used to create
    it. The content is returned as a map with the (full) parameter name as key
    and its setting as string value.

    The result of this function may directly set as :attr:`Recipe.param`
    attribute::
    
      import cpl
      myrecipe = cpl.Recipe('muse_bias')
      myrecipe.param = cpl.drs.get_param('MASTER_BIAS_0.fits')

    '''
    return _get_rec_keys(_get_header(source), 'PARAM', 'NAME', 'VALUE', index)

if __name__ == '__main__':
    import sys

    for arg in sys.argv[1:]:
        print '---------------------' 
        print 'file: %s' % arg
        header = pyfits.open(arg)[0].header
        print 'Recipe: %s, Version %s, CPL version %s ' % (
            get_recipe_name(header), get_recipe_version(header), 
            get_cpl_version(header))
        print 'Parameters:'
        for k,v in get_param(header).items():
            print '  %s.%s.%s = %s' % (
                get_pipeline(header), get_recipe_name(header), k, v)
        print 'Calibration frames:'
        for k,v in get_calib(header).items():
            if isinstance(v, str):
                print '  %s %s' % (v,k)
            else:
                for n in v:
                    print '  %s %s' % (n,k)
        inputs = get_input(header)
        print 'Input frames:'
        if isinstance(inputs, str):
            print '  %s %s' % (inputs, get_tag(header))
        else:
            for n in inputs:
                print '  %s %s' % (n, get_tag(header))
