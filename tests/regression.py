# standard
import unittest
# internal
from encyclopedia.templates import *
from encyclopedia.forest import *
from encyclopedia.relate import *

'''
Run regression tests on the base Encyclopedia classes
'''

class Encyclopedia_Tests(unittest.TestCase):

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

class Test_Forest(unittest.TestCase):

    def setUp(self):
        self.f = f = Forest()
        f += 'G01'
        f['G01'] = 'G11'
        f['G01'] = 'G12'
        f['G11'] = 'G21'
        f['G21'] = 'G31'
        f['G21'] = 'G32'
        f['G21'] = 'G33'
        f['G32'] = 'G41'
        f +=  'G02'

    def test_base(self):
        f1 = self.f
        assert len(f1.trees) == 2
        assert f1.height() == 4
        assert len(f1.canopy()) == len(f1) - 4
        assert 'G21' in f1
        f3 = f1['G21']
        assert f3.counter == f1.counter
        assert len(set(f1.root('G21'))) == 1
        assert len(set(f3.root('G21'))) == 1
        assert Forest.node2alias(f3.root('G21')) == 'G21'
        assert Forest.node2alias(f1.root('G21')) == 'G01'
        f3 = f1.cutting('G21', identified=False)
        assert len(set(f3.above('G21'))) == 3
        assert len(set(f3.below('G21'))) == 0
        assert len(set(f1.below('G21'))) == 1
        assert Forest.node2alias(set(f3.leaves())) == {'G41', 'G33', 'G31'}
        assert f3.counter < f1.counter
        assert 'G01' in f1
        assert 'GX1' not in f1
        f2 = f1['G11']
        assert isinstance(f2, Forest)
        assert len(f2.trees) == 1
        assert len(f2) < len(f1)

    def test_arithmetic(self):
        f1 = self.f.copy()
        f2 = f1.copy()
        f2 += f1.copy()
        assert len(f2) == 2*len(f1)
        f3 = f2 - f1
        assert len(f3) == 0
        f3 = f2 + f1
        assert len(f3) == 3*len(f1)
        f4 = f3.unique()
        assert len(f4) == len(f1)
        assert f4 == f1
        f5 = f1 - f2
        assert len(f5) == 0
        f5 = f1 & f2
        assert f5 == f1
        f6 = f1.copy()
        f5 = f6 & f1
        assert f5 == f1
        f6['G21'] = 'GXX'
        assert f1 != f6
        f5 = f6 & f1
        assert Forest.node2alias(f5.values()) == 'G02'
        assert Forest.node2alias(f5.leaves()) == 'G02'
        assert len(f5) == 1

    def test_aliases(self):
        f = self.f
        f['G01'] = 'G0X'
        f['G21'] = 'G0X'
        l1 = len(f)
        f['G0X'] = 'G0Y'
        assert len(f) == l1 + 2
        assert len(f['G0Y']) == 2

    def test_branching(self):
        f1 = self.f
        f2 = f1.copy()
        assert len(f2) == len(f1)
        assert Forest.equals(f1, f2)
        assert f1['G21'] == f2['G21']
        assert f1['G21'] != f1['G01']
        assert f1 == f2
        f2['G02'] =f2['G21']
        assert len(f2) > len(f1)
        assert not Forest.equals(f1, f2)
        assert f1 != f2
        f3 = f1.cutting(offset=100)
        assert f3 == f1

    def test_iteration(self):
        f1 = self.f
        assert len(list(f1)) ==\
            len(f1.sorted()) ==\
            len(f1.sorted(level=False)) ==\
            len(f1)

    def test_composition(self):
        # scaled
        f1 = self.f
        f2 = 4*f1
        assert len(f2) == 4*len(f1)
        # inner string modification
        def add_x(x):
            return x + 'x'
        f2 = add_x * f1 # modify all the elements
        assert f2 != f1
        assert len(f2) == len(f1)
        def rm_x(x):
            return x[:-1]
        f3 = rm_x * f2
        assert f3 == f1 # undo the modifications
        # element removal
        def rm_g4(x):
            return x if 'G4' not in x else None
        f4 = rm_g4 * f1
        assert len(f4) < len(f1)
        assert 'G41' in Forest.node2alias(f1.leaves())
        assert 'G41' not in Forest.node2alias(f4.leaves())
        # Forest composition
        f5 = Forest()
        f5 += 'G21'
        f5['G21'] = 'G34'
        f5['G34'] = 'G44'
        f5['G44'] = 'G51'
        f6 = f1 * f5
        assert len(f6) == len(f1) + len(f5) - 1
        assert f6.height() == f1.height() + 1

    def test_del(self):
        f1 = self.f.copy()
        f2 = f1.copy()
        del f1['G32']
        assert len(f1) < len(self.f)
        del f2['G41']
        assert len(f1) < len(f2) < len(self.f)

    def test_union(self):
        f1 = self.f.copy()
        f2 = f1.copy()
        f2 += 'G03'
        f2['G03'] = 'G13'

