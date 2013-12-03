"""
Borg and more than one module, Jan Wender, 2001/10/11
If you want to use the Borg pattern from more than one module,
it works as follows: Extract the Borg Pattern into a module and a
class of its own: borg.py:

Let your class in a separate module inherit from Borg and call Borg's
initializer in your __init__:

import BorgSingleton
class Test(BorgSingleton.Borg):
  def __init__(self):
     BorgSingleton.Borg.__init__(self)

Although sounding like a swedish chef, it works now.
The state is shared across all modules using the Test class. 
"""

class Borg:
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state
    # and whatever else you want in your class -- that's all!
    
