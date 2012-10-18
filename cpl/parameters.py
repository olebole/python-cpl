
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

      The numeric range of a parameter, or :attr:`None` if the parameter range
      is unlimited (readonly).

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

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
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

    @value.deleter
    def value(self):
        self._value = None

    def __str__(self):
        return '%s%s' % (
            `self.value if self.value is not None else self.default`, 
            ' (default)' if self.value is None else '')

    def __repr__(self):
        return 'Parameter(%s, %s=%s)' % (
            `self.name`, 
            "value" if self.value is not None else "default",
            `self.value if self.value is not None else self.default`)

    def __getitem__(self,i):
        return (self.name, self.value or self.default)[i]


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
            self[o[0]] = o[1]

    @property
    def _cpl_dict(self):
        if self._recipe is None or self._recipe._recipe is None:
            return None
        cpl_params = self._recipe._recipe.params()
        if cpl_params is None:
            return None
        s = dict()
        for pd in cpl_params:
            (name, context, fullname, desc, _range, sequence, deflt, type) = pd
            pname = name.replace('.', '_')
            if pname in s:
                continue
            else:
                s[pname] = self._values.setdefault(name, Parameter(name))
                s[pname]._set_attributes(context, fullname, deflt, 
                                         desc, _range, sequence, type)
        return s

    @property
    def _dict(self):
        return self._cpl_dict or self._values

    @property
    def _dict_full(self):
        d = self._dict
        return dict(d.items() +
                    [ (p.fullname, p) for p in d.values() if p.fullname ] +
                    [ (p.name, p) for p in d.values() if p.name not in d])

    def __iter__(self):
        return self._dict.itervalues()

    def __getitem__(self, key):
        return self._dict_full[key]

    def __setitem__(self, key, value):
        d = self._cpl_dict
        if d is not None:
            d = dict(d.items() +
                     [ (p.fullname, p) for p in d.values() if p.fullname] +
                     [ (p.name, p) for p in d.values() if p.name not in d])
            d[key].value = value
        else:
            self._values.setdefault(key.replace('.', '_'), 
                                    Parameter(key)).value = value

    def __delitem__(self, key):
        del self._dict_full[key].value

    def __str__(self):
        r = ''
        for s in self:
            if s.value is not None:
                r += ' --%s=%s' % (s.name, str(s.value))
        return r
    
    def __contains__(self, key):
        return key in self._dict_full

    def __len__(self):
        return len(self._dict)
        
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
        return self._dict.keys()

    def __repr__(self):
        return `list(self)`

    def __eq__(self, other):
        return dict(self) == other

    @property
    def __doc__(self):
        r = 'Parameter list for recipe %s.\n\nAttributes:\n' % (
            self._recipe.name if self._recipe is not None else '')
        maxlen = max(len(p.name) for p in self.param)
        for p in self:
            r += ' %s: %s (default: %s)\n' % (
                p.name.rjust(maxlen), p.__doc__, `p.default`)
        return r        

    def _aslist(self, par):
        parlist = ParameterList(self._recipe, self)
        if par is not None:
            parlist._set_items(par.items())
        return [( param.fullname, param.value ) 
                for param in parlist]
