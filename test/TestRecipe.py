import logging
import os
import shutil
import tempfile
import unittest

import numpy
try:
    from astropy.io import fits
except:
    import pyfits as fits
import cpl
cpl.Recipe.memory_mode = 0

recipe_name = 'rtest'
raw_tag = 'RRRECIPE_DOCATG_RAW'

def create_recipe(name):
    cname = name + ".c"
    oname = name + '.o'
    soname = name + '.so'
    env = {
        'CC':  os.getenv("CC", "gcc"),
        'CPPFLAGS': os.getenv("CPPFLAGS", ""),
        'CFLAGS': os.getenv("CFLAGS", ""),
        'LDFLAGS': os.getenv("LDFLAGS", ""),
        'LIBS': "-lcplcore -lcpldfs",
        'cname': cname,
        'oname': oname,
        'soname': soname,
    }
    if (not os.path.exists(soname) or
        os.path.getmtime(soname) <= os.path.getmtime(cname)):
        os.system("{CC} {CPPFLAGS} {CFLAGS} -fPIC -c {cname}".format(**env))
        os.system("{CC} {LDFLAGS} -shared -o {soname} {oname} {LIBS}".format(**env))
        os.remove(oname)
        
class CplTestCase(unittest.TestCase):
    def setUp(self):
        cpl.Recipe.path = os.path.dirname(os.path.abspath(__file__))

class RecipeTestCase(CplTestCase):
    def setUp(self):
        CplTestCase.setUp(self)
        self.temp_dir = tempfile.mkdtemp()
        self.recipe = cpl.Recipe(recipe_name)
        self.recipe.temp_dir = self.temp_dir
        self.recipe.tag = raw_tag
        self.image_size = (16, 16)
        self.raw_frame = fits.HDUList([
                fits.PrimaryHDU(numpy.random.random_integers(0, 65000,
                                                               self.image_size))])
        self.raw_frame[0].header['HIERARCH ESO DET DIT'] = 0.0
        self.raw_frame[0].header['HIERARCH ESO PRO CATG'] = raw_tag

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

class RecipeStatic(CplTestCase):
    def test_list(self):
        '''List available recipes'''
        l = cpl.Recipe.list()
        self.assertTrue(isinstance(l, list))
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0], (recipe_name, ['0.0.1']))

    def test_create_recipe(self):
        '''Create a recipe specified by its name'''
        recipe = cpl.Recipe(recipe_name)
        self.assertTrue(isinstance(recipe, cpl.Recipe))

    def test_create_recipe_version(self):
        '''Create a recipe specified by its name and version'''
        recipe = cpl.Recipe(recipe_name, version = '0.0.1')
        self.assertTrue(isinstance(recipe, cpl.Recipe))        

    def test_create_recipe_wrong_name(self):
        '''Create a recipe specified by a wrong name'''
        self.assertRaises(IOError, cpl.Recipe, 'wrongname')

    def test_create_recipe_wrong_version(self):
        '''Create a recipe specified by a wrong version'''
        self.assertRaises(IOError, cpl.Recipe, recipe_name, version='0.0.10')

    def test_create_recipe_filename(self):
        '''Create a recipe specified by a the name and the filename'''
        recipe = cpl.Recipe(recipe_name, filename = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),'rtest.so'))
        self.assertTrue(isinstance(recipe, cpl.Recipe))

    def test_create_recipe_wrong_filename(self):
        '''Create a recipe specified by a wrong filename'''
        self.assertRaises(IOError, cpl.Recipe, recipe_name, 
                          filename = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'iiinstrumentp', 'recipes', '.libs', 'rtest.o'))

class RecipeCommon(RecipeTestCase):
    def test_name(self):
        '''Recipe name'''
        self.assertEqual(self.recipe.__name__, recipe_name)

    def test_author(self):
        '''Author attribute'''
        self.assertEqual(self.recipe.__author__, 'Ole Streicher')

    def test_email(self):
        '''Author attribute'''
        self.assertEqual(self.recipe.__email__, 'python-cpl@liska.ath.cx')

    def test_description(self):
        '''Synopsis and description'''
        self.assertTrue(isinstance(self.recipe.description[0], str))
        self.assertTrue(len(self.recipe.description[0]) > 0)
        self.assertTrue(isinstance(self.recipe.description[1], str))
        self.assertTrue(len(self.recipe.description[1]) > 0)

    def test_copyright(self):
        '''Copyright'''
        self.assertTrue(isinstance(self.recipe.__copyright__, str))
        self.assertTrue(len(self.recipe.__copyright__) > 0)

