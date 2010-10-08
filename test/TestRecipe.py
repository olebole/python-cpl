import unittest
import logging
import numpy
import pyfits
import cpl

class CplTestCase(unittest.TestCase):
    def setUp(self):
        cpl.Recipe.path = '.'
        cpl.msg.level = cpl.msg.OFF

class RecipeTestCase(CplTestCase):
    def setUp(self):
        CplTestCase.setUp(self)
        self.recipe = cpl.Recipe('rrrecipe')

class RecipeStatic(CplTestCase):
    def test_list(self):
        '''List available recipes'''
        l = cpl.Recipe.list()
        self.assertTrue(isinstance(l, list))
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0], ('rrrecipe', ['0.0.1']))

class RecipeCommon(RecipeTestCase):
    def test_name(self):
        '''Recipe name'''
        self.assertEqual(self.recipe.name, 'rrrecipe')

    def test_author(self):
        '''Author attribute'''
        self.assertEqual(self.recipe.author, 
                         ('Firstname Lastname', 'flastname@eso.org'))

    def test_description(self):
        '''Synopsis and description'''
        self.assertTrue(isinstance(self.recipe.description[0], str))
        self.assertTrue(len(self.recipe.description[0]) > 0)
        self.assertTrue(isinstance(self.recipe.description[1], str))
        self.assertTrue(len(self.recipe.description[1]) > 0)

    def test_copyright(self):
        '''Copyright'''
        self.assertTrue(isinstance(self.recipe.copyright, str))
        self.assertTrue(len(self.recipe.copyright) > 0)

