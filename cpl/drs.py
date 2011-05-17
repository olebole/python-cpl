import os
import pyfits

import cpl

class ProcessingInfo(object):
    '''This class contains support for reading input files and parameters from
    the FITS header of a CPL processed file.

    This is done through the FITS headers that were written by the DRS function
    called within the processing recipe.

    .. attribute:: name 

       Recipe name

    .. attribute:: version 

       Recipe version string

    .. attribute::  pipeline

       Pipeline name

    .. attribute:: cpl_version
    
       CPL version string

    .. attribute:: tag

       Tag name

    .. attribute:: calib

       Calibration frames from a FITS file processed with CPL.
       The result of this function may directly set as :attr:`Recipe.calib`
       attribute::
    
         import cpl
         myrecipe = cpl.Recipe('muse_bias')
         myrecipe.calib = cpl.drs.ProcessingInfo('MASTER_BIAS_0.fits').calib

       .. note:: This will not work properly for files that had
          :attr:`pyfits.HDUlist` inputs since they have assigned a temporary
          file name only.

    .. attribute:: raw

       Raw (input) frames

       .. note:: This will not work properly for files that had
          :attr:`pyfits.HDUlist` inputs since they have assigned a temporary
          file name only.

    .. attribute:: param

       Processing parameters.
       The result of this function may directly set as :attr:`Recipe.param`
       attribute::
    
         import cpl
         myrecipe = cpl.Recipe('muse_bias')
         myrecipe.param = cpl.drs.ProcessingInfo('MASTER_BIAS_0.fits').param
    '''

    def __init__(self, source, index = 1, datapaths = None):
        '''
        :param source: Object pointing to the result file header
        :type source: :class:`str` or :class:`PyFits.HDUList` 
                      or :class:`PyFits.PrimaryHDU` or :class:`PyFits.Header` 
        :param index: Record index (optional).
        :type index: :class:`int`
        :param datapaths: Dictionary with frame tags as keys and directory paths
                        as values to provide a full path for the raw and 
                        calibration frames. Optional.
        :type datapaths: :class:`dict`
        '''
        if isinstance(source, str):
            header = pyfits.open(source)[0].header
        elif isinstance(source, pyfits.HDUList):
            header = source[0].header
        elif isinstance(source, pyfits.PrimaryHDU):
            header = source.header
        elif isinstance(source, (pyfits.Header, dict)):
            header = source
        else:
            raise ValueError('Cannot assign type %s to header' % 
                             source.__class__.__name__)
        
        self.name = header['HIERARCH ESO PRO REC%i ID' % index]
        self.product = header['HIERARCH ESO PRO CATG']
        self.orig_filename = header['PIPEFILE']
        if datapaths and self.product in datapaths:
            self.orig_filename = os.path.join(datapaths[self.product], 
                                              self.orig_filename)
        try:
            pipe_id = header['HIERARCH ESO PRO REC%i PIPE ID' % index]
            self.pipeline = pipe_id.split('/')[0]
            version = pipe_id.split('/')[1]
            num_version = 0
            for i in version.split('.'):
                num_version = num_version * 100 + int(i)
            self.version = (num_version, version)
        except KeyError:
            self.pipeline =  None
            self.version = None
        try:
            self.cpl_version = header['HIERARCH ESO PRO REC%i DRS ID' % index]
        except KeyError:
            self.cpl_version = None
        try:
            self.calib = _get_rec_keys(header, index, 'CAL', 'CATG', 'NAME', 
                                       datapaths)
        except KeyError:
            self.calib = None
        try:
            self.tag = header['HIERARCH ESO PRO REC%i RAW1 CATG' % index]
            self.raw = _get_rec_keys(header, index, 'RAW', 'CATG', 'NAME', 
                                     datapaths)[self.tag]
        except KeyError:
            self.tag = None
            self.input = None
        try:
            param = _get_rec_keys(header, index, 'PARAM', 'NAME', 'VALUE')
            self.param = dict()
            for k,v in param.items():
                try:
                    self.param[k] = int(v)
                except ValueError:
                    try:
                        self.param[k] = float(v)
                    except ValueError:
                        if v == 'true':
                            self.param[k] = True
                        elif v == 'false':
                            self.param[k] = False
                        else:
                            self.param[k] = v
        except KeyError:
            self.param = None
            
    def create_recipe(self):
        recipe = cpl.Recipe(self.name)
        recipe.param = self.param
        recipe.calib = self.calib
        recipe.tag = self.tag
        return recipe

    def printinfo(self):
        print 'Recipe: %s, Version %s, CPL version %s ' % (
            self.name, self.version, self.cpl_version)
        print 'Parameters:'
        for k,v in self.param.items():
            print ' %s.%s.%s = %s' % (self.pipeline, self.name, k, v)
        if self.calib:
            print 'Calibration frames:'
        for k,v in self.calib.items():
            if isinstance(v, str):
                print ' %s %s' % (v,k)
            else:
                for n in v:
                    print ' %s %s' % (n,k)
        print 'Input frames:'
        if isinstance(self.raw, str):
            print ' %s %s' % (self.raw, self.tag)
        else:
            for n in self.raw:
                print ' %s %s' % (n, self.tag)

def _get_rec_keys(header, index, key, name, value, datapaths = None):
    '''Get a dictionary of key/value pairs from the DRS section of the
    header.

    :param key: Common keyword for the value. Usually 'PARAM' for 
                parameters, 'RAW' for raw frames, and 'CAL' for 
                calibration frames.
    :type key: :class:`str`
    :param name: Header keyword (last part) for the name of each key
    :type name: :class:`str`
    :param value: Header keyword (last part) for the value of each key
    :type name: :class:`str`
    :param datapaths: Dictionary with frame tags as keys and directory paths 
                    as values to provide a full path for the raw and 
                    calibration frames. Optional.
    :type datapaths: :class:`dict`

    When the header
    
      HIERARCH ESO PRO REC1 PARAM1 NAME = 'nifu'
      HIERARCH ESO PRO REC1 PARAM1 VALUE = '1'
      HIERARCH ESO PRO REC1 PARAM2 NAME = 'combine'
      HIERARCH ESO PRO REC1 PARAM2 VALUE = 'median'
      
    is called with

      _get_rec_keys('PARAM', 'NAME', 'VALUE')

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
            if datapaths and k in datapaths:
                fn = os.path.join(datapaths[k], fn)
            if k not in  res:
                res[k] = fn
            elif isinstance(res[k], list):
                res[k].append(fn)
            else:
                res[k] = [ res[k], fn ]
        except KeyError:
            break
    return res
    
if __name__ == '__main__':
    import sys

    datapaths = {
        'BIAS':'raw', 'DARK':'raw', 'FLAT':'raw', 'ARC':'raw', 'OBJECT':'raw', 
        'LINE_CATALOG':'aux', 'TRACE_TABLE':'aux', 'GEOMETRY_TABLE':'aux',
        'MASTER_BIAS':'result', 'MASTER_DARK':'result', 'MASTER_FLAT':'result',
        'WAVECAL_TABLE':'result', 'PIXTABLE_OBJECT':'result', 
        }
    for arg in sys.argv[1:]:
        print '---------------------' 
        print 'file: %s' % arg
        pi = ProcessingInfo(arg, datapaths = datapaths)
        pi.printinfo()