class RecipeParams(RecipeTestCase):
    def test_str(self):
        '''String parameter'''
        self.assertTrue(isinstance(self.recipe.param.stropt, cpl.Parameter))
        self.assertEqual(self.recipe.param.stropt.name, 'stropt')
        self.assertEqual(self.recipe.param.stropt.context, 
                         'iiinstrument.rtest')
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
                         self.recipe.param['iiinstrument.rtest.bool_option'])

    def test_dotted_par(self):
        '''Use a parameter that has a dot in its alias'''
        self.assertEqual(self.recipe.param.dot.opt,
                         self.recipe.param.dot['opt'])
        self.assertEqual(self.recipe.param.dot.opt,
                         self.recipe.param['dot.opt'])
        self.assertEqual(self.recipe.param.dot.opt,
                         self.recipe.param['iiinstrument.rtest.dotted.opt'])

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
        self.recipe.param = { 'iiinstrument.rtest.string_option':'dless', 
                      'iiinstrument.rtest.float_option':1.5, 
                      'iiinstrument.rtest.bool_option':True }
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
        self.assertEqual(set(self.recipe.param.__dir__()),
                         set(p.name if '.' not in p.name
                             else p.name.split('.', 1)[0]
                             for p in self.recipe.param
                             ))

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
        f = self.recipe.calib.FLAT.frames
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
        self.assertEqual(set(self.recipe.calib.__dir__()),
                         set(f.tag for f in self.recipe.calib))

