import errno
import os
from functools import reduce
from getpass import getpass
from . import _compat


missing = object()


class cached_property(object):
    """ Decorator that turns a class method into a cached property
    From https://speakerdeck.com/u/mitsuhiko/p/didntknow, slide #69
    """

    def __init__(self, func):
        self.func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self.__module__ = func.__module__

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, missing)
        if value is missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value


def try_int(value):
    try:
        return int(value)
    except ValueError:
        return None


def normalize_path(path):
    return os.path.abspath(os.path.expanduser(path))


def get_attr(obj, attr, default=missing):
    """Recursive getattr
    Works just like the built-in getattr except if a dot is found in `attr`
    it will assume that a sub-attribute of it should be returned.
    It also supports specifying indexes in the `attr` string.
    """
    def getattr_or_index(obj, attr):
        index = None
        if attr.endswith(']'):
            attr, index = attr[:-1].split('[')
            return getattr(obj, attr)[int(index)]
        else:
            return getattr(obj, attr)

    if isinstance(attr, _compat.string_types):
        return get_attr(obj, attr.split('.'), default)
    try:
        return reduce(getattr_or_index, attr, obj)
    except (AttributeError, IndexError):
        if default is missing:
            raise
        return default


def simple_repr(*model_attrs, **kwargs):
    """Returns a repr for SQLAlchemy declarative objects, from its attributes
    The returned object representation will have the following format:

        <ModelName: model_attrs_val[0] - [- model_attrs_val[1]]...>

    Example usage::

        In [1]: class User(Base):
           ...:     __repr__ = simple_repr('email')
           ...:     email = Column(String, nullable=False)
        In [2]: user = User(email='m@jacobian.se')
        In [3]: print(user)
        Out[3]: <User: m@jacobian.se>

    The default separator of ' - ' can be overriden by passing in `sep`.
    A max length of each attribute value can be set with kwarg `max_length`,
    defaults to 40.

    Sub-attributes can be specified by using a dotted syntax. Example::

        In [1]: class Parent(Base):
           ...:     name = Column(String)

           ...: class Child(Base):
           ...:     __repr__ = simple_repr('name', 'parent.name', sep=', ')
           ...:     name = Column(String)
           ...:     parent_id = Column(Integer, ForeignKey(Parent))
           ...:     parent = relationship(Parent)

        In [2]: parent = Parent(name='mom')
        In [3]: child = Child(name='daughter', parent=parent)
        In [4]: repr(child)
        Out[4]: <Child: daughter, mom>

    If the keyword argument `strict` is set to False the specified model
    attribute string will be used as a fallback if the attribute couldn't
    be found. Specific fallbacks can be specified for each model attr.
    Here's an example building on the previous one:

        In [5]: class Child(Base):
           ...:     __repr__ = simple_repr('name', 'parent.name', sep=', ',
           ...:                            strict=False)
        In [6]: child = Child(name='daughter') # Notice: No parent specified
        In [7]: repr(child)
        Out[7]: <Child daughter, [parent.name]>

        In [8]: class Child(Base):
           ...:     __repr__ = simple_repr('name', 'parent.name', sep=', ',
           ...:                        fallbacks={'parents.name': 'no parent'})
        In [9]: repr(Child(name='daughter'))
        Out[9]: <Child daughter, no parent>

    """
    sep = kwargs.pop('sep', u' - ')
    max_length = kwargs.pop('max_length', 40)
    fallbacks = kwargs.pop('fallbacks', {})
    strict = kwargs.pop('strict', True)

    def decorator(self):
        clsname = self.__class__.__name__
        attr_vals = []
        for attr in model_attrs:
            try:
                default_on_attr_error = fallbacks[attr]
            except KeyError:
                default_on_attr_error = u'{}(missing)'.format(attr)
            try:
                val = get_attr(self, attr)
            except (AttributeError, IndexError):
                if strict is True and attr not in fallbacks:
                    raise
                else:
                    attr_vals.append(default_on_attr_error)
                    continue
            if isinstance(val, _compat.string_types) and len(val) > max_length:
                attr_vals.append(val[0:max_length - 3] + u'...')
            else:
                attr_vals.append(val)
        joined = sep.join(_compat.text_type(v) for v in attr_vals)
        text_repr = u'<{}: {}>'.format(clsname, joined)
        return text_repr.encode('utf-8') if _compat.PY2 else text_repr
    return decorator


def get_password(prompt_text,
                 empty_password_text='Please enter a non-empty password.'):
    password = ''
    while not password:
        password = getpass(prompt_text)
        if password:
            return password
        print(empty_password_text)


def mkdir_p(path):
    """Like `mkdir -p` on *nix systems"""
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
