import os

import pyfits

class Result(object):
    def __init__(self, recipedefs, dir, res, delete = True, 
                 input_len = 0, logger = None):
        '''Build an object containing all result frames.

        Calling :meth:`cpl.Recipe.__call__` returns an object that contains
        all result ('production') frames in attributes. All results for one
        tag are summarized in one attribute of the same name. 

        The attribute content is either a :class:`pyfits.HDUList` or a
        class:`list` of HDU lists, depending on the recipe and the call: If
        the recipe produces one out put frame of a tag per input file, the
        attribute contains a list if the recipe was called with a list, and if
        the recipe was called with a single input frame, the result attribute
        will also contain a single input frame. If the recipe combines all
        input frames to one output frame, a single :class:`pyfits.HDUList` es
        returned, independent of the input parameters. 

        .. todo:: This behaviour is made on some heuristics based on the
           number and type of the input frames. The heuristics will go wrong
           if there is only one input frame, specified as a list, but the
           recipe tries to summarize the input. In this case, the attribute
           will contain a list where a single :class:`pyfits.HDUList` was
           expected. To solve this problem, the "MASTER" flag has to be
           forwarded from the (MUSE) recipe which means that it should be
           exported by the recipe -- this is a major change since it probably
           leads into a replacement of CPLs recipeconfig module by something
           more sophisticated. And this is not usable for non-MUSE recipes
           anyway. So, we will skip this to probably some distant future.
        '''
        self.dir = dir
        if res[2][0]:
            raise CplError(res[2][0], res[1], logger)
        self.tags = set()
        for tag, frame in res[0]:
            hdu = pyfits.open(os.path.abspath(os.path.join(dir, frame)),
                              memmap = delete, 
                              mode = 'update' if delete else 'copyonwrite')
            if delete:
                hdu.readall()
                os.remove(os.path.join(dir, frame))
            tag = tag
            if tag not in self.__dict__:
                self.__dict__[tag] = hdu if input_len != 1 else [ hdu ]
                self.tags.add(tag)
            elif isinstance(self.__dict__[tag], pyfits.HDUList):
                self.__dict__[tag] = [ self.__dict__[tag], hdu ]
            else:
                self.__dict__[tag].append(hdu)
        self.stat = Stat(res[2])
        self.error = CplError(res[2][0], res[1], logger) if res[1] else None
        self.log = logger.entries if logger else None

class Stat(object):
    def __init__(self, stat):
        self.return_code = stat[0]
        self.user_time = stat[1]
        self.sys_time = stat[2]
        self.memory_is_empty = { -1:None, 0:False, 1:True }[stat[3]]

class CplError(StandardError):
    '''Error message from the recipe.

    If the CPL recipe invocation returns an error, it is converted into a
    :class:`cpl.CplError` exception and no frames are returned. Also, the
    error is notified in the log file.

    The exception is raised on recipe invocation, or when accessing the result
    frames if the recipe was started in background
    (:attr:`cpl.Recipe.threaded` set to :attr:`True`).

    Attributes:

    .. attribute:: code

       The CPL error code returned from the recipe.

    .. attribute:: msg

       The supplied error message. 
    
    .. attribute:: filename

       The source file name where the error occurred.

    .. attribute:: line

       The line number where the error occurred.

    .. attribute:: log

       Log lines of the recipe that lead to this exception.

       .. seealso:: :class:`cpl.log.LogList`

    .. attribute:: next
     
       Next error, or :attr:`None`.

    '''
    def __init__(self, retval, res, logger = None):
        self.retval = retval
        self.log = logger.entries if logger else None
        self.next = None
        if not res:
            self.code, self.msg, self.file, self.line, self.function = (
                None, None, None, None, None)
        else:
            self.code, self.msg, self.file, self.line, self.function = res[0]
            o = self
            for r in res[1:]:
                o.next = CplError(retval, [ r ], logger)
                o = o.next
    
    def __iter__(self):
        class Iter:
            current = self
            def next(self):
                if Iter.current is None:
                    raise StopIteration
                s = Iter.current
                Iter.current = Iter.current.next
                return s
        return Iter()

    def __str__(self):
        if self.code is None:
            s = 'Unspecified'
        else:
            s = "%s (%i) in %s() (%s:%s)" % (self.msg, self.code, 
                                             self.function, self.file, 
                                             self.line) 
        if self.next:
            for e in self.next:
                s += "\n    %s (%i) in %s() (%s:%s)" % (e.msg, e.code, 
                                                        e.function, e.file, 
                                                        e.line) 
        return s