class RecipeExec(RecipeTestCase):
    def setUp(self):
        RecipeTestCase.setUp(self)
        self.flat_frame = fits.HDUList([
                fits.PrimaryHDU(numpy.random.random_integers(0, 65000,
                                                             self.image_size))])

    def test_frames_keyword_dict(self):
        '''Raw and calibration frames specified as keyword dict'''
        self.recipe.tag = None
        res = self.recipe(raw = {'RRRECIPE_DOCATG_RAW': self.raw_frame },
                          calib = { 'FLAT':self.flat_frame })
        self.assertTrue(isinstance(res, cpl.Result))
        self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, fits.HDUList))
        self.assertTrue(abs(self.raw_frame[0].data 
                            - res.THE_PRO_CATG_VALUE[0].data).max() == 0)
        try:
            res.THE_PRO_CATG_VALUE.close()
        except:
            pass

    def test_frames_keyword_calib(self):
        '''Raw frame specified as keyword, calibration frame set in recipe'''
        self.recipe.tag = None
        self.recipe.calib.FLAT = self.flat_frame
        res = self.recipe({'RRRECIPE_DOCATG_RAW':self.raw_frame})
        self.assertTrue(isinstance(res, cpl.Result))
        self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, fits.HDUList))
        try:
            res.THE_PRO_CATG_VALUE.close()
        except:
            pass

    def test_frames_tag_keyword(self):
        '''The 'tag' parameter'''
        self.recipe.tag = None
        self.recipe.calib.FLAT = self.flat_frame
        res = self.recipe(self.raw_frame, tag = raw_tag)
        self.assertTrue(isinstance(res, cpl.Result))
        self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, fits.HDUList))
        try:
            res.THE_PRO_CATG_VALUE.close()
        except:
            pass

    def test_frames_tag_attribute(self):
        '''The 'tag' attribute'''
        self.recipe.tag = raw_tag
        res = self.recipe(self.raw_frame)
        self.assertTrue(isinstance(res, cpl.Result))
        self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, fits.HDUList))
        try:
            res.THE_PRO_CATG_VALUE.close()
        except:
            pass

    def test_frames_one_element_input_list(self):
        '''Use 1-element list as input'''
        # --> we want a list back'''
        res = self.recipe([self.raw_frame])
        self.assertTrue(isinstance(res, cpl.Result))
        self.assertFalse(isinstance(res.THE_PRO_CATG_VALUE, fits.HDUList))
        self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, list))
        try:
            res.THE_PRO_CATG_VALUE[0].close()
        except:
            pass

    def test_frames_many_element_input_list(self):
        '''Use multiple files as input'''
        # --> since we only get back one image, it is
        # assumed to be a 'master', and we get back a plain frame'''
        res = self.recipe([self.raw_frame, self.raw_frame])
        self.assertTrue(isinstance(res, cpl.Result))
        self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, fits.HDUList))
        try:
            res.THE_PRO_CATG_VALUE.close()
        except:
            pass

    def test_output_dir_attribute(self):
        '''Write an output dir specified as attribute'''
        output_dir = os.path.join(self.temp_dir, 'out')
        self.recipe.output_dir = output_dir
        res = self.recipe(self.raw_frame)
        self.assertTrue(isinstance(res, cpl.Result))
        self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, str))
        self.assertEqual(os.path.basename(res.THE_PRO_CATG_VALUE), 
                         'rtest.fits')
        self.assertTrue(os.path.isdir(output_dir))
        self.assertTrue(os.path.isfile(res.THE_PRO_CATG_VALUE))
        hdu = fits.open(res.THE_PRO_CATG_VALUE)
        self.assertTrue(isinstance(hdu, fits.HDUList))
        try:
            hdu.close()
        except:
            pass

    def test_output_dir_keyword(self):
        '''Write an output dir specified as call keyword arg'''
        output_dir = os.path.join(self.temp_dir, 'out')
        res = self.recipe(self.raw_frame, output_dir = output_dir)
        self.recipe.output_dir = output_dir
        res = self.recipe(self.raw_frame)
        self.assertTrue(os.path.isdir(output_dir))
        self.assertTrue(isinstance(res, cpl.Result))
        self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, str))
        self.assertEqual(os.path.basename(res.THE_PRO_CATG_VALUE), 
                         'rtest.fits')
        self.assertTrue(os.path.isfile(res.THE_PRO_CATG_VALUE))
        hdu = fits.open(res.THE_PRO_CATG_VALUE)
        self.assertTrue(isinstance(hdu, fits.HDUList))
        try:
            hdu.close()
        except:
            pass

    def test_param_default(self):
        '''Test default parameter settings'''
        res = self.recipe(self.raw_frame).THE_PRO_CATG_VALUE
        self.assertEqual(res[0].header['HIERARCH ESO QC STROPT'].strip(),
                         self.recipe.param.stropt.default or '')
        self.assertEqual(res[0].header['HIERARCH ESO QC BOOLOPT'],
                         self.recipe.param.boolopt.default)
        self.assertEqual(res[0].header['HIERARCH ESO QC INTOPT'],
                         self.recipe.param.intopt.default)
        self.assertEqual(res[0].header['HIERARCH ESO QC FLOATOPT'],
                         self.recipe.param.floatopt.default)
        self.assertEqual(res[0].header['HIERARCH ESO QC ENUMOPT'],
                         self.recipe.param.enumopt.default)
        self.assertEqual(res[0].header['HIERARCH ESO QC RANGEOPT'],
                         self.recipe.param.rangeopt.default)
        try:
            res.close()
        except:
            pass

    def test_param_keyword_dict(self):
        '''Parameter handling via keyword dict'''
        res = self.recipe(self.raw_frame, 
                          param = { 'stropt':'more' }).THE_PRO_CATG_VALUE
        self.assertEqual(res[0].header['HIERARCH ESO QC STROPT'], 'more')
        try:
            res.close()
        except:
            pass

    def test_param_keyword_dict_wrong(self):
        '''Parameter handling via keyword dict'''
        self.assertRaises(KeyError, self.recipe,
                          self.raw_frame, param = { 'wrong':True })

    def test_param_setting(self):
        '''Parameter handling via recipe setting'''
        self.recipe.param.stropt = 'more'
        with self.recipe(self.raw_frame).THE_PRO_CATG_VALUE as res:
            self.assertEqual(res[0].header['HIERARCH ESO QC STROPT'], 'more')

    def test_param_delete(self):
        '''Delete a parameter in a second run after setting it'''
        self.recipe.param.intopt = 123
        with self.recipe(self.raw_frame).THE_PRO_CATG_VALUE as res:
            pass
        del self.recipe.param.intopt
        with self.recipe(self.raw_frame).THE_PRO_CATG_VALUE as res:
            self.assertEqual(res[0].header['HIERARCH ESO QC INTOPT'], 2)

    def test_param_overwrite(self):
        '''Overwrite the recipe setting param via via keyword arg'''
        self.recipe.param.stropt = 'more'
        res = self.recipe(self.raw_frame, param = {'stropt':'less'}).THE_PRO_CATG_VALUE
        self.assertEqual(res[0].header['HIERARCH ESO QC STROPT'], 'less')

    def test_param_types(self):
        '''Parameter types'''
        self.recipe.param.stropt = 'more'
        self.recipe.param.boolopt = False
        self.recipe.param.intopt = 123
        self.recipe.param.floatopt = -0.25
        self.recipe.param.enumopt = 'third'
        self.recipe.param.rangeopt = 0.125
        with self.recipe(self.raw_frame).THE_PRO_CATG_VALUE as res:
            self.assertEqual(res[0].header['HIERARCH ESO QC STROPT'], 'more')
            self.assertEqual(res[0].header['HIERARCH ESO QC BOOLOPT'], False)
            self.assertEqual(res[0].header['HIERARCH ESO QC INTOPT'], 123)
            self.assertEqual(res[0].header['HIERARCH ESO QC FLOATOPT'], -0.25)
            self.assertEqual(res[0].header['HIERARCH ESO QC ENUMOPT'], 'third')
            self.assertEqual(res[0].header['HIERARCH ESO QC RANGEOPT'], 0.125)
        
    def test_disabled(self):
        '''Parameter with CLI disabled'''
        self.assertFalse(self.recipe.param.disabled.enabled[0])
        self.assertTrue(self.recipe.param.intopt.enabled[0])
