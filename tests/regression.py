# standard
import unittest
# import the unittests ...
from bits.file import Test_File
from bits.time import Test_Time
from bits.cast import Test_Cast
from encyclopedia.templates import Test_Encyclopedia
from encyclopedia.dictionary import Test_Dictionary
from encyclopedia.record import Test_Record
from encyclopedia.forest import Test_Forest
from encyclopedia.relate import Test_Relation
from encyclopedia.arboretum import Test_Arboretum
from encyclopedia.xmlopedia import Test_XML
from encyclopedia.kmlopedia import Test_KML

'''
Run regression tests on the base Encyclopedia classes
'''
if __name__ == '__main__':
    unittest.main()
