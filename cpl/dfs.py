import itertools
import os
import sys
try:
    from astropy.io import fits
except:
    import pyfits as fits

import cpl

class ProcessingInfo(object):
    '''Support for reading input files and parameters from the FITS
    header of a CPL processed file.

    This is done through the FITS headers that were written by the DFS function
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
       The result of this function may directly set as :attr:`cpl.Recipe.calib`
       attribute::
    
         import cpl
         myrecipe = cpl.Recipe('muse_bias')
         myrecipe.calib = cpl.dfs.ProcessingInfo('MASTER_BIAS_0.fits').calib

       .. note::

          This will not work properly for files that had
          :class:`astropy.io.fits.HDUList` inputs since they have assigned a
          temporary file name only.

    .. attribute:: raw

       Raw (input) frames

       .. note::

          This will not work properly for files that had
          :class:`astropy.io.fits.HDUList` inputs since they have assigned a
          temporary file name only.

    .. attribute:: param

       Processing parameters.
       The result of this function may directly set as :attr:`cpl.Recipe.param`
       attribute::
    
         import cpl
         myrecipe = cpl.Recipe('muse_bias')
         myrecipe.param = cpl.dfs.ProcessingInfo('MASTER_BIAS_0.fits').param

    .. attribute:: md5sum

       MD5 sum of the data portions of the output file (header keyword 
       'DATAMD5').

    .. attribute:: md5sums

       MD5 sums of the input and calibration files. :class:`dict` with the
       file name as key and the corresponding MD5 sum as value.

       .. note::

          Due to a design decision in CPL, the raw input files are not
          accompanied with the MD5 sum.
    '''

    def __init__(self, source, recno = -1, md5sums = None):
        '''
        :param source: Object pointing to the result file header
        :type source: :class:`str` or :class:`astropy.io.fits.HDUList`
                      or :class:`astropy.io.fits.PrimaryHDU` or 
                      :class:`astropy.io.fits.Header`
        :param recno: Record number. Optional. If not given, the last record
                      (with the highest record number) is used.
        :type recno: :class:`int`
        :param md5sums: Dictionary with md5 sums as keys and complete file names
                        as values to provide a full path for the raw and
                        calibration frames. Optional.
        :type md5sums: :class:`dict`
        '''
        if isinstance(source, str):
            header = fits.open(source)[0].header
        elif isinstance(source, (fits.HDUList, list)):
            header = source[0].header
        elif isinstance(source, fits.PrimaryHDU):
            header = source.header
        elif isinstance(source, (fits.Header, dict)):
            header = source
        else:
            raise ValueError('Cannot assign type {0} to header'.format(
                    source.__class__.__name__))
        
        if recno < 0:
            for reccnt in range(1, 2**16):
                if 'HIERARCH ESO PRO REC{0} ID'.format(reccnt) not in header:
                    break
            recno += reccnt
        self.name = header['HIERARCH ESO PRO REC{0} ID'.format(recno)]
        self.product = header['HIERARCH ESO PRO CATG']
        self.orig_filename = header['PIPEFILE']
        pipe_id = header.get('HIERARCH ESO PRO REC{0} PIPE ID'.format(recno))
        if pipe_id:
            self.pipeline, version = pipe_id.split('/')
            num_version = 0
            for i in version.split('.'):
                num_version = num_version * 100 + int(i)
            self.version = (num_version, version)
        else:
            self.pipeline =  None
            self.version = None
        self.cpl_version = header.get('HIERARCH ESO PRO REC{0} DRS ID'.format(recno))
        self.md5sum = header.get('DATAMD5')
        if md5sums and self.md5sum in md5sums:
            self.orig_filename = md5sums[self.md5sum]
        self.md5sums = {}
        self.calib = ProcessingInfo._get_rec_keys(header, recno, 'CAL', 'CATG', 'NAME')
        for cat, md5 in ProcessingInfo._get_rec_keys(header, recno, 'CAL', 'CATG',
                                                     'DATAMD5').items():
            if isinstance(md5, list):
                for i, m in enumerate(md5):
                    if m is not None:
                        if md5sums and m in md5sums:
                            self.calib[cat][i] = md5sums[m]
                        self.md5sums[self.calib[cat][i]] = m
            elif md5 is not None:
                if md5sums and md5 in md5sums:
                    self.calib[cat] = md5sums[md5]
                self.md5sums[self.calib[cat]] = md5
        raw = ProcessingInfo._get_rec_keys(header, recno, 'RAW', 'CATG', 'NAME')
        if raw:
            self.tag = list(raw.keys())[0]
            self.raw = raw[self.tag]
            md5 = ProcessingInfo._get_rec_keys(header, recno, 'RAW', 'CATG',
                                               'DATAMD5')[self.tag]
            if isinstance(md5, list):
                for i, m in enumerate(md5):
                    if m is not None: 
                        if md5sums and m in md5sums:
                            self.raw[i] = md5sums[m]
                        self.md5sums[self.raw[i]] = m
            elif md5 is not None:
                if md5sums and md5 in md5sums:
                    self.raw = md5sums[md5]
                self.md5sums[self.raw] = md5
        else:
            self.tag = None
            self.raw = None
            self.input = None
        param = ProcessingInfo._get_rec_keys(header, recno, 'PARAM', 'NAME', 'VALUE')
        self.param = dict()
        for k,v in param.items():
            self.param[k] = ProcessingInfo._best_type(v)
            
    def create_recipe(self):
        '''Create a recipe and configure it with the parameters, calibration frames,
        and the input tag. The recipe version will be the latest available one.
        '''
        recipe = cpl.Recipe(self.name)
        recipe.param = self.param
        recipe.calib = self.calib
        recipe.tag = self.tag
        return recipe

    def create_script(self, scriptfile = sys.stdout):
        '''Create a sample script that creates the recipe, configures it with
        the parameters, calibration frames and input tags, and finally
        starts the recipe.
        '''
        if isinstance(scriptfile, str):
            scriptfile = file(scriptfile, mode='w')
        scriptfile.write('import cpl\n\n')
        scriptfile.write('# Recipe: {0}.{1}, Version {2}, CPL version {3}\n'.format(
                self.pipeline, self.name, self.version[1], self.cpl_version))
        scriptfile.write('{0} = cpl.Recipe({1}, version = {2})\n'.format(
                self.name, repr(self.name), repr(self.version[0])))
        scriptfile.write('\n# Parameters:\n')
        for k,v in self.param.items():
            scriptfile.write('{0}.param.{1} = {2}\n'.format(self.name, k, repr(v)))
        if self.calib:
            scriptfile.write('\n# Calibration frames:\n')
        for k,v in self.calib.items():
            scriptfile.write('{0}.calib.{1} = {2}\n'.format(self.name, k, repr(v)))
        scriptfile.write('\n# Process input frames:\n')
        scriptfile.write('{0}.tag = {1}\n'.format(self.name, repr(self.tag)))
        scriptfile.write('res = {0}({1})\n'.format(self.name, repr(self.raw)))
