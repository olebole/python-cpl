class RestrictedDict(object):
    '''Create a disctionary where the entries are restricted.
    
    This class is abstract. An implementation should implement 
    __iter__(self) to get the list of possible entries, and 
    _key(self, entry) to get the key (string) for an entry.

    In the implementation, only private variables are allowed (starting with
    an underscore). All other variables are treated as dictionary entries.

    The dictionary entries may be accessed either as attributes, or as keys.
    All entries should be subclasses from RestrictedDictEntry.

    '''
    def __init__(self, other = None):
        if isinstance(other, self.__class__):
            self._values = dict([ (self._key(o), o.value) 
                                  for o in other if o.value])
        elif isinstance(other, dict):
            self._values = dict([ (self._key(o[0]), o[1]) 
                                  for o in other.items() ])
        elif other:
            self._values = dict([ (self._key(o[0]), o[1]) for o in other ])
        else:
            self._values = dict()

    def __getitem__(self, key):
        for p in self:
            if key == self._key(p):
                return p
        raise AttributeError('Object has no attribute %s' % (key))

    def __setitem__(self, key, value):
        for p in self:
            if key == self._key(p):
                p.value = value
                return
        raise AttributeError('Object has no attribute %s' % (key))

    def __delitem__(self, key):
        for p in self:
            if key == self._key(p):
                del p.value
                return
        raise AttributeError('Object has no attribute %s' % (key))

    def __contains__(self, key):
        for p in self:
            if key == self._key(p):
                return True
        return False

    def __len__(self):
        l = 0
        for p in self:
            l += 1
        return l
        
    def _set_value(self, p, value):
        self._values[self._key(p)] = value

    def _get_value(self, p):
        return self._values.get(self._key(p))

    def _del_value(self, p):
        del self._values[self._key(p)]

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super(RestrictedDict, self).__setattr__(key, value)
        else:
            self[key] = value

    def __delattr__(self, key):
        del self[key]

    def __dir__(self):
        return [ self._key(p) for p in self ]

    def __repr__(self):
        return list(self).__repr__()

class UnrestrictedDict(RestrictedDict):
    def __init__(self, other = None):
        RestrictedDict.__init__(self, other)
        self._entries = set()

    def __setitem__(self, key, value):
        for p in self:
            if key == self._key(p):
                p.value = value
                return
        p = self._createentry(key)
        self._entries.add(p)
        p.value = value

    def __iter__(self):
        return self._entries.__iter__()

class RestrictedDictEntry(object):
    '''Abstract class for an entry in the resctricted dictionary.

    All entries of a restricted dictionary should be subclassed from this
    class. 
    '''
    def __init__(self, parent = None):
        self.parent = parent

    def set_value(self, value):
        '''Default setter for the "value" attribute.
        
        This function can be overwritten if there are special needs for that.
        '''
        if self.parent is not None:
            self.parent._set_value(self, value)
            
    def _set_value(self, value):
        self.set_value(value)

    def _get_value(self):
        if self.parent is not None:
            return self.parent._get_value(self)
        else:
            return None

    def _del_value(self):
        try:
            self.parent._del_value(self)
        except KeyError:
            pass

    value = property(_get_value, _set_value, _del_value)

