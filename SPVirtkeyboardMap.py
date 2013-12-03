# Keyboard layouts for the KeyBoard

class Base:
    def __init__(self):
        self.numbersline = ('1','2','3','4','5','6','7','8','9','0')
    
    def getlines(self):
        return (self.line0, self.line1, self.line2, self.line3)
    
class Qwerty(Base):
    def __init__(self):
        Base.__init__(self)
        self.line0 = self.numbersline    
        self.line1 = ('Q','W','E','R','T','Y','U','I','O','P')
        self.line2 = ('A','S','D','F','G','H','J','K','L','.')
        self.line3 = ('Z','X','C','V','B','N','M',',', '-')

class QwertyMinus(Base):
    def __init__(self):
        Base.__init__(self)
        self.line0 = ('Q','W','E', 'R', 'T', 'Y', 'U')
        self.line1 = ('I', 'O', 'P', 'A', 'S', 'D', 'F')
        self.line2 = ('G', 'H', 'J', 'K', 'L', 'Z', 'X')
        self.line3 = ('C', 'V', 'B', 'N', 'M', '-')

class QwertySquare(Base):
    def __init__(self):
        Base.__init__(self)
        self.line0 = ('Q','W','E', 'R', 'T', 'Y', 'U')
        self.line1 = ('I', 'O', 'P', 'A', 'S', 'D', 'F')
        self.line2 = ('G', 'H', 'J', 'K', 'L', 'Z', 'X')
        self.line3 = ('C', 'V', 'B', 'N', 'M')

class Abc(Base):
    def __init__(self):
        Base.__init__(self)
        self.line0 = self.numbersline    
        self.line1 = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
        self.line2 = ('K','L','M','N','O','P','Q','R','S',' . ')
        self.line3 = ('T','U','V','W','X','Y','Z','_',' - ')

class AbcMinus(Base):
    def __init__(self):
        Base.__init__(self)
        self.line0 = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
        self.line1 = ('H', 'I', 'J', 'K', 'L', 'M', 'N')
        self.line2 = ('O', 'P', 'Q', 'R', 'S', 'T', 'U')
        self.line3 = ('V', 'W', 'X', 'Y', 'Z', '-')

class AbcSquare(Base):
    def __init__(self):
        Base.__init__(self)
        self.line0 = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
        self.line1 = ('H', 'I', 'J', 'K', 'L', 'M', 'N')
        self.line2 = ('O', 'P', 'Q', 'R', 'S', 'T', 'U')
        self.line3 = ('V', 'W', 'X', 'Y', 'Z')

class Numbers(Base):
    def __init__(self):
        Base.__init__(self)
        self.line0 = ('7', '8', '9')
        self.line1 = ('4', '5', '6')
        self.line2 = ('1', '2', '3')
        self.line3 = ('0', '.')
        

