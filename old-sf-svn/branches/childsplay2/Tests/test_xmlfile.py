
import unittest
import sys
sys.path.insert(0, '../lib')
from quizengine import Parser

TYPES = ['text', 'picture']
XMLKEYS = ['question_text','wrong_answer1', 'wrong_answer3', \
            'wrong_answer2','answer','id', 'data']
xmlpath = 'content.xml'

class UnitTestFuncs(unittest.TestCase):

    def setUp(self):
        self.xmlhash = {}
        p = Parser(xmlpath)
        self.xmlhash = p.get_xml()
        
    def test_parse_xmlfile(self):
        self.assert_(self.xmlhash)
    
    def test_xmlfile_types(self):
        xmlkeys = self.xmlhash.keys().sort()
        self.assert_(TYPES.sort() == xmlkeys)
            
    def test_text_elements(self):
        fail = []
        for i in range(1, 6):
            for hash in self.xmlhash['text'][str(i)]:
                for k in XMLKEYS:
                    try:
                        hash[k]
                    except KeyError, info:
                        fail.append(k)
        self.assertEqual(len(fail), 0, "there was a missing element")
    
    def test_picture_elements(self):
        fail = []
        for i in range(1, 2):
            for hash in self.xmlhash['picture'][str(i)]:
                for k in XMLKEYS:
                    try:
                        hash[k]
                    except KeyError:
                        fail.append(k)
        self.assertEqual(len(fail), 0,"there was a missing element")    
    
    def test_math_elements(self):
        fail = []
        for i in range(1, 6):
            for hash in self.xmlhash['math'][str(i)]:
                for k in XMLKEYS:
                    try:
                        hash[k]
                    except KeyError, info:
                        fail.append(k)
        self.assertEqual(len(fail), 0,"there was a missing element: %s" % fail)
    
#    def test_question_tuples(self):
#        pass
            

if __name__ == '__main__':
    
    unittest.main()

    