class RecipeParams(RecipeTestCase):
    def test_str(self):
        '''String parameter'''
        self.assertTrue(isinstance(self.recipe.param.stropt, cpl.Parameter))
        self.assertEqual(self.recipe.param.stropt.name, 'stropt')
        self.assertEqual(self.recipe.param.stropt.context, 
                         'iiinstrument.rrrecipe')
        self.assertEqual(self.recipe.param.stropt.default, None)
        self.assertEqual(self.recipe.param.stropt.value, None)
        self.assertEqual(self.recipe.param.stropt.range, None)
        self.assertEqual(self.recipe.param.stropt.sequence, None)
        self.recipe.param.stropt = 'more'
        self.assertEqual(self.recipe.param.stropt.value, 'more')
        del self.recipe.param.stropt 
        self.assertEqual(self.recipe.param.stropt.value, None)

    def test_bool(self):
        '''Boolean parameter'''
        self.assertTrue(isinstance(self.recipe.param.boolopt, cpl.Parameter))
        self.assertEqual(self.recipe.param.boolopt.name, 'boolopt')
        self.assertEqual(self.recipe.param.boolopt.default, True)
        self.assertEqual(self.recipe.param.boolopt.value, None)
        self.recipe.param.boolopt = False
        self.assertEqual(self.recipe.param.boolopt.value, False)
        del self.recipe.param.boolopt 
        self.assertEqual(self.recipe.param.boolopt.value, None)
        
    def test_float(self):
        '''Float parameter'''
        self.assertTrue(isinstance(self.recipe.param.floatopt, cpl.Parameter))
        self.assertEqual(self.recipe.param.floatopt.name, 'floatopt')
        self.assertEqual(self.recipe.param.floatopt.default, 0.1)
        self.assertEqual(self.recipe.param.floatopt.value, None)
        self.recipe.param.floatopt = 1.1
        self.assertEqual(self.recipe.param.floatopt.value, 1.1)
        del self.recipe.param.floatopt 
        self.assertEqual(self.recipe.param.floatopt.value, None)

    def test_int(self):
        '''Integer parameter'''
        self.assertTrue(isinstance(self.recipe.param.intopt, cpl.Parameter))
        self.assertEqual(self.recipe.param.intopt.name, 'intopt')
        self.assertEqual(self.recipe.param.intopt.default, 2)
        self.assertEqual(self.recipe.param.intopt.value, None)
        self.recipe.param.intopt = -1
        self.assertEqual(self.recipe.param.intopt.value, -1)
        del self.recipe.param.intopt 
        self.assertEqual(self.recipe.param.intopt.value, None)

    def test_enum(self):
        '''Enumeration (string) parameter'''
        self.assertTrue(isinstance(self.recipe.param.enumopt, cpl.Parameter))
        self.assertEqual(self.recipe.param.enumopt.name, 'enumopt')
        self.assertEqual(self.recipe.param.enumopt.default, 'first')
        self.assertEqual(self.recipe.param.enumopt.value, None)
        self.recipe.param.enumopt = 'second'
        self.assertEqual(self.recipe.param.enumopt.value, 'second')
        del self.recipe.param.enumopt 
        self.assertEqual(self.recipe.param.enumopt.value, None)
        def setenumoptinvalid():
            self.recipe.param.enumopt = 'invalid'
        self.assertRaises(ValueError, setenumoptinvalid)

    def test_range(self):
        '''Range (float) parameter'''
        self.assertTrue(isinstance(self.recipe.param.rangeopt, cpl.Parameter))
        self.assertEqual(self.recipe.param.rangeopt.name, 'rangeopt')
        self.assertEqual(self.recipe.param.rangeopt.default, 0.1)
        self.assertEqual(self.recipe.param.rangeopt.value, None)
        self.recipe.param.rangeopt = 0.4
        self.assertEqual(self.recipe.param.rangeopt.value, 0.4)
        del self.recipe.param.rangeopt 
        self.assertEqual(self.recipe.param.rangeopt.value, None)
        def setrangeoptinvalid():
            self.recipe.param.rangeopt = 1.5
        self.assertRaises(ValueError, setrangeoptinvalid)

    def test_as_dict(self):
        '''Use the parameter list as a dictionary'''
        self.assertEqual(self.recipe.param.boolopt, 
                         self.recipe.param['boolopt'])
        self.assertEqual(self.recipe.param.boolopt, 
                         self.recipe.param['iiinstrument.rrrecipe.bool_option'])

    def test_dotted_par(self):
        '''Use a parameter that has a dot in its alias'''
        self.assertEqual(self.recipe.param.dot_opt, 
                         self.recipe.param['dot.opt'])
        self.assertEqual(self.recipe.param.dot_opt, 
                         self.recipe.param['iiinstrument.rrrecipe.dotted.opt'])

    def test_iterate(self):
        '''Iteration over all parameters'''
        for p in self.recipe.param:
            self.assertTrue(isinstance(p, cpl.Parameter))
        pars = [p.name for p in self.recipe.param]
        self.assertEqual(len(pars), len(self.recipe.param))
        self.assertTrue('stropt' in pars)
        self.assertTrue('boolopt' in pars)

    def test_set_dict(self):
        '''Assign a dictionary to the parameter list'''
        self.recipe.param = { 'stropt':'dmore', 'boolopt':True }
        self.assertEqual(self.recipe.param.boolopt.value, True)
        self.assertEqual(self.recipe.param.stropt.value, 'dmore')

        # Check that we can assign a dictionary with the short names and string
        self.recipe.param = { 'stropt':'dmore', 'boolopt':'False' }
        self.assertEqual(self.recipe.param.boolopt.value, False)

        # Check that we can assign a dictionary with the long names
        self.recipe.param = { 'iiinstrument.rrrecipe.string_option':'dless', 
                      'iiinstrument.rrrecipe.float_option':1.5, 
                      'iiinstrument.rrrecipe.bool_option':True }
        self.assertEqual(self.recipe.param.stropt.value, 'dless')
        self.assertEqual(self.recipe.param.floatopt.value, 1.5)
        self.assertEqual(self.recipe.param.boolopt.value, True)

    def test_delete(self):
        '''Delete all parameter values to reset to default'''
        self.recipe.param.boolopt.value = True
        self.recipe.param.stropt.value = 'something'
        del self.recipe.param
        self.assertEqual(self.recipe.param.stropt.value, None)
        self.assertEqual(self.recipe.param.boolopt.value, None)

    def test_dir(self):
        '''[TAB] completition. 
        This requires to have   the __dir__() method working.
        '''
        self.assertEqual(self.recipe.param.__dir__(), 
                         [ p.name.replace('.','_') for p in self.recipe.param ])

