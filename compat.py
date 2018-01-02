# coding: utf8

"""
wechat_jump_game.compat
~~~~~~~~~~~~~~~
This module handles import compatibility issues between Python 2 and
Python 3.
"""

import sys

# -------
# Pythons
# -------

# Syntax sugar.
_ver = sys.version_info

#: Python 2.x?
is_py2 = (_ver[0] == 2)

#: Python 3.x?
is_py3 = (_ver[0] == 3)

# ---------
# Specifics
# ---------

if is_py2:

    builtin_str = str
    bytes = str
    str = unicode
    basestring = basestring

    xrange = xrange

elif is_py3:

    builtin_str = str
    str = str
    bytes = bytes
    basestring = (str, bytes)

    xrange = range

