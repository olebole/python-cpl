from restricteddict import RestrictedDict, RestrictedDictEntry

class Parameter(RestrictedDictEntry):
    '''Attributes:
    
    name: Parameter name
    context: Parameter context
    range: Value range if restricted, or None if not
    sequence: Allowed values of None if all are allowed
    default: Default value
    value: currently set value or None if none was set
    '''
    def __init__(self, name, context = None, default = None, desc = None, 
                 range_ = None, sequence = None, parent = None):
        RestrictedDictEntry.__init__(self, parent)
        self.name = name
        self.context = context
        self.range = range_
        self.sequence = sequence
        self.default = default
        self.__doc__ = "%s (%s)" % (desc, default.__class__.__name__)

    def set_value(self, value):
        if value is not None:
            value = self.default.__class__(value) 
            if self.sequence and value not in self.sequence:
                raise ValueError("'%s' is not in %s" % (value, self.sequence))
            if self.range and not (self.range[0] <= value <= self.range[-1]):
                raise ValueError("'%s' is not in range %s" % (value, self.range))
            super(Parameter, self).set_value(value)
        else:
            super(Parameter, self).del_value()

    fullname = property(lambda self: self.context + '.' + self.name)

    def __str__(self):
        return "%s%s" % (
            str(self.value if self.value is not None else self.default), 
            ' (default)' if self.value is None else '')

    def __repr__(self):
        return "Parameter('%s', %s=%s)" % (
            self.name, 
            "value" if self.value is not None else "default",
            self.value if self.value is not None else self.default)

class ParameterList(RestrictedDict):
    def __init__(self, recipe, other = None):
        RestrictedDict.__init__(self, other)
        self._recipe = recipe

    def _key(self, p):
        return p.rsplit('.', 1)[-1] if isinstance(p, str) else p.name

    def __iter__(self):
        return [ Parameter(pd[0], pd[1], pd[5], pd[2], pd[3], pd[4], self)
                 for pd in self._recipe._recipe.params() ].__iter__()

    def __str__(self):
        r = ''
        for s in self:
            if s.value is not None:
                r += ' --%s=%s' % (s.name, str(s.value))
        return r
    
    def _doc(self):
        r = 'Parameter list for recipe %s.\n\nAttributes:\n' % (
            self._recipe.name)
        for s in self:
            r += ' %s: %s (default: %s)\n' % (
                s.name, s.__doc__, str(s.default))
        return r        
    __doc__ = property(_doc)


    def _aslist(self, **ndata):
        parlist = [ ( param.fullname, param.value ) 
                    for param in self
                    if param.value is not None 
                    and (ndata is None or param.name not in ndata) ]
        if ndata:
            parlist += [ (self[name].fullname, tdata)
                         for name, tdata in ndata.items() 
                         if name in self ]
        return parlist