class RecipeCalib(RecipeTestCase):
    def test_set(self):
        '''Set a calibration frame'''
        self.recipe.calib.FLAT = 'flat.fits'
        self.assertEqual(self.recipe.calib.FLAT.frames, 'flat.fits')
        
    def test_set_dict(self):
        '''Assign a dictionary to the calibration frame list'''
        self.recipe.calib = { 'FLAT':'flat2.fits' }
        self.assertEqual(self.recipe.calib.FLAT.frames, 'flat2.fits')

    def test_del(self):
        '''Delete a calibration frame set'''
        self.recipe.calib.FLAT = 'flat.fits'
        del self.recipe.calib.FLAT
        try: 
            f = self.recipe.calib.FLAT.frames
        except:
            f = None
        self.assertEqual(f, None)

    def test_del_all(self):
        '''Delete all calibration frame sets'''
        self.recipe.calib.FLAT = 'flat.fits'
        del self.recipe.calib
        try: 
            f = self.recipe.calib.FLAT.frames
        except:
            f = None
        self.assertEqual(f, None)

    def test_dir(self):
        '''[TAB] completition. 
        This requires to have   the __dir__() method working.
        '''
        self.assertEqual(self.recipe.calib.__dir__(), 
                         [ f.tag for f in self.recipe.calib ])

class RecipeExec(CplTestCase):
    def setUp(self):
        CplTestCase.setUp(self)
        size = (1024, 1024)
        self.raw_frame = pyfits.HDUList([
                pyfits.PrimaryHDU(numpy.random.random_integers(0, 65000,
                                                               size))])
        self.raw_frame[0].header.update('HIERARCH ESO DET DIT', 0.0)
        self.raw_frame[0].header.update('HIERARCH ESO PRO CATG', 
                                        'RRRECIPE_DOCATG_RAW')
        self.flat_frame = pyfits.HDUList([
                pyfits.PrimaryHDU(numpy.random.random_integers(0, 65000,
                                                               size))])

    def test_frames(self):
        '''Raw and calibration frame handling.'''
        rrr = cpl.Recipe('rrrecipe')
        rrr.temp_dir = '/tmp'

        # Both as keyword parameters
        res = rrr(raw_RRRECIPE_DOCATG_RAW = self.raw_frame, 
                  calib_FLAT = self.flat_frame)
        self.assertTrue(isinstance(res, cpl.Result))
        self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, pyfits.HDUList))
        self.assertTrue(abs(self.raw_frame[0].data 
                            - res.THE_PRO_CATG_VALUE[0].data).max() == 0)

        # Set calibration frame in recipe, use raw tag keyword
        rrr.calib.FLAT = self.flat_frame
        res = rrr(raw_RRRECIPE_DOCATG_RAW = self.raw_frame)
        self.assertTrue(isinstance(res, cpl.Result))
        self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, pyfits.HDUList))

        # Use 'tag' parameter
        rrr.calib.FLAT = self.flat_frame
        res = rrr(self.raw_frame, tag = 'RRRECIPE_DOCATG_RAW')
        self.assertTrue(isinstance(res, cpl.Result))
        self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, pyfits.HDUList))

        # Explicitely set 'tag' attribute
        rrr.tag = 'RRRECIPE_DOCATG_RAW'
        res = rrr(self.raw_frame)
        self.assertTrue(isinstance(res, cpl.Result))
        self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, pyfits.HDUList))

        # Use 1-element list as input --> we want a list back
        rrr.tag = 'RRRECIPE_DOCATG_RAW'
        res = rrr([self.raw_frame])
        self.assertTrue(isinstance(res, cpl.Result))
        self.assertFalse(isinstance(res.THE_PRO_CATG_VALUE, pyfits.HDUList))
        self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, list))

        # Use longer as input --> since we only get back one image, it is
        # assumed to be a 'master', and we get back a plain frame
        rrr.tag = 'RRRECIPE_DOCATG_RAW'
        res = rrr([self.raw_frame, self.raw_frame])
        self.assertTrue(isinstance(res, cpl.Result))
        self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, pyfits.HDUList))

    def test_param(self):
        '''Parameter handling'''
        rrr = cpl.Recipe('rrrecipe', threaded = True)
        rrr.temp_dir = '/tmp'
        rrr.tag = 'RRRECIPE_DOCATG_RAW'

        # Test setting the string param via keyword arg
        res = rrr(self.raw_frame, param_stropt = 'more').THE_PRO_CATG_VALUE
        self.assertEqual(res[0].header['HIERARCH ESO QC STROPT'], 'more')

        # Test setting the string param via recipe setting
        rrr.param.stropt = 'more'
        res = rrr(self.raw_frame).THE_PRO_CATG_VALUE
        self.assertEqual(res[0].header['HIERARCH ESO QC STROPT'], 'more')

        # Test overwriting the string param via recipe setting
        rrr.param.stropt = 'more'
        res = rrr(self.raw_frame, param_stropt = 'less').THE_PRO_CATG_VALUE
        self.assertEqual(res[0].header['HIERARCH ESO QC STROPT'], 'less')

        # Test all other parameter types
        rrr.param.boolopt = False
        rrr.param.intopt = 123
        rrr.param.floatopt = -0.25
        rrr.param.enumopt = 'third'
        rrr.param.rangeopt = 0.125
        res = rrr(self.raw_frame).THE_PRO_CATG_VALUE
        self.assertEqual(res[0].header['HIERARCH ESO QC BOOLOPT'], False)
        self.assertEqual(res[0].header['HIERARCH ESO QC INTOPT'], 123)
        self.assertEqual(res[0].header['HIERARCH ESO QC FLOATOPT'], -0.25)
        self.assertEqual(res[0].header['HIERARCH ESO QC ENUMOPT'], 'third')
        self.assertEqual(res[0].header['HIERARCH ESO QC RANGEOPT'], 0.125)
        

    def test_error(self):
        '''Error handling'''
        rrr = cpl.Recipe('rrrecipe')
        rrr.temp_dir = '/tmp'
        rrr.tag = 'some_unknown_tag'
        self.assertRaises(cpl.CplError, rrr, self.raw_frame)

    def test_parallel(self):
        '''Parallel execution'''
        rrr = cpl.Recipe('rrrecipe', threaded = True)
        rrr.temp_dir = '/tmp'
        rrr.tag = 'RRRECIPE_DOCATG_RAW'
        results = list()
        for i in range(20):
            # mark each frame so that we can see their order
            self.raw_frame[0].header.update('HIERARCH ESO RAW1 NR', i)
            results.append(rrr(self.raw_frame, param_intopt = i))
        for i, res in enumerate(results):
            # check if we got the correct type
            self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, pyfits.HDUList))
            # check if we have the correct parameter
            self.assertEqual(res.THE_PRO_CATG_VALUE[0].header[
                    'HIERARCH ESO QC INTOPT'], i)
            # check if we have the correct input frame
            self.assertEqual(res.THE_PRO_CATG_VALUE[0].header[
                    'HIERARCH ESO RAW1 NR'], i)
            # check that the data were moved correctly
            self.assertTrue(abs(self.raw_frame[0].data 
                                - res.THE_PRO_CATG_VALUE[0].data).max() < 1e-6)

