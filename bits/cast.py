# standard
import functools
import re
import unittest

class Cast:
    '''
    Factory for creating "casts", that is, functions which:

    1. change a value into another with the same semantic content but (perhaps) a different type
        (https://en.wikipedia.org/wiki/Type_conversion)
    2. return a default value in the case of no parameters

    Notes:

    - The intention of Cast is to provide a general capability similar to python typers such str() and int().
    - It is assumed that casts reapplied to their own results are the identity function: ``cast(cast(x)) == cast(x)``
    '''
    def __init__(self, cast, default=None):
        '''
        initializion stores the casting function and an initial default value for the factory
        '''
        self.caster = cast
        self.defaulter = default

    def cast(self,default=None):
        '''
        creates the casting function.  An default overriding the Class default may be provided.
        '''
        def convert(thing=None):
            if thing is not None:
                return self.caster(thing)
            elif default is not None:
                return self.caster(default)
            elif self.defaulter is not None:
                return self.caster(self.defaulter)
            else:
                return self.caster()
        return convert

# Utility functions for Casts

def make_fraction(x=0):
    '''
    number between zero and one
    '''
    x= float(x)
    assert x >=0. and x <= 1.
    return x

HEXADECIMAL = re.compile('[a-fA-F0-9]{2}') # preserve for speed
def make_hexstring(x):
    '''
    create a hexstring, that is, '00'..'ff'.
    conversion depends on context:

    - str: check it
    - float: map as fraction [0,1]
    - int: map [0,255]
    '''

    def hexed(i):
        return hex(i).zfill(2).split('x')[-1].zfill(2)

    if isinstance(x,str):
        assert len(x) == 2
        assert HEXADECIMAL.match(x)
        return x
    elif isinstance(x, float):
        assert not x < 0. or x > 1.
        return hexed(int(x*255))
    elif isinstance(x, int):
        return hexed(x % 256)
    else:
        assert False

def make_signed_degree(x=0):
    y = x % 360
    return y - 360 if y > 180 else y

# Pre-built casting function ...

hexstring = Cast(make_hexstring,'00').cast()
fraction = Cast(make_fraction).cast()
degree = Cast(lambda x:x%360,0).cast()
signed_degree = Cast(make_signed_degree).cast()

class Test_Cast(unittest.TestCase):

    def setUp(self):
        self.unknown = 'Unknown'

    def test_string(self):
        unk = Cast(str).cast(self.unknown)
        assert unk() == self.unknown
        assert unk(11) == '11'

    def test_hexstring(self):
        assert hexstring(1.) == hexstring(255) == 'ff'
        assert hexstring() == hexstring(0) == hexstring(0.) == '00'
        for thing in [.1,111,'a0']:
            assert hexstring(hexstring(thing)) == hexstring(thing)

    def test_identity(self):
        id = Cast(lambda x:x).cast(self.unknown)
        assert id(11) == 11
        assert id('hello') == 'hello'
        assert id() == self.unknown

    def test_degree(self):
        assert signed_degree(0) == 0
        assert signed_degree(181) == -179
        assert degree(181) == 181
        assert signed_degree() == 0
        assert degree() == 0
        assert degree(181+360*10) == 181

if __name__ == '__main__':
    unittest.main()