#!/usr/bin/env python3
__all__=("Pipeline", "PipelineInterruptedException")
__author__="KOLANICH"
__license__="Unlicense"
__copyright__=r"""
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org/>
"""

def decorate(func):
	"""A function to decorate functions forming a body of a pipeline in PipelineMeta metaclass."""
	def pipeline(self, res, *args, **kwargs):
		for cls in self.__class__.specialMro:
			try:
				res=func(cls, self, res, *args, **kwargs)
			except Exception as ex:
				raise PipelineInterruptedException(args, kwargs, cls, ex)
		return (res, cls)
	pipeline.__name__=func.__name__
	pipeline.__doc__=(func.__doc__+"\n\n" if func.__doc__ else "") +"It's a pipeline!"
	return pipeline

def Pipeline(pipelineBodyMethods:set, preferBaseImplementationForThisNames:set, depthCorrection:int=0):
	"""A factory function to create a pipeline class.
	`pipelineBodyMethods` is a set of names of methods containing pipelines bodies. These methods MUST have (in this version) the signature def methodName(cls, self, passedArg, *args, **kwargs) and MUST return the thing you want to be passed as `passedArg` argument.
	`preferBaseImplementationForThisNames` is a set of names of methods, which must prefer the implementation defined in the very base class if it is not defined. Usually these are passthrough methods doing no effect, so if you skip their definition, it doesn't disrupt the pipeline. I recommend to define the base implementation full of passthrough methods and then inherit it. Also these passthrough methods may be a good place to insert some debug logging code.
	`depthCorrection` is an integer meaning how much of pipeline to strip from the beginning. It should be useful if anyone wanted to extend my pipeline implementation with the own one. Usually you don't need it.
	"""
	pipelineBodyMethods=set(pipelineBodyMethods)
	preferBaseImplementationForThisNames=set(preferBaseImplementationForThisNames)
	if not preferBaseImplementationForThisNames:
		raise ValueError("preferBaseImplementationForThisNames must be non-empty")
	if not pipelineBodyMethods:
		raise ValueError("pipelineBodyMethods must be non-empty")
	if (pipelineBodyMethods & preferBaseImplementationForThisNames):
		raise ValueError("pipelineBodyMethods must not intersect preferBaseImplementationForThisNames")
	
	class PipelineMeta(type):
		"""A metaclass to create pipelines. Use `Pipeline` class instead."""
		def __new__(cls, className, parents, attrs, *args, **kwargs):
			if len(parents) > 1:
				raise NotImplementedError("I don't know how it behaves in the case4 of multiple inheritance, so it is not supported for now. The thing may be broken in many places because everywhere it was assummed that there is exactly one parent.")
			
			specialMro=attrs["specialMro"]=[]
			mcls=parents[0]
			while mcls is not object:
				specialMro.append(mcls)
				mcls=mcls.__base__
			if specialMro:
				del(specialMro[-1]) # -1 for exclusion of Pipeline class itself
			if depthCorrection and specialMro:
				del(specialMro[-depthCorrection])
			specialMro.reverse()
			
			for name in (set(attrs.keys()) & pipelineBodyMethods):
				attrs[name]=decorate(attrs[name])
			
			if specialMro:
				for name in preferBaseImplementationForThisNames:
					if name not in attrs:
						attrs[name]=getattr(specialMro[0], name)
			
			res=super().__new__(cls, className, parents, attrs, *args, **kwargs)
			res.specialMro.append(res)
			res.specialMro=tuple(res.specialMro)
			return res
	class Pipeline(object, metaclass=PipelineMeta):
		"""A base class for a pipeline. Inherit from it to create an own pipeline."""
		pass
	return Pipeline

class PipelineInterruptedException(Exception):
	pass