class RecipeEsorex(CplTestCase):
    def test_read_sof(self):
        '''Read a SOF file'''
        soffile = 'geometry_table1.fits GEOMETRY_TABLE\n' \
            'geometry_table2.fits GEOMETRY_TABLE\n' \
            'MASTER_BIAS-01.fits MASTER_BIAS\n' \
            'MASTER_FLAT-01.fits MASTER_FLAT\n' \
            '#sky_fullmoon_1.fits          SKY\n' \
            'sky_fullmoon_2.fits          SKY\n'
        self.assertEqual(cpl.esorex.load_sof(soffile),
                         { 'GEOMETRY_TABLE': ['geometry_table1.fits',
                                              'geometry_table2.fits' ],
                           'MASTER_BIAS': 'MASTER_BIAS-01.fits',
                           'MASTER_FLAT': 'MASTER_FLAT-01.fits',
                           'SKY': 'sky_fullmoon_2.fits' })
                           
    def test_read_rc(self):
        '''Read an EsoRec .rc file'''
        rcfile = '# environment variable lambda_low.\n' \
        'muse.muse_sky.lambda_low=4.65e+03\n' \
        'muse.muse_sky.lambda_high=9.3e+03\n'
        self.assertEqual(cpl.esorex.load_rc(rcfile), 
                         { 'muse.muse_sky.lambda_low': '4.65e+03',
                           'muse.muse_sky.lambda_high': '9.3e+03'})
        
    def test_esorex_init(self):
        '''Init CPL from an esorex.rc file'''
        rcfile = 'esorex.caller.recipe-dir=/some/dir\n' \
        'esorex.caller.msg-level=debug'
        cpl.esorex.init(rcfile)
        self.assertEqual(cpl.msg.level, cpl.msg.DEBUG)
        self.assertEqual(cpl.Recipe.path, ['/some/dir'])

