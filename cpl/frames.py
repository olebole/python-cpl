from __future__ import absolute_import
import os
import tempfile
try:
    from astropy.io import fits
except:
    import pyfits as fits

from . import md5sum

class FrameConfig(object):
    '''Frame configuration. 

    Each :class:`FrameConfig` object stores information about one the data
    type a recipe can process. They are used for defining the calibration
    files. However, since this information is not generally provided by CPL
    recipes, it contains only dummy information, except for the MUSE recipes.

    The objects stores a frame tag, a unique identifier for a certain kind of
    frame, the minimum and maximum number of frames needed.

    Attributes:

    .. attribute:: tag 

       Category tag name. The tag name is used to distinguish between
       different types of files. An examples of tag names is 'MASTER_BIAS'
       which specifies the master bias calibration file(s).

    .. attribute:: min

       Minimal number of frames, or :obj:`None` if not specified. A frame is
       required if the :attr:`min` is set to a value greater than 0.

    .. attribute:: max 

       Maximal number of frames, or :obj:`None` if not specified

    .. attribute:: frames

       List of frames (file names or :class:`astropy.io.fits.HDUList` objects)
       that are assigned to this frame type.
    '''
    def __init__(self, tag, min_frames = 0, max_frames = 0, frames = None):
        self.tag = tag
        self.min = min_frames if min_frames > 0 else None
        self.max = max_frames if max_frames > 0 else None
        self.frames = frames
        self.__doc__ = self._doc()

    def extend_range(self, min_frames, max_frames):
        if self.min is not None:
            self.min = min(self.min, min_frames) if min_frames is not None \
                else None
        if self.max is not None:
            self.max = max(self.max, max_frames) if max_frames is not None \
                else None

    def set_range(self, min_frames, max_frames):
        self.min = min_frames
        self.max = max_frames

    def __str__(self):
        return str(self.frames)

    def __repr__(self):
        return 'FrameDef(%s, frames=%s)' % (repr(self.tag), repr(self.frames))

    def _doc(self):
        if self.max is None or self.min is None:
            r = ' one frame or list of frames'
        elif self.max == 1:
            r = ' one frame'
        elif self.min > 1 and self.max > self.min:
            r = ' list of %i-%i frames' % (self.min, self.max)
        elif self.max > 1:
            r = ' one frame or list of max. %i frames' % self.max
        elif self.min > 1:
            r = ' list of min. %i frames' % self.max
        else:
            r = ' one frame or list of frames'
        if not self.min:
            r += ' (optional)'
        return r

    def __getitem__(self, i):
        return (self.tag, self.frames)[i]
    

class FrameList(object):
    def __init__(self, recipe, other = None):
        self._recipe = recipe
        self._values = dict()
        if isinstance(other, self.__class__):
            self._set_items((o.tag, o.frames) for o in other)
        elif isinstance(other, dict):
            self._set_items(other.items())
        elif other:
            self._set_items(other)

    def _set_items(self, l):
        for o in l:
            self[o[0]] = o[1]

    @property
    def _cpl_dict(self):
        cpl_frameconfigs = self._recipe._recipe.frameConfig()
        if cpl_frameconfigs is None:
            return None
        s = dict()
        for configs in cpl_frameconfigs:
            c_cfg = configs[1]
            for f in c_cfg:
                if f[0] in s:
                    s[f[0]].extend_range(f[1], f[2])
                elif f[0] in self._values:
                    s[f[0]] = self._values[f[0]]
                    s[f[0]].set_range(f[1], f[2])
                else:
                    s[f[0]] = FrameConfig(f[0], f[1], f[2])
                    self._values[f[0]] = s[f[0]]
        return s

    @property
    def _dict(self):
        return self._cpl_dict or self._values

    def __iter__(self):
        return iter(self._dict.values())

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        d = self._cpl_dict
        if d is not None:
            d[key].frames = value
        else:
            self._values.setdefault(key, FrameConfig(key)).frames = value

    def __delitem__(self, key):
        self._dict[key].frames = None

    def __contains__(self, key):
        return key in self._dict

    def __len__(self):
        return len(self._dict)
        
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super(FrameList, self).__setattr__(key, value)
        else:
            self[key] = value

    def __delattr__(self, key):
        del self[key]

    def __dir__(self):
        return self._dict.keys()

    def __repr__(self):
        return repr(dict(self))

    def __str__(self):
        return str(dict(self))

    def __eq__(self, other):
        return dict(self) == other

    @property
    def __doc__(self):
        r = 'Frames for recipe %s.\n\nAttributes:\n' % (
            self._recipe.name)
        for s in self:
            r += '%s: %s\n' % (self._key(s), s.__doc__)
        return r        

    def _aslist(self, frames):
        flist = FrameList(self._recipe, self)
        if frames is not None:
            flist._set_items(frames.items())
        return [(f.tag, f.frames) for f in flist]

def mkabspath(frames, tmpdir):
    '''Convert all filenames in the frames list into absolute paths.

    :class:`astropy.io.fits.HDUList`s will be converted to temporary files
    located in the temporary directory tmpdir.

    The replacement is done in-place. The function will return the list of
    temporary files.

    param frames: :class:`list` of (tag, frame) tuples with frame being either
                  a file name or a HDU list.

    param tmpdir: directory where the temporary files are being created.
    '''
    
    tmpfiles = list()
    for i, frame in enumerate(frames):
        if isinstance(frame[1], fits.HDUList):
            md5 = md5sum.update_md5(frame[1])
            filename = os.path.abspath(os.path.join(tmpdir, '%s_%s.fits' 
                                                    % (frame[0], md5[:8])))
            try:
                os.remove(filename)
            except:
                pass
            frames[i] = ( frame[0], filename )
            tmpfiles.append(filename)
            frame[1].writeto(filename)
        else:
            frames[i] = ( frame[0], os.path.abspath(frame[1]) )
    return tmpfiles

def expandframelist(frames):
    '''Convert a dictionary with frames into a frame list where each frame
    gets its own entry in the form (tag, frame)
    '''
    framelist = list()
    for tag, f in frames:
        if isinstance(f, list) and not isinstance(f, fits.HDUList):
            framelist += [ (tag, frame) for frame in f ]
        elif f is not None:
            framelist.append((tag, f))
    return framelist

