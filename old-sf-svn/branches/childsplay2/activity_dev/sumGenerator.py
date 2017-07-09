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

class sumGenerator:

    def __init__(self):
        #init operators:
        self.operators=("+","-","x",":")
        self.simpleOperators=("+","-")
        self.question=None
        self.wrongAnswers=[] # contains the right and wrong answers
        self.numbers=[]
        self.sumAnswer=None
        self.pythonSum=[]
        self.textSum=""
        self.nrOfOperators=0
        self.alfabetSize=0
        self.operatorSet="normal"
        
    
    def getSum(self, nrOfOperators, alfabetSize, maxNumber, maxAnswer, operatorSet="normal"):
        self.numbers=[]
        self.operatorSet=operatorSet
        self.nrOfOperators=nrOfOperators
        self.alfabetSize=alfabetSize
        self.maxNumber=maxNumber
        self.maxAnswer=maxAnswer
        # generate needed baseNumbers for the sum
        # generate needed operator sequence
        #generate a valid answer between my constraints
        answerFound=0
        while answerFound==0:
            self.sumAnswer=self.generateAnswer()
            if self.sumAnswer<maxAnswer and self.sumAnswer>=0: answerFound=1

        #get some wrong answers and put right one also in wro
        self.wrongAnswers=[]
        self.wrongAnswers.append(self.sumAnswer)
        self.wrongAnswers.append(self.sumAnswer+1)
        if self.sumAnswer>1: self.wrongAnswers.append(self.sumAnswer-1)
        else:
            #use a digit not in self.numbers and not 1 to get a 100% unique wronganswer:
            numberFound=0
            randomNumber=0
            while numberFound==0:
                randomNumber=random.choice(range(self.sumAnswer-4,self.sumAnswer+4))
                if randomNumber>=0 and randomNumber not in self.wrongAnswers: numberFound=1
            self.wrongAnswers.append(randomNumber)
        numberFound=0
        randomNumber=0
        while numberFound==0:
            randomNumber=random.choice(range(self.sumAnswer-4,self.sumAnswer+4))
            if randomNumber>=0 and randomNumber not in self.wrongAnswers: numberFound=1
        self.wrongAnswers.append(randomNumber)


        #print self.textSum
        #print self.sumAnswer
        #print self.wrongAnswers

        

    def generateAnswer(self):
        #init sum vars
        self.numbers=[]
        self.pythonSum=[]
        #get first number to work with
        self.numbers.append(random.choice(range(1,self.maxNumber)))
        self.pythonSum.append(self.numbers[0])
        if self.nrOfOperators==1 and self.alfabetSize==1:
            if self.operatorSet=="normal": self.pythonSum.append(random.choice(self.operators))
            else: self.pythonSum.append(random.choice(self.simpleOperators))
            self.pythonSum.append(self.numbers[0])
        elif self.nrOfOperators==1 and self.alfabetSize==2:
            if self.operatorSet=="normal": self.pythonSum.append(random.choice(self.operators))
            else: self.pythonSum.append(random.choice(self.simpleOperators))
            if self.pythonSum[1]==":": # make new number 1: higher
                self.numbers.append(random.choice(range(1,self.maxNumber)))
                self.numbers[0]=self.numbers[0]*self.numbers[1]
                self.pythonSum[0]=self.numbers[0]
                self.pythonSum.append(self.numbers[1])
            else:     
                self.numbers.append(random.choice(range(1,self.maxNumber)))
                self.pythonSum.append(self.numbers[1])
        elif self.nrOfOperators==2 and self.alfabetSize==1:
            if self.operatorSet=="normal": self.pythonSum.append(random.choice(self.operators))
            else: self.pythonSum.append(random.choice(self.simpleOperators))
            self.pythonSum.append(self.numbers[0])
            #choose 2nd operator from simple to avoid "meneer van dalen" problem
            self.pythonSum.append(random.choice(self.simpleOperators))
            self.pythonSum.append(self.numbers[0])
            
        else: # 2 operators and 2 or 3 numbers
            if self.operatorSet=="normal": self.pythonSum.append(random.choice(self.operators))
            else: self.pythonSum.append(random.choice(self.simpleOperators))
            if self.pythonSum[1]==":": # make new number 1: higher
                self.numbers.append(random.choice(range(1,self.maxNumber)))
                self.numbers[0]=self.numbers[0]*self.numbers[1]
                self.pythonSum[0]=self.numbers[0]
                self.pythonSum.append(self.numbers[1])
            else:     
                self.numbers.append(random.choice(range(1,self.maxNumber)))
                self.pythonSum.append(self.numbers[1])
            #OK get ready for the last operator and number
            if self.pythonSum[1]=="-" or self.pythonSum[1]=="+":
                self.pythonSum.append(random.choice(self.simpleOperators))
                if self.alfabetSize==2: self.pythonSum.append(random.choice(self.numbers))
                else: 
                    self.numbers.append(random.choice(range(1,self.maxNumber)))
                    self.pythonSum.append(self.numbers[2])
            else:     
                if self.alfabetSize==2 and self.pythonSum[1]==":":self.pythonSum.append(random.choice(self.operators[:3]))
                else:
                    if self.operatorSet=="normal": self.pythonSum.append(random.choice(self.operators))
                    else: self.pythonSum.append(random.choice(self.simpleOperators))
                if self.alfabetSize==2: self.pythonSum.append(random.choice(self.numbers))
                else:     
                    if self.pythonSum[3]==":": #check if current sum is dividable by a number smaller than itself 
                        #calc current sum value:
                        myAnswer=self.pythonSum[0]
                        if self.pythonSum[1]=="+": myAnswer=myAnswer+self.pythonSum[2]
                        elif self.pythonSum[1]=="-": myAnswer=myAnswer-self.pythonSum[2]
                        elif self.pythonSum[1]==":": myAnswer=myAnswer/self.pythonSum[2]
                        elif self.pythonSum[1]=="x": myAnswer=myAnswer*self.pythonSum[2]
                        numberFound=0
                        lastNumber=myAnswer-1
                        while numberFound==0 and lastNumber>1:
                            lastNumber=lastNumber-1
                            if lastNumber>1 and myAnswer%lastNumber == 0 and myAnswer/lastNumber!=0: 
                                #print "%d %s %d %s %d found in div!!" % (self.pythonSum[0],self.pythonSum[1],self.pythonSum[2],self.pythonSum[3],lastNumber)
                                numberFound=1
                        if numberFound==0: return self.maxAnswer+1
                        else:
                            self.numbers.append(lastNumber)
                        self.pythonSum.append(self.numbers[2])

                    else:
                        self.numbers.append(random.choice(range(1,self.maxNumber)))
                        self.pythonSum.append(self.numbers[2])


        myAnswer=self.pythonSum[0]
        for i in range(0, len(self.pythonSum)): 
            if self.pythonSum[i]=="+": myAnswer=myAnswer+self.pythonSum[i+1]
            elif self.pythonSum[i]=="-": myAnswer=myAnswer-self.pythonSum[i+1]
            elif self.pythonSum[i]==":": myAnswer=myAnswer/self.pythonSum[i+1]
            elif self.pythonSum[i]=="x": myAnswer=myAnswer*self.pythonSum[i+1]
            else: 1
            if myAnswer<0: #
                #temp answer below zero: start over again
                return self.maxAnswer+1
        if len(self.pythonSum)==5: self.textSum="%d %s %d %s %d =" % (self.pythonSum[0], self.pythonSum[1], self.pythonSum[2], self.pythonSum[3], self.pythonSum[4])
        else: self.textSum="%d %s %d =" % (self.pythonSum[0], self.pythonSum[1], self.pythonSum[2])
        #print self.pythonSum
        return myAnswer


if __name__ == '__main__':
    mySumGenerator=sumGenerator()
    max=20
    print "level 1"
    for i in range(0,max):
        mySumGenerator.getSum(nrOfOperators=1,alfabetSize=2,maxNumber=9,maxAnswer=99, operatorSet="simple")
    print "level 2"
    for i in range(0,max):
        mySumGenerator.getSum(nrOfOperators=1,alfabetSize=2,maxNumber=9,maxAnswer=99)
    print "level 3"
    for i in range(0,max):
        mySumGenerator.getSum(nrOfOperators=2,alfabetSize=3,maxNumber=9,maxAnswer=99)
    print "level 4"
    for i in range(0,max):
        mySumGenerator.getSum(nrOfOperators=2,alfabetSize=3,maxNumber=9,maxAnswer=99)
    print "level 5"
    for i in range(0,max):
        mySumGenerator.getSum(nrOfOperators=2,alfabetSize=3,maxNumber=19,maxAnswer=199)

