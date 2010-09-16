import unittest
import numpy
import pyfits
import cpl

class TestRecipe(unittest.TestCase):

    def setUp(self):
        cpl.Recipe.path = '.'
        cpl.msg.level = 'off'

        size = (1024, 1024)
        self.raw_frame = pyfits.HDUList([
                pyfits.PrimaryHDU(numpy.random.random(size))])
        self.raw_frame[0].header.update('HIERARCH ESO DET DIT', 0.0)
        self.raw_frame[0].header.update('HIERARCH ESO PRO CATG', 
                                        'RRRECIPE_DOCATG_RAW')
        self.flat_frame = pyfits.HDUList([
                pyfits.PrimaryHDU(numpy.random.random(size))])

    def test_Recipe_list(self):
        l = cpl.Recipe.list()
        self.assertTrue(isinstance(l, list))
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0], ('rrrecipe', ['0.0.1']))

    def test_Recipe_common(self):
        rrr = cpl.Recipe('rrrecipe')
        self.assertEqual(rrr.name, 'rrrecipe')
        self.assertEqual(rrr.author, ('Firstname Lastname', 'flastname@eso.org'))
        self.assertTrue(isinstance(rrr.description[0], str))
        self.assertTrue(len(rrr.description[0]) > 0)
        self.assertTrue(isinstance(rrr.description[1], str))
        self.assertTrue(len(rrr.description[1]) > 0)
        
    def test_Recipe_params(self):
        rrr = cpl.Recipe('rrrecipe')

        # Check the string parameter
        self.assertTrue(isinstance(rrr.param.stropt, cpl.Parameter))
        self.assertEqual(rrr.param.stropt.name, 'stropt')
        self.assertEqual(rrr.param.stropt.context, 'iiinstrument.rrrecipe')
        self.assertEqual(rrr.param.stropt.default, None)
        self.assertEqual(rrr.param.stropt.value, None)
        self.assertEqual(rrr.param.stropt.range, None)
        self.assertEqual(rrr.param.stropt.sequence, None)
        rrr.param.stropt = 'more'
        self.assertEqual(rrr.param.stropt.value, 'more')
        del rrr.param.stropt 
        self.assertEqual(rrr.param.stropt.value, None)

        # Check the boolean parameter
        self.assertTrue(isinstance(rrr.param.boolopt, cpl.Parameter))
        self.assertEqual(rrr.param.boolopt.name, 'boolopt')
        self.assertEqual(rrr.param.boolopt.default, True)
        self.assertEqual(rrr.param.boolopt.value, None)
        rrr.param.boolopt = False
        self.assertEqual(rrr.param.boolopt.value, False)
        del rrr.param.boolopt 
        self.assertEqual(rrr.param.boolopt.value, None)
        
        # Check the float parameter
        self.assertTrue(isinstance(rrr.param.floatopt, cpl.Parameter))
        self.assertEqual(rrr.param.floatopt.name, 'floatopt')
        self.assertEqual(rrr.param.floatopt.default, 0.1)
        self.assertEqual(rrr.param.floatopt.value, None)
        rrr.param.floatopt = 1.1
        self.assertEqual(rrr.param.floatopt.value, 1.1)
        del rrr.param.floatopt 
        self.assertEqual(rrr.param.floatopt.value, None)

        # Check the int parameter
        self.assertTrue(isinstance(rrr.param.intopt, cpl.Parameter))
        self.assertEqual(rrr.param.intopt.name, 'intopt')
        self.assertEqual(rrr.param.intopt.default, 2)
        self.assertEqual(rrr.param.intopt.value, None)
        rrr.param.intopt = -1
        self.assertEqual(rrr.param.intopt.value, -1)
        del rrr.param.intopt 
        self.assertEqual(rrr.param.intopt.value, None)

        # Check the enum parameter
        self.assertTrue(isinstance(rrr.param.enumopt, cpl.Parameter))
        self.assertEqual(rrr.param.enumopt.name, 'enumopt')
        self.assertEqual(rrr.param.enumopt.default, 'first')
        self.assertEqual(rrr.param.enumopt.value, None)
        rrr.param.enumopt = 'second'
        self.assertEqual(rrr.param.enumopt.value, 'second')
        del rrr.param.enumopt 
        self.assertEqual(rrr.param.enumopt.value, None)
        def setenumoptinvalid():
            rrr.param.enumopt = 'invalid'
        self.assertRaises(ValueError, setenumoptinvalid)

        # Check the range parameter
        self.assertTrue(isinstance(rrr.param.rangeopt, cpl.Parameter))
        self.assertEqual(rrr.param.rangeopt.name, 'rangeopt')
        self.assertEqual(rrr.param.rangeopt.default, 0.1)
        self.assertEqual(rrr.param.rangeopt.value, None)
        rrr.param.rangeopt = 0.4
        self.assertEqual(rrr.param.rangeopt.value, 0.4)
        del rrr.param.rangeopt 
        self.assertEqual(rrr.param.rangeopt.value, None)
        def setrangeoptinvalid():
            rrr.param.rangeopt = 1.5
        self.assertRaises(ValueError, setrangeoptinvalid)

        # Check that we can access the param as a dict
        self.assertEqual(rrr.param.boolopt, rrr.param['boolopt'])
        self.assertEqual(rrr.param.boolopt, 
                         rrr.param['iiinstrument.rrrecipe.bool_option'])

        # check that we can iterate over the params
        for p in rrr.param:
            self.assertTrue(isinstance(p, cpl.Parameter))
        pars = [p.name for p in rrr.param]
        self.assertEqual(len(pars), len(rrr.param))
        self.assertTrue('stropt' in pars)
        self.assertTrue('boolopt' in pars)

        # Check that we can assign a dictionary with the short names
        rrr.param = { 'stropt':'dmore', 'boolopt':True }
        self.assertEqual(rrr.param.boolopt.value, True)
        self.assertEqual(rrr.param.stropt.value, 'dmore')

        # Check that we can assign a dictionary with the short names and string
        rrr.param = { 'stropt':'dmore', 'boolopt':'False' }
        self.assertEqual(rrr.param.boolopt.value, False)

        # Check that we can assign a dictionary with the long names
        rrr.param = { 'iiinstrument.rrrecipe.string_option':'dless', 
                      'iiinstrument.rrrecipe.float_option':1.5, 
                      'iiinstrument.rrrecipe.bool_option':True }
        self.assertEqual(rrr.param.stropt.value, 'dless')
        self.assertEqual(rrr.param.floatopt.value, 1.5)
        self.assertEqual(rrr.param.boolopt.value, True)

        # check that we can delete all params
        del rrr.param
        self.assertEqual(rrr.param.stropt.value, None)
        self.assertEqual(rrr.param.boolopt.value, None)

    def test_Recipe_calib(self):
        '''test the calib frame list'''
        rrr = cpl.Recipe('rrrecipe')

        rrr.calib.FLAT = 'flat.fits'
        self.assertEqual(rrr.calib.FLAT.frames, 'flat.fits')
        
        rrr.calib = { 'FLAT':'flat2.fits' }
        self.assertEqual(rrr.calib.FLAT.frames, 'flat2.fits')

    def test_Recipe_exec_frames(self):
        '''test the frame handling during execution.'''
        rrr = cpl.Recipe('rrrecipe')
        rrr.temp_dir = '/tmp'

        # Both as keyword parameters
        res = rrr(raw_RRRECIPE_DOCATG_RAW = self.raw_frame, 
                  calib_FLAT = self.flat_frame)
        self.assertTrue(isinstance(res, cpl.Result))
        self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, pyfits.HDUList))
        self.assertTrue(abs(self.raw_frame[0].data 
                            - res.THE_PRO_CATG_VALUE[0].data).max() < 1e-6)

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

    def test_Recipe_exec_param(self):
        '''test the parameter handling during execution.'''
        rrr = cpl.Recipe('rrrecipe')
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
        

    def test_Recipe_error(self):
        '''test the error handling'''
        rrr = cpl.Recipe('rrrecipe')
        rrr.temp_dir = '/tmp'
        rrr.tag = 'some_unknown_tag'
        self.assertRaises(cpl.CplError, rrr, self.raw_frame)

    def test_Recipe_parallel(self):
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

    def test_Esorex(self):
        # Test if we can read a SOF file
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
                           
        # test if we can convert a recipe's rc file
        rcfile = '# environment variable lambda_low.\n' \
        'muse.muse_sky.lambda_low=4.65e+03\n' \
        'muse.muse_sky.lambda_high=9.3e+03\n'
        self.assertEqual(cpl.esorex.load_rc(rcfile), 
                         { 'muse.muse_sky.lambda_low': '4.65e+03',
                           'muse.muse_sky.lambda_high': '9.3e+03'})
        
        # test if we can init from an esorex.rc file
        orig_level = cpl.msg.level
        orig_path = cpl.Recipe.path
        rcfile = 'esorex.caller.recipe-dir=/some/dir\n' \
        'esorex.caller.msg-level=debug'
        cpl.esorex.init(rcfile)
        self.assertEqual(cpl.msg.level, 'debug')
        self.assertEqual(cpl.Recipe.path, ['/some/dir'])
        cpl.msg.level = orig_level
        cpl.Recipe.path = orig_path
            
if __name__ == '__main__':
    unittest.main()