#        self.recipe.param.disabled = 0.2
#        res = self.recipe(self.raw_frame)
#        self.assertEqual(res[0].header['HIERARCH ESO QC DISABLED'], 0.2)
#        try:
#            res.close()
#        except:
#            pass

    def test_environment_setting(self):
        '''Additional environment parameter via recipe setting'''
        self.recipe.env['TESTENV'] = 'unkk'
        with self.recipe(self.raw_frame).THE_PRO_CATG_VALUE as res:
            self.assertEqual(res[0].header['HIERARCH ESO QC TESTENV'], 'unkk')

    def test_environment_keyword(self):
        '''Additional environment parameter via recipe call keyword'''
        with self.recipe(self.raw_frame, 
                         env = {'TESTENV':'kknu'}).THE_PRO_CATG_VALUE as res:
            self.assertEqual(res[0].header['HIERARCH ESO QC TESTENV'], 'kknu')

    def test_error(self):
        '''Error handling'''
        self.recipe.tag = 'some_unknown_tag'
        self.assertRaises(cpl.CplError, self.recipe, self.raw_frame)

    def test_parallel(self):
        '''Parallel execution'''
        results = list()
        for i in range(20):
            # mark each frame so that we can see their order
            self.raw_frame[0].header['HIERARCH ESO RAW1 NR'] = i
            results.append(self.recipe(self.raw_frame, param = {'intopt':i},
                                       env = {'TESTENV':('knu%02i' % i)},
                                       threaded = True))
        for i, res in enumerate(results):
            # check if we got the correct type
            self.assertTrue(isinstance(res.THE_PRO_CATG_VALUE, fits.HDUList))
            # check if we have the correct parameter
            self.assertEqual(res.THE_PRO_CATG_VALUE[0].header[
                    'HIERARCH ESO QC INTOPT'], i)
            # check if we have the correct environment
            self.assertEqual(res.THE_PRO_CATG_VALUE[0].header[
                    'HIERARCH ESO QC TESTENV'], ('knu%02i' % i))
            # check if we have the correct input frame
            self.assertEqual(res.THE_PRO_CATG_VALUE[0].header[
                    'HIERARCH ESO RAW1 NR'], i)
            # check that the data were moved correctly
            self.assertTrue(abs(self.raw_frame[0].data 
                                - res.THE_PRO_CATG_VALUE[0].data).max() < 1e-6)
            try:
                res.THE_PRO_CATG_VALUE.close()
            except:
                pass

    def test_error_parallel(self):
        '''Error handling in parallel execution'''
        self.recipe.tag = 'some_unknown_tag'
        res = self.recipe(self.raw_frame, threaded = True)
        def get(x):
            return x.THE_PRO_CATG_VALUE
        self.assertRaises(cpl.CplError, get, res)

    def test_md5sum_result(self):
        '''MD5sum of the result file'''
        self.recipe.tag = raw_tag
        res = self.recipe(self.raw_frame)
        key = 'DATAMD5'
        md5sum = res.THE_PRO_CATG_VALUE[0].header[key]
        try:
            res.THE_PRO_CATG_VALUE.close()
        except:
            pass
        self.assertNotEqual(md5sum, 'Not computed')
        self.assertEqual(len(md5sum), 
                         len('9d123996fa9a7bda315d07e063043454'))

    def test_md5sum_calib(self):
        '''Created MD5sum for a HDUList calib file'''
        self.recipe.tag = raw_tag
        self.recipe.calib.FLAT = self.flat_frame
        res = self.recipe(self.raw_frame)
        key = 'HIERARCH ESO PRO REC1 CAL1 DATAMD5'
        md5sum = res.THE_PRO_CATG_VALUE[0].header[key]
        try:
            res.THE_PRO_CATG_VALUE.close()
        except:
            pass
        self.assertNotEqual(md5sum, 'Not computed')
        self.assertEqual(len(md5sum), 
                         len('9d123996fa9a7bda315d07e063043454'))

