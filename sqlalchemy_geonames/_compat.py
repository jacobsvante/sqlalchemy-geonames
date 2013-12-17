"""py2/py3 compatibility, borrowed from pocoo's jinja2 _compat module

Some info: http://lucumr.pocoo.org/2013/5/21/porting-to-python-3-redux/
"""
import sys

PY2 = sys.version_info[0] == 2
_identity = lambda x: x

if not PY2:
    text_type = str
    string_types = (str, )
    implements_to_string = _identity
else:
    import cdecimal as decimal
    text_type = unicode
    string_types = (str, unicode)

    def implements_to_string(cls):
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda x: x.__unicode__().encode('utf-8')
        return cls

# Needed for sqlalchemy's active db library to use cdecimal
# cdecimal is the standard implementation for 3.3 and higher
if sys.version_info[0:2] < (3, 3):
    import cdecimal as decimal
    sys.modules["decimal"] = decimal
else:
    import decimal

Decimal = decimal.Decimal
