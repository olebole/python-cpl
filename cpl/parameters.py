from restricteddict import RestrictedDict, RestrictedDictEntry

class Parameter(RestrictedDictEntry):
    '''Runtime configuration parameter of a recipe. 
    Parameters are designed to handle monitor/control data and they provide a
    standard way to pass information to the recipe.

    The CPL implementation supports three classes of parameters: a plain
    value, a value within a given range, or a value as part of an
    enumeration. When a parameter is created it is created for a particular
    value type. In the latter two cases, validation is performed whenever the
    value is set.

    Attributes:

    .. attribute:: Parameter.value

       The value of the parameter, or :attr:`None` if set to default

    .. attribute:: Parameter.default

       The default value of the parameter (readonly).

    .. attribute:: Parameter.name

      The parameter name (readonly). Parameter names are unique. They
      define the identity of a given parameter.

    .. attribute:: Parameter.context

      The parameter context (readonly). The context usually consists of the
      instrument name and the recipe name, separated by a dot. The context is
      used to associate parameters together.

    .. attribute:: Parameter.range 

      The numeric range of a parameter, or :attr:`None` if the parameter has
      no limited range (readonly).

    .. attribute:: Parameter.sequence

      A :class:`list` of possible values for the parameter if the parameter
      are limited to an enumeration of possible values (readonly).

    The following example prints the attributes of one parameter:

    >>> print 'name:    ', muse_scibasic.param.cr.name
    name:     cr
    >>> print 'fullname:', muse_scibasic.param.cr.fullname
    fullname: muse.muse_scibasic.cr
    >>> print 'context: ', muse_scibasic.param.cr.context
    context:  muse.muse_scibasic
    >>> print 'sequence:', muse_scibasic.param.cr.sequence
    sequence: ['dcr', 'none']
    >>> print 'range:   ', muse_scibasic.param.cr.range
    range:    None
    >>> print 'default: ', muse_scibasic.param.cr.default
    default:  dcr
    >>> print 'value:   ', muse_scibasic.param.cr.value
    value:    None
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

    fullname = property(lambda self: self.context + '.' + self.name, 
                        doc='The parameter name including the context (readonly). '
                        'The fullname consists of the parameter context and the parameter '
                        'name, separated by a dot.')

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
        parlist = dict([ ( param.fullname, param.value ) 
                         for param in self
                         if param.value is not None 
                         and (ndata is None or param.name not in ndata) ])
        if ndata:
            for name, tdata in ndata.items():
                if name.startswith('param_'):
                    pname = name.split('_', 1)[1]
                    if pname in self:
                        parlist[self[pname].fullname] = tdata
        return list(parlist.iteritems())
