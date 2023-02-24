# standard
import unittest
import typing
# external
from encyclopedia import Unindexed

class EAV(dict, Unindexed):
    '''
    Container for storing smallish EAV "triples" (Entity-Attribute-Value).
    - intent of class is to provide dictionary-like access rather than data analysis functionality
    - internally, EAV is stored as a dictionary (key:E) of dictionaries (key:A,value:V)
    - class supports encyclopedic operations e.g. subtraction (difference) and addition (union)

    set-ting:

        eav[entity, attribute] = value
        eav[[entity1, ...], attribute] = value
        eav[[entity1, ...], attribute] = [value1, ...] # len(entities) must equal len(values)
        eav[:, attribute] = value #  assign all entities same value for attribute

    get-ting:

        eav[entity, attribute] # value for a specific attribute
        eav[entity] #  dictionary of elements referenced by entity

    get-ting producing new EAV:

        eav[:, attribute] # new EAV with all entities and but only one attribute
        eav[:, [attribute1, attribute2]] # new EAV with all entities and but only specified attributes
        eav[entity,:] #  new EAV with only one entity
        eav[[entity1, ...],:] #  new EAV with only specified entities

    Unsupported at this time:

        eav[entity, :] = value # ERROR
        eav[entity, [attribute1, ...]] = [value1, ...] # ERROR
    '''

    def __init__(self, data=None,
        fmt: str = None,
        fields = ('entity', 'attribute', 'value'),
        vcast=None,
        acast=str,
        ecast=str,
        defaults=None,
        vcasts=None):
        '''
        - fmt (type may be specified using one of the following *strings*  ...)
            - dict: dictionary of dictionaries (auto-detected)
            - triple: list of EAV dictionaries/tuples  (defaulted)
            - column: list of records with field names as first row and entities on first column (must force this option)
        - vcast: value cast e.g. int
        - acast: attribute cast e.g. str
        - ecast: entity cast e.g. str
        - defaults: dictionary of defaults for specific attributes
        - vcasts: dictionary of casting for specific attributes
        '''

        self.fields = ENTITY, ATTRIBUTE, VALUE = fields

        if fmt is None:
            if data is None:
                fmt = 'triple'
            elif isinstance(data, dict):
                fmt = 'dict'
            elif isinstance(data, typing.Iterable):
                fmt = 'triple'
            else:
                assert False # do not understand this data format

        if not defaults:
            self.defaults = {} # keys are attributes
        else:
            self.defaults = defaults

        if not vcasts:
            self.vcasts = {} # keys are attributes
        else:
            self.vcasts = vcasts

        self.vcast = vcast
        self.ecast = ecast
        self.acast = acast

        Unindexed.__init__(self)
        dict.__init__(self)
        if data is not None:
            get = iter(data)
            if fmt == 'dict' :
                d = data
                for e in d:
                    for a in d[e]:
                        self[e, a] = d[e][a]

            elif fmt == 'column':
                fields = next(get)
                d = {r[0]: dict(zip(fields[1:], r[1:])) for r in get}
                for e in d:
                    for a in d[e]:
                        self[e, a] = d[e][a]

            elif fmt == 'triple':
                for d in data:
                    if isinstance(d, dict):
                        e, a, v = d[ENTITY], d[ATTRIBUTE], d[VALUE]
                    else:
                        e, a, v = d
                    self[e, a] = v
            else:
                print(fmt + ' not supported')
                assert False

    @staticmethod
    def is_list(thing):
        # return isinstance(thing, (list, tuple))
        return isinstance(thing, list)

    @staticmethod
    def to_list(thing):
        return thing if EAV.is_list(thing) else [thing]

    def _new_entity(self, entity):
        return dict.__setitem__(self, entity, {})

    def _check_entities(self, entities=None):
        if not entities:
            yield from self.keys()
        else:
            for entity in entities:
                if entity in self:
                    yield entity
                else:
                    print('Entity not found:' + entity)

    def _check_attributes(self, attributes=None, entities=None):
        if attributes is None:
            yield from self.attributes(entities=entities)
        else:
            yield from attributes

    def compose(self, other, entities=None):

        if isinstance(other, EAV):
            new = self.copy_style()
            new.defaults.update(other.defaults)
            new.vcasts.update(other.vcasts)
            for entity in self._check_entities(entities):
                for attribute in self[entity]:
                    value = self[entity, attribute]
                    if value in other:
                        for a, v in other[value].items():
                            new[entity, a] = v
                    else:
                        new[entity, attribute] = value

        elif callable(other):
            new = []
            for entity in self._check_entities(entities):
                new.append(other(self[entity]))
        else:
            assert False
        return new

    def copy_style(self):
        '''
        create empty EAV preserving casting and defaults.
        '''
        return EAV(data=None,
            defaults=self.defaults,
            vcasts=self.vcasts,
            vcast=self.vcast,
            ecast=self.ecast,
            acast=self.acast,
            )

    def copy(self):
        '''
        deep copy of EAV.  Preserves casting and defaults.
        '''
        return EAV(data=self,
            defaults=self.defaults,
            vcasts=self.vcasts,
            vcast=self.vcast,
            ecast=self.ecast,
            acast=self.acast,
            )

    def subtract(self, other):
        new = self.copy_style()
        for e, av in self.items():
            if e in other:
                for a, v in av.items():
                    if a not in other[e]:
                        new[e, a] = v
            else:
                for a, v in av.items():
                    new[e, a] = v
        return new

    def __getitem__(self, thing):

        def _get(attributes=None, entities=None):
            new = self.copy_style()
            for entity in self._check_entities(entities):
                for attribute in self._check_attributes(attributes, entities):
                    if attribute in self[entity]:
                        new[entity, attribute] = self[entity, attribute]
            return new

        if isinstance(thing, tuple):
            e, a = thing
            if isinstance(e, slice):
                assert e.start == e.stop == None
            if isinstance(a, slice):
                assert a.start == a.stop == None
            if isinstance(e, slice) and isinstance(a, slice):
                return self.copy()
            elif isinstance(e, slice):
                return _get(attributes=EAV.to_list(a))
            elif isinstance(a, slice):
                return _get(entities=EAV.to_list(e))
            elif EAV.is_list(a) or EAV.is_list(e):
                return _get(entities=EAV.to_list(e), attributes=EAV.to_list(a))
            else:
                if e not in self:
                    print('x', e, a)
                    print(self.keys())
                    raise KeyError
                if a in self[e]:
                    return self[e][a]
                elif a in self.defaults:
                    return self.defaults[a]
                else:
                    return None
        else:
            return dict.__getitem__(self, thing)

    def __setitem__(self, thing, value):

        def _set(entity, attribute, value):
            e, a = self.ecast(entity), self.acast(attribute)
            if a in self.vcasts:
                v = self.vcasts[a](value)
            elif self.vcast is not None:
                v = self.vcast(value)
            else:
                v = value
            if e not in self:
                self._new_entity(e)
            self[e][a] = v

        if isinstance(thing, tuple):
            e, a = thing
            if isinstance(e, slice):
                assert e.start == e.stop == None
                e = list(self)
            if isinstance(a, slice):
                assert False # not yet supported
            es = EAV.to_list(e)

            if EAV.is_list(value) and not EAV.is_list(a):
                assert len(value) == len(es)
                for i, v in enumerate(value):
                    _set(es[i], a, v)
            elif not EAV.is_list(value):
                for entity in es:
                    for attribute in EAV.to_list(a):
                        _set(entity, attribute, value)
            else:
                assert False # combination not yet supported
        else:
            assert isinstance(value, dict) and len(value) > 0
            for k, v in value.items():
                self[thing, k] = v

    def __delitem__(self, thing):

        def remove(attributes=None, entities=None):
            for entity in self._check_entities(entities):
                for attribute in self._check_attributes(attributes, entities):
                    del self[entity, attribute]

        if isinstance(thing, tuple):
            e, a = thing
            if isinstance(e, slice) and isinstance(a, slice):
                assert e.start == e.stop == None
                assert a.start == a.stop == None
                remove()
            elif isinstance(e, slice):
                assert e.start == e.stop == None
                remove(attributes=a)
            elif isinstance(a, slice):
                assert a.start == a.stop == None
                remove(entities=e)
            elif EAV.is_list(e) or EAV.is_list(a):
                remove(attributes=EAV.to_list(a), entities=EAV.to_list(e))
            else:
                del self[e][a]
        else:
            return dict.__delitem__(self, thing)

    def attributes(self, entities=None):
        '''
        computationally determine which attributes are used for specified entities
        '''
        result = []
        for entity in self._check_entities(entities):
            for attribute in self[entity].keys():
                if attribute not in result:
                    result.append(attribute)
        return result

    def rename(self, renames, entities=None):
        '''
        rename attributes (... not the entities)
        '''
        new = self.copy()
        for entity in new._check_entities(entities):
            for k, v in renames.items():
                if k in new[entity]:
                    new[entity, v] = new[entity, k]
                    del new[entity, k]
        return new

    def assign(self, attribute, f, entities=None):
        for entity in self._check_entities(entities):
            self[entity][attribute] = f(self[entity])

    def triples(self):
        for k0, v0 in self.items():
            for k1, v1 in v0.items():
                yield k0, k1, v1

    def value_str(self, e, a):
        return '' if self[e, a] is None else str(self[e, a])

    def tabular(self, by_entity=False, attributes=None, entities=None):
        ents = list(self._check_entities(entities))
        atts = list(self._check_attributes(attributes, ents))

        def row_by_entity():
            yield ['', *atts]
            for e in ents:
                yield [str(e)] + [self.value_str(e, a) for a in atts]

        def row_by_attribute():
            yield ['', *ents]
            for a in atts:
                yield [str(a)] + [self.value_str(e, a) for e in ents]

        row = row_by_entity if by_entity else row_by_attribute
        yield from row()

    def string(self, sep=',', by_entity=False, attributes=None, entities=None):
        return '\n'.join([sep.join(row) for row in self.tabular(
                    by_entity=by_entity,
                    attributes=attributes,
                    entities=entities)])

    def __str__(self):
        return '\n'.join([
            ','.join([str(y) for y in x]) for x in self.triples()])

