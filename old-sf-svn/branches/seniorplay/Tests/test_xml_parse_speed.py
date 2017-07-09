
import timeit

import sys
sys.path.insert(0, '../lib')
from quizengine import Parser
xmlpath = 'content.xml'

t = timeit.Timer("Parser('%s')" % xmlpath,"from quizengine import Parser")

print 'Parsing: %s in %f seconds' % (xmlpath, t.timeit(1))




