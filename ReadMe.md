Pipeline.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
===============
[![PyPi Status](https://img.shields.io/pypi/v/Pipeline.py.svg)](https://pypi.python.org/pypi/Pipeline.py)
~~[![GitLab Build Status](https://gitlab.com/KOLANICH/Pipeline.py/badges/master/pipeline.svg)](https://gitlab.com/KOLANICH/Pipeline.py/pipelines/master/latest)~~
~~![GitLab Coverage](https://gitlab.com/KOLANICH/Pipeline.py/badges/master/coverage.svg)~~
[![Libraries.io Status](https://img.shields.io/librariesio/github/KOLANICH/Pipeline.py.svg)](https://libraries.io/github/KOLANICH/Pipeline.py)
[![Code style: antiflash](https://img.shields.io/badge/code%20style-antiflash-FFF.svg)](https://codeberg.org/KOLANICH-tools/antiflash.py)

It's a framework to create processing hierarchical pipelines.

Tutorial
--------
Here is [example1.ipynb](./examples/example1.ipynb)[![NBViewer](https://nbviewer.org/static/ico/ipynb_icon_16x16.png)](https://nbviewer.org/urls/codeberg.org/KOLANICH-libs/Pipeline.py/raw/branch/master/examples/example1.ipynb). For other examples see the [examples dir](./examples/). 

<details>
<summary>The code</summary>

```python
import importlib
import Pipeline
importlib.reload(Pipeline)
from Pipeline import *
class DemoPipeline(
	Pipeline( # a ctor of a pipeline object
		{"pipeline1", "pipeline2"}, # the methods making pipelines bodies
	)
):
	def pipeline1(self, stage, a): # NOTE THE SIGNATURE. The first argument is the one returned and passed to the next stage. It must be present. Don't use the kwargs for the first element!
		if stage.wanna(self, a):
			a=stage.do1(self, a)# NOTE HOW THE METHODS ARE CALLED!
		return a
	def pipeline2(self, stage, a):
		if stage.wanna(self, a):
			a=stage.do2(self, a)
		return a
class A(
	Stage( # a ctor of a pipeline object
		{"do1", "do2", "wanna"} # the methods to be replaced with the impl of the very base pipeline class
	)
):
	def do1(pipeline, a):
		print(__class__.__name__, pipeline.__class__.__name__, "do1", a, "+2=", (a+2))
		return a+2
	def do2(pipeline, a):
		print(__class__.__name__, pipeline.__class__.__name__, "do2", a, "+3=", (a+3))
		return a+3
	def wanna(pipeline, a):
		print(__class__.__name__, pipeline.__class__.__name__, "wanna")
		return True
class B(A):
	def do1(pipeline, a):
		print(__class__.__name__, pipeline.__class__.__name__, "do1", a, "*2=", (a*2))
		return a*2
	def do2(pipeline, a):
		print(__class__.__name__, pipeline.__class__.__name__, "do2", a, "*3=", (a*3))
		return a*3
	def wanna(pipeline, a):
		print(__class__.__name__, pipeline.__class__.__name__, "wanna", a, "<5", repr(a<5))
		return a<5

class C(B):
	def do1(pipeline, a):
		print(__class__.__name__, pipeline.__class__.__name__, "do1", a, "**2=", (a**2))
		return a**2
	#If a pipeline method is skipped, the method from the very base class is used
	#def do2(pipeline, a):
	#	print(__class__.__name__, pipeline.__class__.__name__, "do2", a, "**3=", (a**2))
	#	return a**3
	
	def wanna(pipeline, a):
		print(__class__.__name__, pipeline.__class__.__name__, "wanna", a, "<10", repr(a<10))
		return a<10

c=DemoPipeline([A, B, C])
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
A DemoPipeline wanna
A DemoPipeline do1 0 +2= 2
B DemoPipeline wanna 2 <5 True
B DemoPipeline do1 2 *2= 4
C DemoPipeline wanna 4 <10 True
C DemoPipeline do1 4 **2= 16
--------------
A DemoPipeline wanna
A DemoPipeline do2 0 +3= 3
B DemoPipeline wanna 3 <5 True
B DemoPipeline do2 3 *3= 9
C DemoPipeline wanna 9 <10 True
A DemoPipeline do2 9 +3= 12
==============
A DemoPipeline wanna
A DemoPipeline do1 1 +2= 3
B DemoPipeline wanna 3 <5 True
B DemoPipeline do1 3 *2= 6
C DemoPipeline wanna 6 <10 True
C DemoPipeline do1 6 **2= 36
--------------
A DemoPipeline wanna
A DemoPipeline do2 1 +3= 4
B DemoPipeline wanna 4 <5 True
B DemoPipeline do2 4 *3= 12
C DemoPipeline wanna 12 <10 False
==============
A DemoPipeline wanna
A DemoPipeline do1 2 +2= 4
B DemoPipeline wanna 4 <5 True
B DemoPipeline do1 4 *2= 8
C DemoPipeline wanna 8 <10 True
C DemoPipeline do1 8 **2= 64
--------------
A DemoPipeline wanna
A DemoPipeline do2 2 +3= 5
B DemoPipeline wanna 5 <5 False
C DemoPipeline wanna 5 <10 True
A DemoPipeline do2 5 +3= 8
==============
A DemoPipeline wanna
A DemoPipeline do1 3 +2= 5
B DemoPipeline wanna 5 <5 False
C DemoPipeline wanna 5 <10 True
C DemoPipeline do1 5 **2= 25
--------------
A DemoPipeline wanna
A DemoPipeline do2 3 +3= 6
B DemoPipeline wanna 6 <5 False
C DemoPipeline wanna 6 <10 True
A DemoPipeline do2 6 +3= 9
==============
A DemoPipeline wanna
A DemoPipeline do1 4 +2= 6
B DemoPipeline wanna 6 <5 False
C DemoPipeline wanna 6 <10 True
C DemoPipeline do1 6 **2= 36
--------------
A DemoPipeline wanna
A DemoPipeline do2 4 +3= 7
B DemoPipeline wanna 7 <5 False
C DemoPipeline wanna 7 <10 True
A DemoPipeline do2 7 +3= 10
==============
A DemoPipeline wanna
A DemoPipeline do1 5 +2= 7
B DemoPipeline wanna 7 <5 False
C DemoPipeline wanna 7 <10 True
C DemoPipeline do1 7 **2= 49
--------------
A DemoPipeline wanna
A DemoPipeline do2 5 +3= 8
B DemoPipeline wanna 8 <5 False
C DemoPipeline wanna 8 <10 True
A DemoPipeline do2 8 +3= 11
==============
```

</details>