class RecipeLog(RecipeTestCase):
    def setUp(self):
        RecipeTestCase.setUp(self)
        self.recipe.temp_dir = '/tmp'
        self.recipe.tag = 'RRRECIPE_DOCATG_RAW'
        size = (1024, 1024)
        self.raw_frame = pyfits.HDUList([
                pyfits.PrimaryHDU(numpy.random.random_integers(0, 65000,
                                                               size))])
        self.raw_frame[0].header.update('HIERARCH ESO DET DIT', 0.0)
        self.raw_frame[0].header.update('HIERARCH ESO PRO CATG', 
                                        'RRRECIPE_DOCATG_RAW')

    def test_logging(self):
        '''Injection of CPL messages into the python logging system'''
        logs = list()

        class THandler(logging.Handler):
            def __init__(self, l):
                logging.Handler.__init__(self)
                self.logs = l

            def emit(self, record):
                self.logs.append(record)

        # Test the conventional log name
        logging.getLogger('cpl.rrrecipe').addHandler(THandler(logs))
        self.recipe(self.raw_frame)
        # check that the logs are not empty
        self.assertNotEqual(len(logs), 0)
        funcnames = set()
        lognames = set()
        for r in logs:
            # Check that we saved the right class
            self.assertTrue(isinstance(r, logging.LogRecord))
            # Check that a message was provided
            self.assertNotEqual(r.msg, None)
            # Check that a function name was provided
            self.assertNotEqual(r.funcName, None)
            funcnames.add(r.funcName)
            lognames.add(r.name)
        # Check that we had at least one expected entry
        self.assertTrue('cpl_dfs_product_save' in funcnames)
        self.assertTrue('cpl.rrrecipe.cpl_dfs_product_save' in lognames)
        
        # Test if we can specify the log name on recipe's call
        logs = list()
        logging.getLogger('othername').addHandler(THandler(logs))
        self.recipe(self.raw_frame, logname = 'othername')
        self.assertNotEqual(len(logs), 0)

    def test_result(self):
        ''''log' attribute of the result object'''
        res = self.recipe(self.raw_frame)
        # Check that we get a not-empty list back
        self.assertTrue(isinstance(res.log, list))
        self.assertNotEqual(len(res.log), 0)
        self.assertTrue(isinstance(res.log[0], logging.LogRecord))

        # Check that we can read debug messages
        self.assertNotEqual(len(res.log.debug), 0)
        self.assertTrue(isinstance(res.log.debug[0], str))
        # Check that we can read info messages
        self.assertNotEqual(len(res.log.info), 0)
        self.assertTrue(isinstance(res.log.info[0], str))
        # Check that we can read warning messages
        self.assertNotEqual(len(res.log.warning), 0)
        self.assertTrue(isinstance(res.log.warning[0], str))
        # Check that there were no error messages
        self.assertEqual(len(res.log.error), 0)

    def test_error(self):
        ''''log' attribute of the CplError object'''
        try:
            self.recipe('test.fits')
        except cpl.CplError as res:
            pass
        # Check that we get a not-empty list back
        self.assertTrue(isinstance(res.log, list))
        self.assertNotEqual(len(res.log), 0)
        self.assertTrue(isinstance(res.log[0], logging.LogRecord))
        # Check that we can read debug messages
        self.assertNotEqual(len(res.log.debug), 0)
        self.assertTrue(isinstance(res.log.debug[0], str))
        # Check that we can read info messages
        self.assertNotEqual(len(res.log.info), 0)
        self.assertTrue(isinstance(res.log.info[0], str))
        # Check that we can read warning messages
        self.assertNotEqual(len(res.log.warning), 0)
        self.assertTrue(isinstance(res.log.warning[0], str))
        # Check that we can read error messages
        self.assertNotEqual(len(res.log.error), 0)
        self.assertTrue(isinstance(res.log.error[0], str))
        
if __name__ == '__main__':
    unittest.main()
