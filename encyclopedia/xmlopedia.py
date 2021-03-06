# standard
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
import copy
import sys
import unittest
import xml.etree.ElementTree as et
# internal
from encyclopedia.templates import Unindexed

class XML(Unindexed):
    '''
    Forest syntax combined with an elementTree XML implementation.
    To avoid internal confusion, inherits from neither elementTree nor Arboretum directly,
    thus the tree(forest) is stored *in parallel* to the elementTree structure
    '''
    FOLD = '/' # use this delimeter to create unique identifiers

    def __init__(self):
        self.counter = 0
        self.root = None
        self.elements = None

    def _create(self, root):
        assert root is not None
        self.elements = {root:et.Element(root)}
        self.root = root

    def __iadd__(self, root):
        assert self.root is None
        self._create(root)
        return self

    def __str__(self):
        return str(self.elements)

# reading functions

    @staticmethod
    def _iterate(element, recursive=True, tag=None):
        '''
        recursive: recursive into subelements
        tag: limit to these tags during recursive iteration
        '''
        if isinstance(element, XML):
            element = element[element.root]
        if recursive:
            it = element.iter(tag)
        else:
            it = list(element)
        yield from it

    @staticmethod
    def traverse(element, tag=None):
        yield from XML._iterate(element, recursive=False, tag=tag)

    @staticmethod
    def recurse(element, tag=None):
        yield from XML._iterate(element, recursive=True, tag=tag)

    def _read(self, element, name, level):

        def clean(s):
            if '}' in s:
                return s[s.index('}') + 1:]
            else:
                return s

        def attribute(name, element):
            for key, value in element.items():
                self[name].set(key, value)

        if level == 0:
            name = clean(element.tag)
            self._create(name)

        attribute(name, element)
        for other in list(element):
            tag = clean(other.tag)
            if not list(other):
                if not other.attrib:
                    self[name, tag] = other.text
                else: # special case where component ID stored in attribute
                    for value in other.attrib.values():
                        self[name, value] = other.text
                        break # just going to use the first one we find and ignore the rest
            else:
                self[name] = oname = self.unique(tag)
                self._read(other, oname, level+1)

    def copy(self):
        return copy.deepcopy(self)

    @staticmethod
    def read(filename):
        # read file
        if filename is None:
            file = sys.stdin
        elif '://' in filename: # hackey ... but you know, whatever works
            file = urlopen(filename)
        else:
            file = open(filename, 'rt')
        # process file
        xml = XML()
        xml._read(et.parse(file).getroot(), None, 0)
        file.close()
        return xml

    def iterate(self, recursive=True, tag=None):
        yield from XML._iterate(self, recursive, tag)

    def __iter__(self):
        yield from self.iterate()

    def __len__(self):
        return len(self.elements)

# writing/assigning functions

    def __delitem__(self, key):
        assert key != self.root
        element = self.elements[key]
        element.clear()
        del self.elements[key]

    def __getitem__(self, key):
        if not isinstance(key, tuple):
            return self.elements[key]
        else:
            assert False

    def __setitem__(self, key, value):
        if not isinstance(key, tuple):
            assert value not in self.elements
            self.elements[value] = et.SubElement(self.elements[key], value.split(XML.FOLD)[-1])
        else:
            node, attr = key
            thing = et.SubElement(self.elements[node], attr)
            thing.text = str(value)

    @staticmethod
    def _indent(elem, level=0):
        i = '\n' + level * '  '
        if elem:
            if not elem.text or not elem.text.strip():
                elem.text = i + '  '
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                XML._indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def unique(self, name):
        '''
        create a unique element name
        '''
        if name not in self.elements:
            return name
        else:
            self.counter += 1
            return XML.FOLD.join([str(self.counter), name])

    def write(self, filename=None, doctype=None):
        '''
        write the XML, adding tabs for pretty-printing
        '''
        root = self.elements[self.root]
        XML._indent(root)
        etree = et.ElementTree(root)

        def _write(f):
            f.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
            if doctype is not None:
                f.write('<!DOCTYPE ' + doctype + '>\n')
            etree.write(f, encoding='unicode')

        if filename is not None:
            with open(filename, 'wt', newline='\n') as f:
                _write(f)
        else:
            _write(sys.stdout)

class Test_XML(unittest.TestCase):

    def setUp(self):
        self.xt = xt = XML()
        xt += 'trunk'
        xt['trunk'] = 'Document'
        for node in ['G1', 'G2']:
            xt['Document'] = folder = xt.unique('Folder')
            xt[folder, 'name'] = node + ' folder'
            xt[folder].set('id', node)
            for place in ['P1', 'P2']:
                xt[folder] = placemark = xt.unique('Placemark')
                xt[placemark, 'name'] = place + ' placemark'

    def test_io(self):
        xt = self.xt
        with NamedTemporaryFile() as f:
            xc = xt.copy()
            xc.write(f.name)
            xs = XML.read(f.name)
        assert et.tostring(xt.elements[xt.root]) == et.tostring(xs.elements[xs.root])
        assert et.tostring(xt.elements[xt.root]) != et.tostring(xc.elements[xc.root]) # because, tabs

    def test_del(self):
        xt = self.xt
        xc = xt.copy()
        del xc['4/Placemark']
        assert len(xc)+1 == len(xt)
        del xc['Document']

    def test_iterate(self):
        xt = self.xt
        l1 = list(xt.iterate(recursive=False))
        l2 = list(xt.iterate(recursive=True))
        l3 = [item for item in xt]
        assert len(l3) == len(l2) > len(l1)

if __name__ == '__main__':
    unittest.main()
