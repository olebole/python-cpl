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
        self.assertEqual(rrr.param.stropt.default, '')
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
        
        # Check that we can access the param as a dict
        # Note: comparing the params directly fails since 
        # the parameter is re-created on each call (to be changed some time)
        self.assertEqual(rrr.param.boolopt.name, rrr.param['boolopt'].name)

        # check that we can iterate over the params
        for p in rrr.param:
            self.assertTrue(isinstance(p, cpl.Parameter))
        pars = [p.name for p in rrr.param]
        self.assertEqual(len(pars), len(rrr.param))
        self.assertTrue('stropt' in pars)
        self.assertTrue('boolopt' in pars)

    def test_Recipe_exec_frames(self):
        '''test the frame handling during execution.'''
        rrr = cpl.Recipe('rrrecipe')
        rrr.temp_dir = '/tmp'

        # Both as keyword parameters
        res = rrr(raw_RRRECIPE_DOCATG_RAW = self.raw_frame, 
                  calib_FLAT = self.flat_frame)
        self.assertTrue(isinstance(res, cpl.Result))
        self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, pyfits.HDUList))
        self.assertTrue(abs(self.raw_frame[0].data - res.THE_PRO_CATG_VALUE[0].data).max() < 1e-6)

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
            results.append(rrr(self.raw_frame, param_stropt = 'i%i' % i))
        for i, res in enumerate(results):
            # check if we got the correct type
            self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, pyfits.HDUList))
            # check if we have the correct parameter
            self.assertEqual(res.THE_PRO_CATG_VALUE[0].header['HIERARCH ESO QC STROPT'],
                             'i%i' % i)
            # check if we have the correct input frame
            self.assertEqual(res.THE_PRO_CATG_VALUE[0].header['HIERARCH ESO RAW1 NR'], i)
            # check that the data were moved correctly
            self.assertTrue(abs(self.raw_frame[0].data - res.THE_PRO_CATG_VALUE[0].data).max() < 1e-6)
            
            
if __name__ == '__main__':
    unittest.main()
