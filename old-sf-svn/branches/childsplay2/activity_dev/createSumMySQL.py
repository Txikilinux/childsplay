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
from mysql import *

#init the ID, Sums and Chains
max=200
mySumGenerator=sumGenerator()
myChainGenerator=chainGenerator()

# get ready for Mysql
mysqlConn = MySQL("root", "" ,"localhost","braintrainer_content")

for level in range(1,7):
    for i in range(0,max):
        #generate a sum
        if level==1: mySumGenerator.getSum(nrOfOperators=1,alfabetSize=2,maxNumber=6,maxAnswer=99,operatorSet="simple")
        if level==2: mySumGenerator.getSum(nrOfOperators=1,alfabetSize=2,maxNumber=9,maxAnswer=99)
        if level==3: mySumGenerator.getSum(nrOfOperators=2,alfabetSize=3,maxNumber=9,maxAnswer=99)
        if level==4: mySumGenerator.getSum(nrOfOperators=2,alfabetSize=3,maxNumber=15,maxAnswer=99)
        if level==5: mySumGenerator.getSum(nrOfOperators=2,alfabetSize=3,maxNumber=19,maxAnswer=199)
        if level==6: mySumGenerator.getSum(nrOfOperators=2,alfabetSize=3,maxNumber=25,maxAnswer=199)
        query= "INSERT INTO `braintrainer_content`.`game_quiztext` (`ID`, `CID`, `language`, `game_theme`, `difficulty`, `question`, `answer`, `wrong1`, `wrong2`, `wrong3`, `content_checked`, `ownerID`, `createdAt`, `modifiedAt`, `locked`) VALUES (NULL, '0', '1', '49', '%s', '%s', '%s', '%s', '%s', '%s', '0', '1', NOW(), CURRENT_TIMESTAMP, 'no');" % (level,mySumGenerator.textSum,mySumGenerator.sumAnswer,mySumGenerator.wrongAnswers[1],mySumGenerator.wrongAnswers[2],mySumGenerator.wrongAnswers[3])
        mysqlConn.query(query)
        ID=mysqlConn.getInsertID()
        print "Added sum to DB, ID=%d" % ID

for level in range(5,7):
    myChainGenerator.setDifficulty(level)
    for i in range(0,max):
        chainFound=0
        while chainFound==0:
            chain=myChainGenerator.getChain()
            if chain==1: chainFound=1
        query= "INSERT INTO `braintrainer_content`.`game_quiztext` (`ID`, `CID`, `language`, `game_theme`, `difficulty`, `question`, `answer`, `wrong1`, `wrong2`, `wrong3`, `content_checked`, `ownerID`, `createdAt`, `modifiedAt`, `locked`) VALUES (NULL, '0', '1', '49', '%s', '%s', '%s', '%s', '%s', '%s', '0', '1', NOW(), CURRENT_TIMESTAMP, 'no');" % (level,myChainGenerator.getChainAsText(),myChainGenerator.answer,myChainGenerator.wrongAnswers[1],myChainGenerator.wrongAnswers[2],myChainGenerator.wrongAnswers[3])
        mysqlConn.query(query)
        ID=mysqlConn.getInsertID()
        print "Added chain to DB, ID=%d" % ID