class RecipeCrashing(RecipeTestCase):
    def test_corrupted(self):
        '''Handling of recipe crashes because of corrupted memory'''
        self.recipe.param.crashing = 'free'
        self.assertRaises(cpl.RecipeCrash, self.recipe, self.raw_frame)

    def test_segfault(self):
        '''Handling of recipe crashes because of segmentation fault'''
        self.recipe.param.crashing = 'segfault'
        self.assertRaises(cpl.RecipeCrash, self.recipe, self.raw_frame)

    def test_cleanup_after_crash(self):
        '''Test that a second run after a crash will succeed'''
        output_dir = os.path.join(self.temp_dir, 'out')
        self.recipe.output_dir = output_dir
        self.recipe.param.crashing = 'segfault'
        self.assertRaises(cpl.RecipeCrash, self.recipe, self.raw_frame)
        del self.recipe.param.crashing
        self.recipe(self.raw_frame)

class RecipeRes(RecipeTestCase):
    def setUp(self):
        RecipeTestCase.setUp(self)
        self.res = self.recipe(self.raw_frame)

    def tearDown(self):
        try:
            res.THE_PRO_CATG_VALUE.close()
        except:
            pass

    def test_attribute(self):
        '''The result as an attribute'''
        self.assertTrue(isinstance(self.res.THE_PRO_CATG_VALUE, 
                                   fits.HDUList))

    def test_dict(self):
        '''The result as an attribute'''
        self.assertTrue(isinstance(self.res['THE_PRO_CATG_VALUE'], 
                                   fits.HDUList))

    def test_len(self):
        '''Length of the result'''
        self.assertEqual(len(self.res), 1)

    def test_iter(self):
        '''Iterate over the result'''
        for tag, hdu in self.res:
            self.assertEqual(tag, 'THE_PRO_CATG_VALUE')
            self.assertTrue(isinstance(hdu, fits.HDUList))

