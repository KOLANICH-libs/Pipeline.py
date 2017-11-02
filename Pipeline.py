import typing

__all__ = ("Pipeline", "PipelineInterruptedException", "Stage")
__author__ = "KOLANICH"
__license__ = "Unlicense"
__copyright__ = r"""
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute this software, either in source code form or as a compiled binary, for any purpose, commercial or non-commercial, and by any means.

In jurisdictions that recognize copyright laws, the author or authors of this software dedicate any and all copyright interest in the software to the public domain. We make this dedication for the benefit of the public at large and to the detriment of our heirs and successors. We intend this dedication to be an overt act of relinquishment in perpetuity of all present and future rights to this software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org/>
"""


def decorate(func: typing.Callable) -> typing.Callable:
	"""A function to decorate functions forming a body of a pipeline in PipelineMeta metaclass."""

	def pipeline(self, res, *args, **kwargs):
		for stage in self.stages:
			try:
				res = func(self, stage, res, *args, **kwargs)
			except Exception as ex:
				raise PipelineInterruptedException(args, kwargs, stage, ex) from ex
		return (res, stage)

	pipeline.__name__ = func.__name__
	pipeline.__doc__ = (func.__doc__ + "\n\n" if func.__doc__ else "") + "It's a pipeline!"
	return pipeline


def getClassesHierarchy(cls: typing.Type) -> typing.List[typing.Any]:
	res = []
	while cls is not object:
		res.append(cls)
		cls = cls.__base__
	return res


def Pipeline(pipelineBodyMethods: set, depthCorrection: int = 0):
	"""A factory function to create a pipeline class.
	`pipelineBodyMethods` is a set of names of methods containing pipelines bodies. These methods MUST have (in this version) the signature def methodName(cls, self, passedArg, *args, **kwargs) and MUST return the thing you want to be passed as `passedArg` argument.
	"""
	pipelineBodyMethods = set(pipelineBodyMethods)
	if not pipelineBodyMethods:
		raise ValueError("pipelineBodyMethods must be non-empty")

	class PipelineMeta(type):
		"""A metaclass to create pipelines. Use `Pipeline` class instead."""

		def __new__(cls, className, parents, attrs, *args, **kwargs):
			for name in set(attrs.keys()) & pipelineBodyMethods:
				attrs[name] = decorate(attrs[name])

			res = super().__new__(cls, className, parents, attrs, *args, **kwargs)

			return res

	class Pipeline(object, metaclass=PipelineMeta):
		"""A class for a pipeline."""

		def __init__(self, stages):
			self.stages = stages

	return Pipeline


def Stage(preferBaseImplementationForThisNames: set, depthCorrection: int = 0):
	"""A factory function to create a pipeline stage class.
	`preferBaseImplementationForThisNames` is a set of names of methods, which must prefer the implementation defined in the very base class if it is not defined. Usually these are passthrough methods doing no effect, so if you skip their definition, it doesn't disrupt the pipeline. I recommend to define the base implementation full of passthrough methods and then inherit it. Also these passthrough methods may be a good place to insert some debug logging code.
	`depthCorrection` is an integer meaning how much of class hierarchy to strip from the beginning. It should be useful if anyone wanted to extend my Stage implementation with the own one. Usually you don't need it.
	"""
	preferBaseImplementationForThisNames = set(preferBaseImplementationForThisNames)
	if not preferBaseImplementationForThisNames:
		raise ValueError("preferBaseImplementationForThisNames must be non-empty")

	class StageMeta(type):
		"""A metaclass to create pipelines. Use `Pipeline` class instead."""

		__slots__ = ()

		def __new__(cls, className, parents, attrs, *args, **kwargs):
			if len(parents) > 1:
				raise NotImplementedError("I don't know how it behaves in the cases of multiple inheritance, so it is not supported for now. The thing may be broken in many places because everywhere it was assummed that there is exactly one parent.")

			specialMro = getClassesHierarchy(parents[0])

			if specialMro:
				del specialMro[-1]  # -1 for exclusion of Stage class itself
			if depthCorrection and specialMro:
				del specialMro[-depthCorrection]

			if specialMro:
				for name in preferBaseImplementationForThisNames:
					if name not in attrs:
						attrs[name] = getattr(specialMro[-1], name)

			return super().__new__(cls, className, parents, attrs, *args, **kwargs)

	class Stage(object, metaclass=StageMeta):
		"""A base class for a stage of a pipeline. Inherit from it to create an own stage."""

		__slots__ = ()

	return Stage


class PipelineInterruptedException(Exception):
	__slots__ = ()