#        scriptfile.write('{0} = res.{1}\n'.format(self.product.lower(), self.product))
#        scriptfile.write('{0}.writeto({1})\n'.format(self.product.lower(),
#                                                     repr(self.orig_filename)))

    def __str__(self):
        s = 'Recipe: {0}, Version {1}, CPL version {2}\n'.format(
            self.name, self.version, self.cpl_version)
        s += 'Parameters:\n'
        for k,v in self.param.items():
            s += ' {0}.{1}.{2} = {3}\n'.format(self.pipeline, self.name, k, v)
        if self.calib:
            s += 'Calibration frames:\n'
        for k,v in self.calib.items():
            if isinstance(v, (str, unicode)):
                s += ' {0} {1}\n'.format(v,k)
            else:
                m = max(len(n) for n in v)
                for n in v:
                    s += ' {0:<{width}} {1}\n'.format(n, m, k, width = m)
        if self.raw is not None:
            s += 'Input frames:\n'
            if isinstance(self.raw, (str, unicode)):
                s += ' {0} {1}\n'.format(self.raw, self.tag)
            else:
                m = max(len(n) for n in self.raw)
                for n in self.raw:
                    s += ' {0:<{width}} {1}\n'.format(n, self.tag, width = m)
        return s

    def printinfo(self):
        '''Print the recipe information to standard output.
        '''
        print(str(self))

    @staticmethod
    def _get_rec_keys(header, recno, key, name, value):
        '''Get a dictionary of key/value pairs from the DFS section of the
        header.

        :param key: Common keyword for the value. Usually 'PARAM' for
                    parameters, 'RAW' for raw frames, and 'CAL' for
                    calibration frames.
        :type key: :class:`str`
        :param recno: Record number.
        :type recno: :class:`int`
        :param name: Header keyword (last part) for the name of each key
        :type name: :class:`str`
        :param value: Header keyword (last part) for the value of each key
        :type name: :class:`str`

        When the header

          HIERARCH ESO PRO REC1 PARAM1 NAME = 'nifu'
          HIERARCH ESO PRO REC1 PARAM1 VALUE = '1'
          HIERARCH ESO PRO REC1 PARAM2 NAME = 'combine'
          HIERARCH ESO PRO REC1 PARAM2 VALUE = 'median'

        is called with

          ProcessingInfo._get_rec_keys(1, 'PARAM', 'NAME', 'VALUE')

        the returned dictionary will contain the keys

          res['nifu'] = '1'
          res['combine'] = 'median'
        '''
        res = dict()
        for i in range(1, 2**16):
            try:
                prefix = 'HIERARCH ESO PRO REC{0} {1}{2}'.format(recno, key, i)
                k = header['{0} {1}'.format(prefix, name)]
                fn = header.get('{0} {1}'.format(prefix, value))
                if k not in  res:
                    res[k] = fn
                elif isinstance(res[k], list):
                    res[k].append(fn)
                else:
                    res[k] = [ res[k], fn ]
            except KeyError:
                break
        return res

    @staticmethod
    def _best_type(value):
        '''Convert the value to the best applicable type: :class:`int`,
        :class:`float`, :class:`bool` or :class`str`.

        :param value: Value to convert.
        :type value: :class:`str`
        '''
        for t in int, float:
            try:
                return t(value)
            except ValueError:
                pass
        return {'true':True, 'false':False}.get(value, value)

    @staticmethod
    def list(source, md5sums = None):
        '''Get a list of all `ProcessingInfo` objects in the FITS header. The
        list is sorted by the execution order.

        :param source: Object pointing to the result file header
        :type source: :class:`str` or :class:`astropy.io.fits.HDUList`
                      or :class:`astropy.io.fits.PrimaryHDU` or
                      :class:`astropy.io.fits.Header`
        '''
        pi = []
        for i in range(1, 2**16):
            try:
                pi.append(ProcessingInfo(source, i, md5sums))
            except KeyError:
                break
        return pi

if __name__ == '__main__':
    import sys

    for arg in sys.argv[1:]:
        print('{0}\nfile: {1}'.format('-' * 72, arg))
        pi = cpl.dfs.ProcessingInfo(arg)
        pi.printinfo()
