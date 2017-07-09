# -*- coding: utf-8 -*-
# Copyright (c) 2010 Rene Dohmen <rene@formatics.nl>
# Copyright (c) 2010 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           childsplay_sp_local
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License
# as published by the Free Software Foundation.  A copy of this license should
# be included in the file GPL-3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.


from sumGenerator import *
from chainGenerator import *

#init the ID, Sums and Chains
id=175
max=20
mySumGenerator=sumGenerator()
myChainGenerator=chainGenerator()

XML_HEADER = \
"""<?xml version="1.0" encoding="UTF-8"?>
<questions>
"""

XML_BODY = \
"""    <question id="%(id)s" type="math">
        <difficulty>%(difficulty)s</difficulty>
        <question_text audio="">%(question_text)s</question_text>
        <answer audio="">%(answer)s</answer>
        <data></data>
        <group></group>
        <wrong_answer1 audio="">%(wrong1)s</wrong_answer1>
        <wrong_answer2 audio="">%(wrong2)s</wrong_answer2>
        <wrong_answer3 audio="">%(wrong3)s</wrong_answer3>
    </question>
"""

XML_FOOOTER = \
"""</questions>
"""

class sumToXML:
    def __init__(self):
        self.xml = [XML_HEADER]
        
    def write(self, **kwargs):
        self.xml.append(XML_BODY % kwargs)
    
    def get_xml(self):
        self.xml.append(XML_FOOOTER)
        return self.xml


STX = sumToXML()

for level in range(1,6):
    for i in range(0,max):
        #generate a sum
        if level==1: mySumGenerator.getSum(nrOfOperators=1,alfabetSize=2,maxNumber=6,maxAnswer=99,operatorSet="simple")
        if level==2: mySumGenerator.getSum(nrOfOperators=1,alfabetSize=2,maxNumber=9,maxAnswer=99)
        if level==3: mySumGenerator.getSum(nrOfOperators=2,alfabetSize=3,maxNumber=9,maxAnswer=99)
        if level==4: mySumGenerator.getSum(nrOfOperators=2,alfabetSize=3,maxNumber=15,maxAnswer=99)
        if level==5: mySumGenerator.getSum(nrOfOperators=2,alfabetSize=3,maxNumber=19,maxAnswer=199)
        STX.write(id=id, \
                  question_text = mySumGenerator.textSum,\
                 answer = mySumGenerator.sumAnswer,\
                wrong1 = mySumGenerator.wrongAnswers[1],\
                wrong2 = mySumGenerator.wrongAnswers[2],\
                wrong3 = mySumGenerator.wrongAnswers[3],
                difficulty = level)
        id+=1

for level in range(4,6):
    myChainGenerator.setDifficulty(level)
    for i in range(0,max):
        chainFound=0
        while chainFound==0:
            chain=myChainGenerator.getChain()
            if chain==1: chainFound=1
        STX.write(id=id,\
                  question_text = myChainGenerator.getChainAsText(),\
                 answer = myChainGenerator.answer,\
                wrong1 = myChainGenerator.wrongAnswers[1],\
                wrong2 = myChainGenerator.wrongAnswers[2],\
                wrong3 = myChainGenerator.wrongAnswers[3],\
                difficulty = level)
        id+=1

f = open('content.xml', 'w')
f.writelines(STX.get_xml())
f.close()
print "Wrote xml file"


