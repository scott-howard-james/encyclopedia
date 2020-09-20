# standard
import unittest
# import the unittests ...
from encyclopedia.templates import Test_Encyclopedia
from encyclopedia.dictionary import Test_Dictionary
from encyclopedia.eav import Test_EAV
from encyclopedia.record import Test_Record
from encyclopedia.forest import Test_Forest
from encyclopedia.relate import Test_Relation
from encyclopedia.arboretum import Test_Arboretum
from encyclopedia.xmlopedia import Test_XML
from encyclopedia.kmlopedia import Test_KML
from encyclopedia.kmlfolder import Test_KML_Folder

'''
Run regression tests on the base Encyclopedia classes
'''
if __name__ == '__main__':
    unittest.main()
