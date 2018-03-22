# standard
from abc import abstractmethod
from collections import MutableMapping
from functools import wraps
import copy
import unittest

class Unindexed(MutableMapping):
    '''
    An *Unindexed Encyclopedia* extends a *MutableMapping* with the following features:

    - **composition**: Encyclopedia contents may be altered by functions or Encyclopedias
    - **set operation**: Encyclopedias may be combined using union, difference and intersection
    - **mutability**: ability to "freeze" and "melt" an object, that is, change its mutability

    '''

    def __init__(self, mapping=None, frozen=False):
        '''
        - mapping: initialize the Encyclopedia with another mapping
        - frozen: when True, do not allow in-place modification
        '''
        self.frozen = frozen
        if mapping is not None:
            self.update(mapping)

    def unfrozen(f):
        '''
        function decorator to check if object is unfrozen
        '''
        @wraps(f)
        def new(self, *args, **kw):
            if self.frozen:
                return None
            else:
                return f(self, *args, **kw)
        return new

    @unfrozen
    def subtract(self, other):
        '''
        perform set difference
        '''
        for key in other:
            del self[key]
        return self

    @staticmethod
    def identity(thing):
        '''
        a single input, single output identity function
        '''
        return thing

    def copy(self):
        '''
        perform a "deep" copy
        '''
        return copy.deepcopy(self)

    def freeze(self):
        '''
        make encyclopedia immutable
        '''
        new = copy.deepcopy(self)
        new.frozen = True
        return new

    def melt(self):
        '''
        make encyclopedia mutable
        '''
        new = copy.deepcopy(self)
        new.frozen = False
        return new

    def __add__(self, other):
        '''
        create union with this encyclopedia and another
        '''
        new = copy.deepcopy(self)
        new.update(other)
        return new

    def __radd__(self, other):
        return self + other

    @unfrozen
    def __iadd__(self, other):
        self.update(other)
        return self

    @unfrozen
    def __isub__(self, other):
        self.subtract(other)
        return self

    def __sub__(self, other):
        '''
        perform set difference of this encyclopedia and other
        '''
        return self.copy().subtract(other)

    def __mul__(self, other):
        '''
        compose encyclopedia with another object
        '''
        return self.compose(other)
    __rmul__ = __mul__ # note that signature is purposefully *not* reversed

    def __and__(self, other):
        '''
        intersect using unsigned logic
        '''
        return self - (self - other)

    def compose(self, other):
        '''
        perform functional or Encyclopedic composition
        '''
        new = self.__class__()
        for key, value in self.items():
            if value in other:
                new[key] = other[value]
        return new

    class Error(Exception):
        '''
        label Encylopedia exceptions
        '''
        pass

class Indexed(Unindexed):
    '''
    An **Indexed** Encyclopedia may be inverted such that its values map to their keys
    '''

    @abstractmethod
    def __invert__(self):
        '''
        invert the Encyclopedia
        '''
        pass

class Unity(Indexed):

    def __init__(self):
        self.freeze()

    @Indexed.unfrozen
    def __delitem__(self, key):
        pass

    @Indexed.unfrozen
    def __setitem__(self, key, value):
        pass

    @Indexed.unfrozen
    def subtract(self,other):
        pass

    def __getitem__(self, key):
        return key

    def compose(self,other):
        return other.copy()

    def __len__(self):
        return None

    def __iter__(self):
        for i in range(0):
            yield None

    def __invert__(self):
        return self.copy()

class Signed(Indexed):
    '''
    A *Signed Encyclopedia* may contain negative elements, that is, elements which
    cancel similarly keyed elements
    '''

    @abstractmethod
    def __abs__(self):
        '''
        remove negative elements for this encyclopedia
        '''
        pass

    @abstractmethod
    def __neg__(self):
        '''
        negate this encyclopedia
        '''
        pass

    def __and__(self, other):
        '''
        intersect using signed logic
        '''
        return self - abs(self - other)

class Zero(Signed):

    def __init__(self):
        self.freeze()

    @Indexed.unfrozen
    def __delitem__(self, key):
        pass

    @Indexed.unfrozen
    def __setitem__(self, key, value):
        pass

    @Indexed.unfrozen
    def subtract(self, other):
        pass

    def __neg__(self):
        return self.copy()

    def __abs__(self):
        return self.copy()

    def __getitem__(self, key):
        return None

    def compose(self, other):
        return self.copy()

    def __len__(self):
        return 0

    def __iter__(self):
        for i in range(0):
            yield None

    def __add__(self, other):
        return other.copy()

    def __radd__(self, other):
        return other.copy()

    def __invert__(self):
        assert False # 1/0

class Test_Encyclopedia(unittest.TestCase):

    def setUp(self):
        self.unity = Unity()
        self.zero = Zero()

    def test_unity(self):
        unity = self.unity
        for thing in {1, 'thing', None}:
            assert unity[thing] == thing
            assert (unity*~unity)[thing] == thing
            assert (~unity)[thing] == thing

    def test_zero(self):
        unity = self.unity
        zero = self.zero
        for thing in {1, 'thing', None}:
            assert zero[thing] is None
            assert (zero*unity)[thing] is None
            assert (zero+unity)[thing] == thing

if __name__ == '__main__':
    unittest.main()