class Relation_Tests(unittest.TestCase):

    def setUp(self):
        fruit = self.fruit = Relation(ordered=True)
        fruit['apple'] = 'red'
        fruit['apple'] = 'shiny'
        fruit['apple'] = 'round'
        fruit['melon'] = 'round'
        fruit['melon'] = 'green'
        fruit['watermelon'] = 'red'
        fruit['watermelon'] = 'green'
        fruit['watermelon'] = 'ovoid'
        fruit['pear'] = 'yellow'
        fruit['kiwi'] = 'green'
        fruit['kiwi'] = 'seedy'
        amount = self.amount = Isomorphism(
            {'pack': 5, 'bushel': 10, 'crate': 100})
        colors = self.colors = Isomorphism(
            {'red': (1, 0, 0), 'blue': (0, 1, 0), 'green': (0, 0, 1)})

    def test_basic(self):
        fruit = self.fruit
        assert 'seedy' in ~fruit
        assert 'lolipop' not in fruit
        assert fruit.pop('kiwi') == ['green', 'seedy']
        assert 'seedy' not in fruit.values()
        for f in fruit:
            assert isinstance(f, str)
        assert list(fruit.keys()) == ['apple', 'melon', 'watermelon', 'pear']
        assert len(fruit) == 4
        assert len(~fruit) == 6
        assert len(fruit['apple']) == 3
        assert len(fruit['watermelon']) == 3
        assert 'pear' in (~fruit)['yellow']
        assert 'yellow' in fruit['pear']
        assert fruit['pear'] == ['yellow']
        del fruit['pear']
        assert len(fruit) == 3
        assert len(~fruit) == 5
        del fruit['apple']
        assert len(fruit) == 2
        assert len(~fruit) == 4
        another = fruit.copy()
        assert len(~another) == len(~fruit)
        assert len(another) == len(fruit)
        assert len(fruit.keys()) == len(fruit)
        assert len(fruit.values()) == len(~fruit)
        assert len(fruit.items()) == len(fruit)
        assert fruit.get('armadillo') is None
        fruit.clear()
        assert len(fruit) == 0
        assert fruit.get('melon') is None

    def test_creation(self):
        m = Isomorphism({'a': 1, 'b': 2, 'c': 11})
        mp = ~m
        assert mp[2] == 'b'
        m = Function({'a': 1, 'b': 1, 'c': 11})
        mp = ~m
        assert mp[1] == {'b', 'a'}
        m = Partition({'a': 1, 'b': 2, 'c': 11})
        m['a'] = 3
        mp = ~m
        assert mp[1] == 'a'
        assert mp[2] != 'a'
        assert mp[3] == 'a'

    def test_composite(self):
        fruits = {'apple': 'red', 'cherry': 'red',
                  'strawberry': 'red', 'banana': 'yellow'}
        fruit = Relation(fruits)
        assert len(fruit) == len(fruits)
        more = {'yellow': 'pear', 'pomegranate': 'red', 'watermelon': 'seedy'}
        fruit.update(more)
        assert len(fruit) == len(more) + len(fruits)
        even_more = Isomorphism({'papaya': 'starchy', 'grape': 'tangy'})
        fruit.update(even_more)
        assert len(fruit) == len(even_more) + len(more) + len(fruits)

    def test_restrictions(self):
        fruit = Relation(cardinality='1:1')
        fruit['apple'] = 'red'
        fruit['pear'] = 'yellow'
        fruit['apple'] = 'green'
        assert 'apple' in fruit
        fruit['watermelon'] = 'green'
        assert 'apple' not in fruit
        fruit['papaya'] = 'green'
        assert 'watermelon' not in fruit

        # NOTE: setting restriction directly; not suggested usage as this can
        # make objects inconsistent.

        fruit.cardinality = 'M:1'
        fruit['papaya'] = 'green'
        fruit['raspberry'] = 'blue'
        fruit['raspberry'] = 'red'
        assert fruit['raspberry'] == 'red'
        fruit['cranberry'] = 'red'
        assert 'raspberry' in fruit
        assert fruit['raspberry'] == 'red'

        fruit.cardinality = '1:M'
        fruit['cranberry'] = 'round'
        fruit['lemon'] = 'sour'
        fruit['cranberry'] = 'sour'
        assert 'lemon' not in fruit
        assert len(fruit['cranberry']) > 1
        fruit['pear'] = 'sweet'

        fruit.cardinality = 'M:M'
        fruit['apple'] = 'sweet'
        assert len(fruit['apple']) == 1
        fruit['apple'] = 'fruit'
        assert len(fruit['apple']) == 2

    def test_composition(self):
        fruit = Function()
        fruit['apple'] = 'red'
        fruit['pear'] = 'yellow'
        colors = Isomorphism()
        colors['yellow'] = '0:1:1'
        colors['red'] = '1:0:0'
        assert (fruit * colors).cardinality == 'M:1'
        assert Isomorphism(fruit * colors).cardinality == '1:1'
        properties = Relation()
        properties['red'] = 'sanguine'
        properties['red'] = 'pinkish'
        properties['red'] = 'bloody'
        assert len(fruit * properties) == 1
        assert len(properties * fruit) == 0

    def test_arithmetic(self):
        colors = Isomorphism()
        colors['yellow'] = '0:1:1'
        colors['red'] = '1:0:0'
        fruit = Isomorphism()
        fruit['apple'] = 'red'
        fruit['pear'] = 'yellow'
        funny = fruit + colors
        assert len(funny) == len(fruit) + len(colors)
        funny -= colors
        assert funny == fruit

    def test_freeze(self):
        f = self.fruit
        c = self.colors
        f1 = f.copy()
        f1['something'] = 'else'
        assert 'something' in f1
        assert f1 != f
        del f1['apple']
        assert 'apple' not in f1
        f2 = self.fruit.freeze()
        f2['something'] = 'else'
        assert f2 == f
        del f2['apple']
        assert 'apple' in f2

    def test_crosss_product(self):
        fruit = self.fruit
        colors = self.colors
        assert len(fruit.cross(colors)) == len(fruit) * len(colors)

    def test_pipe(self):
        fruit = self.fruit
        new = fruit * (lambda x: x + '1') * (lambda x: x.upper())
        assert len(new) == len(fruit)
        new = (~fruit) * (lambda x: x + '1') * (lambda x: x.upper())
        assert len(new) == len(~fruit)
        new = fruit * \
            (lambda x: x if x not in ['shiny', 'red', 'round'] else None)
        assert 'apple' not in new
        new = fruit * (lambda x: x if x in ['shiny', 'red', 'round'] else None)
        assert 'kiwi' not in new
        assert 'apple' in new

    def test_zero(self):
        fruit=self.fruit
        more=fruit+Zero()
        for key in fruit:
            assert more[key] == fruit[key]

    def test_unity(self):
        unity = Unity()
        fruit = self.fruit
        assert len(fruit*unity) == len(fruit)
        back = fruit * ~fruit # not identity, but kind of
        for key in back:
            assert key in back[key]

        more = Relation(cardinality='1:M')
        more.update(fruit)
        identity = more * ~more  # identity
        for key in identity:
            assert key == key


if __name__ == '__main__':
    unittest.main()