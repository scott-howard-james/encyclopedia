# standard
import unittest
import tempfile
import typing
# external
from nits.file import CSV
from encyclopedia import Unindexed

# utilities

def islist(thing):
    '''
    Open to other ideas here.
    Note that being a string is *not* the only other option for thing
    ToDo: move this to nits
    '''
    return isinstance(thing, (list, tuple))

def listed(thing):
    return thing if islist(thing) else [thing]

class EAV(dict, Unindexed):
    '''
    Container for storing small-ish EAV "triples" (Entity-Atrribute-Value).
    Intent of class is to provide dictionary-like access rather than large-scale data analysis functionality.
    Internally, EAV is stored as a dictionary (key:E) of dictionaries (key:A,value:V)
    '''
    EAV = ENTITY, ATTRIBUTE, VALUE = 'entity', 'attribute', 'value'

    def __init__(self, data=None,
        fmt: str = None, # forced input formatter (necessary for some formats)
        vcast=str, # default value cast
        acast=str, # attribute cast
        ecast=str, # entity cast
        defaults=None, # defaults when attribute not found
        vcasts=None): # specific casts (by attribute)
        '''
        - fmt (one of the following ...)
            - dict: dictionary of dictionaries (auto-detected)
            - file: CSV of triples  (auto-dected)
            - triple: list of EAV dictionaries  (defaulted)
            - column: list of entity-rows with field names as first element (must force this option)
        - vcast: default value cast
        - acast: attribute cast
        - ecast: entity cast
        - defaults: dictionary of defaults for specific attributes
        - vcasts: dictionary of casting for specific attributes

        '''

        if fmt is None:
            if data is None:
                fmt = 'triple' # although doesn't matter
            elif isinstance(data, str):
                fmt = 'file'
            elif isinstance(data, dict):
                fmt = 'dict'
            elif isinstance(data, typing.Iterable):
                fmt = 'triple'
            else:
                assert False # do not understand this data

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
            if fmt == 'file' :
                fmt = 'triple'
                data = CSV.read(data)

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
                        e, a, v = d[EAV.ENTITY], d[EAV.ATTRIBUTE], d[EAV.VALUE]
                    else:
                        e, a, v = d
                    self[e, a] = v
            else:
                print(fmt + ' not supported')
                assert False

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

    def compose(self, other, field='value', entities=None):
        new = self.copy_style()

        if isinstance(other, EAV):
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
            for entity in self._check_entities(entities):
                new[entity, field] = other(self[entity])
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
        '''
        Usage:

                eav[entity, attribute]

        Notes:

        - eav[:, attribute]: new EAV with all entities and but only attribute(s) specified
        - eav[entity,:]:  new EAV with only entity (ies) specified
        '''

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
                return _get(attributes=listed(a))
            elif isinstance(a, slice):
                return _get(entities=listed(e))
            elif islist(a) or islist(e):
                return _get(entities=listed(e), attributes=listed(a))
            else:
                assert e in self
                if a in self[e]:
                    return self[e][a]
                elif a in self.defaults:
                    return self.defaults[a]
                else:
                    return None
        else:
            return dict.__getitem__(self, thing)

    def __setitem__(self, thing, value):
        '''
        Usage:

                eav[entity, attribute] = value

        Notes:

        - eav[:, attribute] = value: assigns all entities a new attribute with a fixed value
        '''

        def _set(entity, attribute, value):
            e, a = self.ecast(entity), self.acast(attribute)
            if a in self.vcasts:
                v = self.vcasts[a](value)
            else:
                v = self.vcast(value)
            if e not in self:
                self._new_entity(e)
            self[e][a] = v

        if isinstance(thing, tuple):
            e, a = thing
            if isinstance(a, slice):
                assert False
            elif isinstance(e, slice):
                assert e.start == e.stop == None
                for entity in self:
                    for attribute in listed(a):
                        _set(entity, attribute, value)
            else:
                for entity in listed(e):
                    for attribute in listed(a):
                        _set(entity, attribute, value)
        else:
            assert isinstance(value, dict) and len(value) > 0
            for k, v in value.items():
                self[thing, k] = v

    def __delitem__(self, thing):
        '''
        Use 2-tuple as in:

            del eav[entity, attribute]
        '''

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
            elif islist(e) or islist(a):
                remove(attributes=listed(a), entities=listed(e))
            else:
                del self[e][a]
        else:
            return dict.__delitem__(self, thing)

    def attributes(self, entities=None):
        '''
        Computationally determine which attributes are used
        '''
        result = []
        for entity in self._check_entities(entities):
            for attribute in self[entity].keys():
                if attribute not in result:
                    result.append(attribute)
        return result

    def rename(self, renames, entities=None):
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

    def table_str(self, attributes=None, entities=None):
        atts = list(self._check_attributes(attributes, entities))
        def image(e, a):
            return '' if self[e, a] is None else str(self[e, a])
        def row():
            yield '\t'.join(['entity', *atts])
            for entity in self._check_entities(entities):
                yield '\t'.join([entity] + [image(entity, a) for a in atts])
        return '\n'.join(list(row()))

    def labeled_str(self, entities=None):
        def row():
            for entity in self._check_entities(entities):
                yield entity + ': ' + ' '.join([str(k1) + '(' + str(v1) + ')' for k1, v1 in self[entity].items()])
        return '\n'.join(row())

    def __str__(self):
        return self.table_str()

    def write(self, filename):
        CSV.write(self.triples(), filename, fields=EAV.EAV)

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
            (2, 0, 6, 33, 'poor', 1)], vcast=int, vcasts=self.vcasts, fmt='column')

    def test_io(self):
        t1 = self.t1
        with tempfile.NamedTemporaryFile() as file:
            file.close()
            t1.write(file.name)
            t2 = EAV(file.name,
                vcasts=self.vcasts,
                vcast=int)
        assert t1 == t2
        assert t1['Fred', 'visits'] == 0
        assert t1['2', 'visits'] == 6

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
        t1 = self.t1
        t1.table_str()
        t1.labeled_str()
        t1.table_str(['age'])

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
