Pipeline.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
===============
[![PyPi Status](https://img.shields.io/pypi/v/Pipeline.py.svg)](https://pypi.python.org/pypi/Pipeline.py)
[![TravisCI Build Status](https://travis-ci.org/KOLANICH/Pipeline.svg?branch=master)](https://travis-ci.org/KOLANICH/Pipeline.py)
[![Coveralls Coverage](https://img.shields.io/coveralls/KOLANICH/Pipeline.py.svg)](https://coveralls.io/r/KOLANICH/Pipeline)
[![Libraries.io Status](https://img.shields.io/librariesio/github/KOLANICH/Pipeline.py.svg)](https://libraries.io/github/KOLANICH/Pipeline.py)
[![Gitter.im](https://badges.gitter.im/Pipeline.py/Lobby.svg)](https://gitter.im/Pipeline.py/Lobby)

It's a framework to create processing hierarchcal pipelines.

Requirements
------------
* [```Python 3```](https://www.python.org/downloads/). ```Python 2``` is dead, stop raping its corpse. Use ```2to3``` with manual postprocessing to migrate incompatible code to ```3```. It shouldn't take so much time.


Tutorial
--------
Here is [example1.ipynb](./examples/example1.ipynb). For other examples see the [examples dir](./examples/).

<details>
<summary>The code</summary>

```python
import importlib
import Pipeline
importlib.reload(Pipeline)
from Pipeline import *
class A(
	Pipeline( # a ctor of a pipeline object
		{"pipeline1", "pipeline2"}, # the methods making pipelines bodies
		{"do1", "do2", "wanna"} # the methods to be replaced with the impl of the very base pipeline class
	)
):
	def do1(self, a):
		print(__class__.__name__, self.__class__.__name__, "do1", a, "+2=", (a+2))
		return a+2
	def do2(self, a):
		print(__class__.__name__, self.__class__.__name__, "do2", a, "+3=", (a+3))
		return a+3
	def wanna(self, a):
		print(__class__.__name__, self.__class__.__name__, "wanna")
		return True
	
	def pipeline1(cls, self, a): # NOTE THE SIGNATURE. The first argument is reduced. Don't use the kwargs for the first element!
		if cls.wanna(self, a):
			a=cls.do1(self, a)# NOTE HOW THE METHODS ARE CALLED!
		return a
	def pipeline2(cls, self, a):
		if cls.wanna(self, a):
			a=cls.do2(self, a)
		return a
class B(A):
	def do1(self, a):
		print(__class__.__name__, self.__class__.__name__, "do1", a, "*2=", (a*2))
		return a*2
	def do2(self, a):
		print(__class__.__name__, self.__class__.__name__, "do2", a, "*3=", (a*3))
		return a*3
	def wanna(self, a):
		print(__class__.__name__, self.__class__.__name__, "wanna", a, "<5", repr(a<5))
		return a<5

class C(B):
	def do1(self, a):
		print(__class__.__name__, self.__class__.__name__, "do1", a, "**2=", (a**2))
		return a**2
	#If a pipeline method is skipped, the method from the very base class is used
	#def do2(self, a):
	#	print(__class__.__name__, self.__class__.__name__, "do2", a, "**3=", (a**2))
	#	return a**3
	
	def wanna(self, a):
		print(__class__.__name__, self.__class__.__name__, "wanna", a, "<10", repr(a<10))
		return a<10
c=C()
for i in range(6):
	c.pipeline1(i)
	print("--------------")
	c.pipeline2(i)
	print("==============")
```

</details>
<details>
<summary>The output</summary>

```
A C wanna
A C do1 0 +2= 2
B C wanna 2 <5 True
B C do1 2 *2= 4
C C wanna 4 <10 True
C C do1 4 **2= 16
--------------
A C wanna
A C do2 0 +3= 3
B C wanna 3 <5 True
B C do2 3 *3= 9
C C wanna 9 <10 True
A C do2 9 +3= 12
==============
A C wanna
A C do1 1 +2= 3
B C wanna 3 <5 True
B C do1 3 *2= 6
C C wanna 6 <10 True
C C do1 6 **2= 36
--------------
A C wanna
A C do2 1 +3= 4
B C wanna 4 <5 True
B C do2 4 *3= 12
C C wanna 12 <10 False
==============
A C wanna
A C do1 2 +2= 4
B C wanna 4 <5 True
B C do1 4 *2= 8
C C wanna 8 <10 True
C C do1 8 **2= 64
--------------
A C wanna
A C do2 2 +3= 5
B C wanna 5 <5 False
C C wanna 5 <10 True
A C do2 5 +3= 8
==============
A C wanna
A C do1 3 +2= 5
B C wanna 5 <5 False
C C wanna 5 <10 True
C C do1 5 **2= 25
--------------
A C wanna
A C do2 3 +3= 6
B C wanna 6 <5 False
C C wanna 6 <10 True
A C do2 6 +3= 9
==============
A C wanna
A C do1 4 +2= 6
B C wanna 6 <5 False
C C wanna 6 <10 True
C C do1 6 **2= 36
--------------
A C wanna
A C do2 4 +3= 7
B C wanna 7 <5 False
C C wanna 7 <10 True
A C do2 7 +3= 10
==============
A C wanna
A C do1 5 +2= 7
B C wanna 7 <5 False
C C wanna 7 <10 True
C C do1 7 **2= 49
--------------
A C wanna
A C do2 5 +3= 8
B C wanna 8 <5 False
C C wanna 8 <10 True
A C do2 8 +3= 11
==============
```

</details>