class Test_EAV(unittest.TestCase):

    def setUp(self):
        self.vcasts = {'health': str}
        self.t1 = EAV([
            ('name', 'medicines', 'visits', 'age', 'health', 'code'),
            (-3, -2, 0, 55, 'poor', 0),
            (-1, -1, 0, 79, 'good', 0),
            ('Fred', 0, 0, 11, 'ok', 0),
            ('Wilma', -1, -2, 17, 'better', 1),
            (1, 0, 4, 100, 'poor', 1),
            (2, 0, 6, 33, 'poor', 1)], vcast=int, acast = str, ecast=str, vcasts=self.vcasts, fmt='column')

    def test_compose(self):
        t1 = EAV({
            'a' :{'r':'high', 'g':.5, 'b':0},
            'b' :{'r':1, 'g':'medium', 'b':.1}
        })
        t2 = EAV({
            'high': {'r': .9, 'alpha': .5},
            'low': {'b': .9, 'alpha': .1},
            'medium': {'r': .15, 'alpha': .8},
        }, vcasts={'alpha': float})
        t3 = (t1 * t2)[:, ['r', 'g', 'b', 'alpha']]
        assert t3['a', 'alpha'] == .5
        assert t3['b', 'alpha'] == .8

    def test_compose_f(self):
        flintstones = ['Fred', 'Wilma']
        self.t1[flintstones, 'age'] = [31, 28]
        def f(e):
            return int(e['medicines'])*int(e['visits'])*int(e['age'])
        self.t1[flintstones, 'nonsense'] = f * self.t1[flintstones,:]

    def test_assign(self):
        t1 = self.t1
        t1['Barney'] = {'age': 25}
        assert 'age' in t1.attributes()
        assert 'expectancy' not in t1.attributes()
        t1['Barney', 'expectancy'] = t1['Barney', 'age'] + 11
        assert 'expectancy' not in t1['Fred']
        assert t1['Fred', 'expectancy'] is None
        t1.defaults['expectancy'] = 5
        assert 'expectancy' not in t1['Fred']
        assert t1['Fred', 'expectancy'] == 5
        t1.assign('expectancy',  lambda x: x['age'] + 11)
        assert t1['Fred', 'expectancy'] == 22
        t1[['Barney', '2'], 'expectancy'] = 79
        assert t1['Fred', 'expectancy'] == 22
        assert t1['Barney', 'expectancy'] == 79

    def test_filter(self):
        t1 = self.t1
        t2 = t1[:, :]
        assert t1 == t2
        t2 = t1[['-3', 'Fred'], ['age', 'visits']]
        assert len(t2) == len(t2.attributes()) == 2

    def test_strings(self):
        t1 = self.t1.string()

    def test_get(self):
        t1 = self.t1
        t2 = t1[:, :]
        assert t1 == t2
        assert t1['Fred', 'age'] == 11
        assert len(t1['Fred', :]) == 1
        assert len(t1[:, 'visits']) == len(t1)
        assert len(t1[:, ['medicines', 'visits']]) == len(t1)
        k1 = sorted(t1.attributes())
        assert k1 != t1.attributes()
        t2 = t1[:, k1]
        assert t1 == t2 # even though different orders

    def test_set_operations(self):
        t1 = self.t1
        t2 = EAV({'Dino':{'medicines':6, 'age': 17}, 'Pebbles':{'age': 13, 'visits': 18}})
        t3 = t2 + t1
        assert len(t3) == len(t2) + len(t1)
        del t3['Dino']
        del t3['Pebbles', 'visits']
        assert len(t3) == len(t2) + len(t1) - 1
        assert len(t3['Pebbles']) == 1

    def test_dict(self):
        t1 = self.t1
        t2 = EAV(t1, vcast=int, vcasts=self.vcasts)
        assert t1 == t2

    def test_subtract(self):
        t1 = self.t1
        t2 = t1 + t1
        assert t2 == t1
        t2 = EAV({'Dino':{'medicines':6, 'age': 17}, 'Pebbles':{'age': 13, 'visits': 18}})
        t3 = t1 + t2
        assert t3 != t1
        t4 = t3 - t2
        assert t4 == t1

    def test_remove(self):
        t1 = self.t1
        assert len(t1.attributes()) == 5
        del t1[:, ['code', 'visits']]
        assert len(t1.attributes()) == 3
        assert len(t1) == 6
        t1.defaults['age'] = -11
        t2 = t1.copy()
        del t1[:, :]
        assert len(t2.attributes()) == 3
        assert len(t1.attributes()) == 0
        assert len(t1) == 6

if __name__ == '__main__':
    unittest.main()
