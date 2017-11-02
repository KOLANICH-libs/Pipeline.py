#!/usr/bin/env python3
import os, sys
import unittest
import itertools
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from collections import OrderedDict
dict=OrderedDict

from Pipeline import *

class TestPipeline(Pipeline({"pipelineA", "pipelineB"})):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.res=[]
	def pipelineA(self, stage, arg):
		print("pipelineA", stage, arg)
		res=stage.part(self, arg)
		self.res.append(res)
		return res[-1]
	def pipelineB(self, stage, arg):
		print("pipelineB", stage, arg)
		res=stage.nonpart(self, arg)
		self.res.append(res)
		return res[-1]

class BaseStage(Stage({"part"})):
	def part(pipeline, arg):
		return ("part", pipeline.__class__.__name__, __class__.__name__, arg+1)
	def nonpart(pipeline, arg):
		return ("nonpart", pipeline.__class__.__name__, __class__.__name__, arg+1)

class SimpleStage(BaseStage):
	def part(pipeline, arg):
		return ("part", pipeline.__class__.__name__, __class__.__name__, arg+1)
	def nonpart(pipeline, arg):
		return ("nonpart", pipeline.__class__.__name__, __class__.__name__, arg+1)

class BaseImplementationRedefinedStage(SimpleStage):
	pass
class BaseImplementationRedefinedDegenerateStage(BaseStage):
	pass

class TestException(Exception):
	pass

class ErroredStage(BaseStage):
	def part(pipeline, arg):
		raise TestException("part", pipeline.__class__.__name__, __class__.__name__, arg+1)
	def nonpart(pipeline, arg):
		raise TestException("nonpart", pipeline.__class__.__name__, __class__.__name__, arg+1)
	pass

class Tests(unittest.TestCase):
	def baseTest(self, pipelineSeq, pipelineLetter, reference):
		obj=TestPipeline(pipelineSeq)
		getattr(obj, "pipeline"+pipelineLetter)(0)
		if obj.res != reference:
			print(obj.res, reference)
			self.assertEqual(obj.res, reference)
	def exceptionTest(self, pipelineSeq, pipelineLetter, finalStageCls, exceptionType):
		obj=TestPipeline(pipelineSeq)
		with self.assertRaises(PipelineInterruptedException) as cm:
			getattr(obj, "pipeline"+pipelineLetter)(0)
		(args, kwargs, fsCls, ex)=cm.exception.args
		self.assertIs(fsCls, finalStageCls)
		self.assertIs(ex.__class__, exceptionType)
	
	def testBasePart(self):
		self.baseTest([BaseStage], "A", [('part', TestPipeline.__name__, BaseStage.__name__, 1)])
	def testBaseNonPart(self):
		self.baseTest([BaseStage], "B", [('nonpart', TestPipeline.__name__, BaseStage.__name__, 1)])
	def testSimplePipelinePart(self):
		self.baseTest([BaseStage, SimpleStage], "A", [
			('part', TestPipeline.__name__, BaseStage.__name__, 1),
			('part', TestPipeline.__name__, SimpleStage.__name__, 2)
		])
	def testSimplePipelineNonPart(self):
		self.baseTest([BaseStage, SimpleStage], "B", [
			('nonpart', TestPipeline.__name__, BaseStage.__name__, 1),
			('nonpart', TestPipeline.__name__, SimpleStage.__name__, 2)
		])
	def testRedefinedWithBaseImplementationForPart(self):
		self.baseTest([BaseStage, SimpleStage, BaseImplementationRedefinedStage], "A", [
			('part', TestPipeline.__name__, BaseStage.__name__, 1),
			('part', TestPipeline.__name__, SimpleStage.__name__, 2),
			('part', TestPipeline.__name__, BaseStage.__name__, 3)
		])
	def testNotRedefinedWithBaseImplementationForNonPart(self):
		self.baseTest([BaseStage, SimpleStage, BaseImplementationRedefinedStage], "B", [
			('nonpart', TestPipeline.__name__, BaseStage.__name__, 1),
			('nonpart', TestPipeline.__name__, SimpleStage.__name__, 2),
			('nonpart', TestPipeline.__name__, SimpleStage.__name__, 3)
		])
	def testRedefinedWithBaseImplementationForPartDegenerate(self):
		self.baseTest([BaseStage, BaseImplementationRedefinedDegenerateStage], "A", [
			('part', TestPipeline.__name__, BaseStage.__name__, 1),
			('part', TestPipeline.__name__, BaseStage.__name__, 2)
		])
	def testNotRedefinedWithBaseImplementationForNonPartDegenerate(self):
		self.baseTest([BaseStage, BaseImplementationRedefinedDegenerateStage], "B", [
			('nonpart', TestPipeline.__name__, BaseStage.__name__, 1),
			('nonpart', TestPipeline.__name__, BaseStage.__name__, 2)
		])
	def testErroredRedefinedWithBaseImplementation(self):
		self.exceptionTest([BaseStage, SimpleStage, ErroredStage], "A", ErroredStage, TestException)
	def testErroredNotRedefinedWithBaseImplementation(self):
		self.exceptionTest([BaseStage, SimpleStage, ErroredStage], "B", ErroredStage, TestException)


if __name__ == '__main__':
	unittest.main()