class RecipeEsorex(CplTestCase):
    def setUp(self):
        CplTestCase.setUp(self)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        CplTestCase.tearDown(self)
        cpl.esorex.msg.level = cpl.esorex.msg.OFF
        cpl.esorex.log.level = cpl.esorex.msg.OFF
        shutil.rmtree(self.temp_dir)

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
        rcfile = '''esorex.caller.recipe-dir=/some/dir
        esorex.caller.msg-level=debug
        esorex.caller.log-level=info
        esorex.caller.log-dir=%s
        esorex.caller.log-file=some.log''' % self.temp_dir
        cpl.esorex.init(rcfile)
        self.assertEqual(cpl.esorex.msg.level, cpl.esorex.msg.DEBUG)
        self.assertEqual(cpl.esorex.log.level, cpl.esorex.msg.INFO)
        self.assertEqual(cpl.esorex.log.dir, self.temp_dir)
        self.assertEqual(cpl.esorex.log.filename, 'some.log')
        self.assertEqual(cpl.Recipe.path, ['/some/dir'])

    def test_esorex_log(self):
        '''Write a logfile controlled by the convienence logger'''
        dirname = os.path.join(self.temp_dir, 'log')
        filename = 'python-cpl.log'
        log_msg = 'Esorex convienence log'
        os.mkdir(dirname)
        cpl.esorex.log.dir = dirname
        cpl.esorex.log.filename = filename
        cpl.esorex.log.level = cpl.esorex.log.INFO
        filename = os.path.join(dirname, filename)
        logging.getLogger('cpl').info(log_msg)
        self.assertTrue(os.path.exists(filename))
        logfile = open(filename)
        log_content = logfile.read()
        logfile.close()
        self.assertTrue(log_msg in log_content)
        self.assertTrue('INFO' in log_content)

    def test_esorex_log_off(self):
        '''Switch the logfile off after writing something'''
        dirname = os.path.join(self.temp_dir, 'log')
        filename = 'python-cpl_off.log'
        log_msg = 'Esorex convienence log'
        os.mkdir(dirname)
        cpl.esorex.log.dir = dirname
        cpl.esorex.log.filename = 'python-cpl_debug.log'
        cpl.esorex.log.level = 'debug'
        logging.getLogger('cpl').debug(log_msg)
        cpl.esorex.log.filename = filename
        cpl.esorex.log.level = 'off'
        logging.getLogger('cpl').debug(log_msg)
        filename = os.path.join(dirname, filename)
        logfile = open(filename)
        log_content = logfile.read()
        logfile.close()
        self.assertEqual(len(log_content), 0)

class RecipeLog(RecipeTestCase):
    def setUp(self):
        RecipeTestCase.setUp(self)
        self.handler = RecipeLog.THandler()
        logging.getLogger('cpl.rtest').addHandler(self.handler)
        self.other_handler = RecipeLog.THandler()
        logging.getLogger('othername').addHandler(self.other_handler)

    def tearDown(self):
        RecipeTestCase.tearDown(self)
        logging.getLogger('cpl.rtest').removeHandler(self.handler)
        logging.getLogger('othername').removeHandler(self.other_handler)

    class THandler(logging.Handler):
        def __init__(self):
            logging.Handler.__init__(self)
            self.logs = list()

        def emit(self, record):
            self.logs.append(record)

        def clear(self):
            self.logs = list()

    def test_logging_DEBUG(self):
        '''Injection of CPL messages into the python logging system'''
        self.handler.clear()
        logging.getLogger().setLevel(logging.DEBUG)
        res = self.recipe(self.raw_frame)
        try:
            res.THE_PRO_CATG_VALUE.close()
        except:
            pass

        # check that the logs are not empty
        self.assertNotEqual(len(self.handler.logs), 0)
        funcnames = set()
        lognames = set()
        for r in self.handler.logs:
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
        self.assertTrue('cpl.rtest.cpl_dfs_product_save' in lognames)
        
    def test_logging_INFO(self):
        '''Filtering INFO messages'''
        self.handler.clear()
        logging.getLogger('cpl.rtest').setLevel(logging.INFO)
        res = self.recipe(self.raw_frame)
        try:
            res.THE_PRO_CATG_VALUE.close()
        except:
            pass

        # check that the logs are not empty
        self.assertNotEqual(len(self.handler.logs), 0)

    def test_logging_WARN(self):
        '''Filtering WARN messages'''
        self.handler.clear()
        logging.getLogger('cpl.rtest').setLevel(logging.WARN)
        res = self.recipe(self.raw_frame)
        try:
            res.THE_PRO_CATG_VALUE.close()
        except:
            pass

        # check that the logs are not empty
        self.assertNotEqual(len(self.handler.logs), 0)

    def test_logging_ERROR(self):
        '''Filtering of error messages'''
        # There is no error msg written by the recipe, so it should be empty.
        self.handler.clear()
        logging.getLogger('cpl.rtest').setLevel(logging.ERROR)
        res = self.recipe(self.raw_frame)
        try:
            res.THE_PRO_CATG_VALUE.close()
        except:
            pass
        self.assertEqual(len(self.handler.logs), 0)

    def test_logging_common(self):
        '''Log name specification on recipe call'''
        self.handler.clear()
        self.other_handler.clear()
        res = self.recipe(self.raw_frame, logname = 'othername')
        try:
            res.THE_PRO_CATG_VALUE.close()
        except:
            pass
        self.assertNotEqual(len(self.other_handler.logs), 0)

    def test_logging_multiline(self):
        '''Multiple lines in messages'''
        self.handler.clear()
        logging.getLogger('cpl.rtest').setLevel(logging.INFO)
        res = self.recipe(self.raw_frame)
        try:
            res.THE_PRO_CATG_VALUE.close()
        except:
            pass
        # check that the multi line log sequence appears
        multiline = 0
        tag = 'multiline#'
        for l in self.handler.logs:
            if tag not in l.msg:
                continue
            i = int(l.msg[l.msg.index(tag)+len(tag):].split()[0])
            self.assertEqual(multiline + 1, i)
            multiline = i
        self.assertEqual(multiline, 3)

    def test_result(self):
        '''"log" attribute of the result object'''
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
        try:
            res.THE_PRO_CATG_VALUE.close()
        except:
            pass

    def test_error(self):
        '''"log" attribute of the CplError object'''
        try:
            self.recipe('test.fits')
        except cpl.CplError as r:
            res = r
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

