# -*- coding: utf-8 -*-
# Copyright (c) 2010 Rene Dohmen <rene@formatics.nl>
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


import os,sys,random

class chainGenerator:

    def __init__(self,difficulty=3):
        self.difficulty=difficulty
        self.operators=("+","-")
        self.userChain=[]
        self.realChain=[]
        self.answer=[]
        self.wrongAnswers=[]
        self.nrOfOperators=0
        self.numbersUsed=[]
        self.operatorsUsed=[]
        #print "Moeilijkheid=>%d" % self.difficulty    

    def setDifficulty(self,difficulty):
        self.difficulty=difficulty
        #print "Moeilijkheid=>%d" % self.difficulty    
    
    def getChain(self):
        #resoet list stuff:
        self.userChain=[]
        self.realChain=[]
        self.wrongAnswers=[]
        self.numbersUsed=[]
        self.operatorsUsed=[]

        #set new start number

        #get number op operators
        self.nrOfOperators=2
        #if self.difficulty<3: self.nrOfOperators=random.choice((1,2))
        #else: self.nrOfOperators=random.choice((2,3));
        
        #get a number for each operator
        for i in range(0,self.nrOfOperators): 
            self.operatorsUsed.append(random.choice(self.operators)) 
            self.numbersUsed.append(random.choice(range(1,9))) 

        # pick higher start number is first operator == "-":
        if self.operatorsUsed[0]=="-": self.startNumber=random.choice(range(20,40))
        else: self.startNumber=random.choice(range(1,20))
        lastNumber=self.startNumber
        #OK lets build the chain
        self.realChain.append(lastNumber)
        self.userChain.append(lastNumber)
        for teller in range(0,2):
            for i in range (0,self.nrOfOperators): 
                if self.operatorsUsed[i]=="+":
                    self.realChain.append("+")
                    self.realChain.append(self.numbersUsed[i])
                    self.userChain.append(lastNumber+self.numbersUsed[i])
                    lastNumber=lastNumber+self.numbersUsed[i]
                if self.operatorsUsed[i]=="-":
                    self.realChain.append("-")
                    self.realChain.append(self.numbersUsed[i])
                    self.userChain.append(lastNumber-self.numbersUsed[i])
                    lastNumber=lastNumber-self.numbersUsed[i]
                if lastNumber<0: return 0
        #random stuff to make answer more complex 
        moreDigits=random.choice((0,1))
        #print moreDigits
        if moreDigits==1:
            #one more digit:
            if self.operatorsUsed[0]=="-":
                self.realChain.append("-")
                self.realChain.append(self.numbersUsed[0])
                self.userChain.append(lastNumber-self.numbersUsed[0])
                lastNumber=lastNumber-self.numbersUsed[0]
            if self.operatorsUsed[0]=="+":
                self.realChain.append("+")
                self.realChain.append(self.numbersUsed[0])
                self.userChain.append(lastNumber+self.numbersUsed[0])
                lastNumber=lastNumber+self.numbersUsed[0]
            if lastNumber<0: return 0
            #determine correct anser:
            if self.operatorsUsed[1]=="+": self.answer=lastNumber+self.numbersUsed[1]
            if self.operatorsUsed[1]=="-": self.answer=lastNumber-self.numbersUsed[1]
        else:
            #determine correct anser:
            if self.operatorsUsed[0]=="+": self.answer=lastNumber+self.numbersUsed[0]
            if self.operatorsUsed[0]=="-": self.answer=lastNumber-self.numbersUsed[0]
            
        if self.answer<0: return 0

        self.wrongAnswers.append(self.answer)
        #print "numbersused:"
        #print self.numbersUsed 
        if len(self.numbersUsed)<2: 
            self.wrongAnswers.append(lastNumber+self.numbersUsed[0]+self.numbersUsed[0])
            self.wrongAnswers.append(lastNumber-self.numbersUsed[0]-self.numbersUsed[0])
        else:
            tempje=lastNumber+self.numbersUsed[1]
            if tempje in self.wrongAnswers: tempje=tempje+self.numbersUsed[1]
            self.wrongAnswers.append(tempje)
            tempje=lastNumber-self.numbersUsed[1]
            if tempje in self.wrongAnswers: tempje=tempje-self.numbersUsed[1]
            self.wrongAnswers.append(tempje)

        tempje=self.answer+random.choice(range(1,10))
        while tempje in self.wrongAnswers: tempje=self.answer+random.choice(range(1,10))
        self.wrongAnswers.append(tempje)

        #check for below zero answers and replace them:
        for number in self.wrongAnswers:
            if number<0: 
                tempje=self.answer+random.choice(range(1,10))
                while tempje in self.wrongAnswers: tempje=self.answer+random.choice(range(1,10))
                myIndex=self.wrongAnswers.index(number)
                self.wrongAnswers[myIndex]=tempje

        #"""print "USERCHAIN:"
        #print self.userChain    
        #print "\n"
        #"""
        #print "REALCHAIN:"
        #print self.realChain    
        #print "ANSWER:"
        #print self.answer    
        #print "ALL ANSWERS:"
        #print self.wrongAnswers    
        return 1

    def getChainAsText(self):
        retvalue=""
        for element in self.userChain:
            retvalue += `element`
            retvalue += ", "
        retvalue+= "?"
        return retvalue

if __name__ == '__main__':
    myChainGenerator=chainGenerator(1)
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    
    myChainGenerator.setDifficulty(2)
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    
    
    myChainGenerator.setDifficulty(3)
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()

    myChainGenerator.setDifficulty(4)
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()

    myChainGenerator.setDifficulty(5)
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    myChainGenerator.getChain()
    print myChainGenerator.getChainAsText()
    #myChainGenerator.getChain()
