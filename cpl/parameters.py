
class Parameter(object):
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

    .. attribute: Parameter.fullname
      The parameter name including the context (readonly).
      The fullname usually consists of the parameter context and the parameter
      name, separated by a dot.

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
    def __init__(self, name):
        self.name = name
        self._value = None

    def _set_attributes(self, context = None, fullname = None, default = None, 
                        desc = None, range_ = None, sequence = None, 
                        type = None):
        self.context = context
        self.range = range_
        self.sequence = sequence
        self.default = default
        self.fullname = fullname
        self.type = type or default.__class__
        self.__doc__ = "%s (%s)" % (desc, default.__class__.__name__)

    def _set_value(self, value):
        if value is not None and self.type is not None.__class__:
            if self.type is bool and isinstance(value, str):
                d = {'true':True, 'false':False, 'yes':True, 'no':False}
                value = d.get(value.lower(), value)
            value = self.type(value) 
            if self.sequence and value not in self.sequence:
                raise ValueError("'%s' is not in %s" % (value, self.sequence))
            if self.range and not (self.range[0] <= value <= self.range[-1]):
                raise ValueError("'%s' is not in range %s" % (value, self.range))
        self._value = value

    def _get_value(self):
        return self._value

    def _del_value(self):
        self._value = None

    value = property(_get_value, _set_value, _del_value)

    def __str__(self):
        return "%s%s" % (
            str(self.value if self.value is not None else self.default), 
            ' (default)' if self.value is None else '')

    def __repr__(self):
        return "Parameter('%s', %s=%s)" % (
            self.name, 
            "value" if self.value is not None else "default",
            self.value if self.value is not None else self.default)


class ParameterList(object):
    def __init__(self, recipe, other = None):
        self._recipe = recipe
        self._values = dict()
        if isinstance(other, self.__class__):
            self._set_items((o.name, o.value) for o in other)
        elif isinstance(other, dict):
            self._set_items(other.iteritems())
        elif other:
            self._set_items(other)

    def _set_items(self, l):
        for o in l:
            if o[1] is not None:
                try:
                    self[o[0]] = o[1]
                except:
                    pass

    def _cpl_dict(self):
        cpl_params = self._recipe._recipe.params()
        if cpl_params is None:
            return None
        s = dict()
        for pd in cpl_params:
            (name, context, fullname, desc, _range, sequence, deflt, type) = pd
            if name in s:
                continue
            else:
                s[name] = self._values.setdefault(name, Parameter(name))
                s[name]._set_attributes(context, fullname, deflt, 
                                        desc, _range, sequence, type)
        return s

    def _get_dict(self):
        return self._cpl_dict() or self._values

    _dict = property(_get_dict)

    def _get_dict_full(self):
        return dict(self._get_dict().items() 
                    + [ (p.fullname, p) for p in self._get_dict().values()
                        if p.fullname ])

    def __iter__(self):
        return self._get_dict().itervalues()

    def __getitem__(self, key):
        return self._get_dict_full()[key]

    def __setitem__(self, key, value):
        d = self._cpl_dict()
        if d is not None:
            d = dict(d.items() + 
                     [ (p.fullname, p) for p in d.values() if p.fullname] )
            d[key].value = value
        else:
            self._values.setdefault(key, Parameter(key)).value = value

    def __delitem__(self, key):
        del self._get_dict_full()[key].value

    def __str__(self):
        r = ''
        for s in self:
            if s.value is not None:
                r += ' --%s=%s' % (s.name, str(s.value))
        return r
    
    def __contains__(self, key):
        return key in self._get_dict_full()

    def __len__(self):
        return len(self._get_dict())
        
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super(ParameterList, self).__setattr__(key, value)
        else:
            self[key] = value

    def __delattr__(self, key):
        del self[key]

    def __dir__(self):
        return self._get_dict().keys()

    def __repr__(self):
        return list(self).__repr__()

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