class ProcessingInfo(RecipeTestCase):
    def setUp(self):
        RecipeTestCase.setUp(self)
        '''Parameter storage in the result'''
        self.recipe.param.stropt = 'more'
        self.recipe.param.boolopt = False
        self.recipe.param.intopt = 123
        self.recipe.param.floatopt = -0.25
        self.recipe.param.enumopt = 'third'
        self.recipe.param.rangeopt = 0.125
        self.recipe.calib.FLAT = fits.HDUList([
                fits.PrimaryHDU(numpy.random.random_integers(0, 65000,
                                                          self.image_size))])
        self.res = self.recipe(self.raw_frame).THE_PRO_CATG_VALUE
        self.pinfo = cpl.dfs.ProcessingInfo(self.res)

    def tearDown(self):
        try:
            self.res.close()
        except:
            pass

    def test_list(self):
        '''All processing infos as a list'''
        pi = cpl.dfs.ProcessingInfo.list(self.res[0])
        self.assertTrue(len(pi), 1)
        self.assertTrue(pi[0], self.pinfo)

    def test_param(self):
        '''Parameter information'''
        self.assertEqual(len(self.pinfo.param), len(self.recipe.param))
        for p in self.recipe.param:
            self.assertEqual(self.pinfo.param[p.name], 
                             p.value if p.value is not None else p.default)

    def test_calib(self):
        '''Calibration frame information'''
        self.assertEqual(len(self.pinfo.calib), 1)
        self.assertEqual(self.pinfo.calib['FLAT'][-5:], '.fits')

    def test_tag(self):
        '''Input tag information'''
        self.assertEqual(self.pinfo.tag, self.recipe.tag)

    def test_raw(self):
        '''Raw file information'''
        self.assertEqual(self.pinfo.raw[-5:], '.fits')

    def test_name(self):
        '''Recipe and pipeline name information'''
        self.assertEqual(self.pinfo.name, self.recipe.__name__)
        self.assertEqual(self.pinfo.pipeline, 'iiinstrument')

    def test_version(self):
        '''Version information'''
        self.assertEqual(self.pinfo.version[0], self.recipe.version[0])
        self.assertEqual(self.pinfo.cpl_version, 'cpl-%s' % self.recipe.cpl_version)

    def test_md5(self):
        '''MD5 checksums'''
        md5sum = self.res[0].header.get('DATAMD5')
        self.assertEqual(md5sum, self.pinfo.md5sum)
        md5sum = self.res[0].header.get('HIERARCH ESO PRO REC1 CAL1 DATAMD5')
        self.assertEqual(md5sum, self.pinfo.md5sums[self.pinfo.calib['FLAT']])

create_recipe(recipe_name)
if __name__ == '__main__':
    unittest.main()
