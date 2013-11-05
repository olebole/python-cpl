import textwrap

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

       The value of the parameter, or :obj:`None` if set to default

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

      The numeric range of a parameter, or :obj:`None` if the parameter range
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
                        ptype = None, enabled = None):
        self.context = context
        self.range = range_
        self.sequence = sequence
        self.default = default
        self.fullname = fullname
        self.type = ptype or default.__class__
        self.enabled = enabled
        self.__doc__ = textwrap.fill("%s (%s; default: %s)" %
                                     (desc, self.type.__name__,
                                      repr(self.default)))

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
            repr(self.value if self.value is not None else self.default),
            ' (default)' if self.value is None else '')

    def __repr__(self):
        return 'Parameter(%s, %s=%s)' % (
            repr(self.name),
            "value" if self.value is not None else "default",
            repr(self.value if self.value is not None else self.default))

    def __getitem__(self,i):
        return (self.name, self.value or self.default)[i]


class ParameterList(object):
    def __init__(self, recipe, other = None, prefix = None):
        self._recipe = recipe
        self._dict = dict()
        self._pars = list()
        self._prefix = prefix
        childs = set()
        for name, context, fullname, desc, prange, \
                sequence, deflt, ptype, enabled in recipe._recipe.params():
            if prefix:
                if name.startswith(prefix + '.'):
                    aname = name[len(prefix)+1:]
                else:
                    continue
            else:
                aname = name
            if '.' in aname:
                aname = aname.split('.', 1)[0]
                if prefix:
                    aname = prefix + '.' + aname
                childs.add(aname)
            else:
                par = Parameter(name)
                par._set_attributes(context, fullname, deflt,
                                    desc, prange, sequence, ptype, enabled)
                self._dict[name] = par
                self._dict[fullname] = par
                self._dict[self._paramname(aname)] = par
                self._pars.append(par)
        for name in childs:
            clist = ParameterList(recipe, prefix = name)
            self._dict[name] = clist
            for par in clist._pars:
                self._dict[par.name] = par
                self._dict[par.fullname] = par
                self._pars.append(par)
            aname = self._paramname(name)
            self._dict[aname] = clist
        if other:
            self._set_items(other)
        self.__doc__ = self._doc()

    def _set_items(self, other):
        if isinstance(other, self.__class__):
            l = ((o.name, o.value) for o in other)
        elif isinstance(other, dict):
            l = other.items()
        else:
            l = other
        for o in l:
            self[o[0]] = o[1]

    def _del_items(self):
        for p in self:
            del p.value

    @staticmethod
    def _paramname(s):
        for c in [ '-', ' ' ]:
            if isinstance(c, tuple):
                s = s.replace(c[0], c[1])
            else:
                s = s.replace(c, '_')
        return s

    def __iter__(self):
        return self._pars.__iter__()

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        p = self[key]
        if isinstance(p, self.__class__):
            if value is not None:
                p._set_items(value)
            else:
                p._del_items()
        else:
            p.value = value

    def __delitem__(self, key):
        p = self[key]
        if isinstance(p, self.__class__):
            p._del_items()
        else:
            del p.value

    def __str__(self):
        return dict(self).__str__()
    
    def __contains__(self, key):
        return key in self._dict

    def __len__(self):
        return len(self._pars)
        
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
        return list(set(self._paramname(d) 
                        for d in self._dict.keys() if '.' not in d))

    def __repr__(self):
        return repr(dict(self))

    def __eq__(self, other):
        return dict(self) == other

    def _doc(self):
        if len(self) == 0:
            return 'No parameters'
        r = ''
        maxlen = max(len(p.name) for p in self)
        for p in self:
            r += textwrap.fill(
                p.__doc__,
                subsequent_indent = ' ' * (maxlen + 3),
                initial_indent = ' %s: ' % p.name.rjust(maxlen)) + '\n'
        return r        

    def _aslist(self, par):
        parlist = ParameterList(self._recipe, self)
        if par is not None:
            parlist._set_items(par.items())
        l = list()
        for param in parlist:
            if isinstance(param, Parameter):
                if param.value is not None:
                    l.append((param.fullname, param.value))
            else:
                l += param._aslist(par)
        return l
