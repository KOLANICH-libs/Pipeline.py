#!/usr/bin/env python3
import os, sys
import unittest
import itertools
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from collections import OrderedDict
dict=OrderedDict

from Pipeline import *

class Base(Pipeline({"pipelineA", "pipelineB"}, {"part"})):
	def __init__(self):
		self.res=[]
	def part(self, arg):
		return ("part", self.__class__.__name__, __class__.__name__, arg+1)
	def nonpart(self, arg):
		return ("nonpart", self.__class__.__name__, __class__.__name__, arg+1)
	def pipelineA(cls, self, arg):
		res=cls.part(self, arg)
		self.res.append(res)
		return res[-1]
	def pipelineB(cls, self, arg):
		res=cls.nonpart(self, arg)
		self.res.append(res)
		return res[-1]

class Simple(Base):
	def part(self, arg):
		return ("part", self.__class__.__name__, __class__.__name__, arg+1)
	def nonpart(self, arg):
		return ("nonpart", self.__class__.__name__, __class__.__name__, arg+1)

class BaseImplementationRedefined(Simple):
	pass
class BaseImplementationRedefinedDegenerate(Base):
	pass

class TestException(Exception):
	pass

class Errored(Simple):
	def part(self, arg):
		raise TestException("part", self.__class__.__name__, __class__.__name__, arg+1)
	def nonpart(self, arg):
		raise TestException("nonpart", self.__class__.__name__, __class__.__name__, arg+1)
	pass

class Tests(unittest.TestCase):
	def getRes(cls, pipelineLetter):
		obj=cls()
		getattr(obj, "pipeline"+pipelineLetter)(0)
		return obj.res
	
	def baseTest(self, cls, pipelineLetter, reference):
		self.assertEqual(self.__class__.getRes(cls, pipelineLetter), reference)
	def exceptionTest(self, cls, pipelineLetter, finalStageCls, exceptionType):
		with self.assertRaises(PipelineInterruptedException) as cm:
			__class__.getRes(Errored, pipelineLetter)
		(args, kwargs, fsCls, ex)=cm.exception.args
		self.assertIs(fsCls, finalStageCls)
		self.assertIs(ex.__class__, exceptionType)
	
	def testBasePart(self):
		self.baseTest(Base, "A", [('part', Base.__name__, Base.__name__, 1)])
	def testBaseNonPart(self):
		self.baseTest(Base, "B", [('nonpart', Base.__name__, Base.__name__, 1)])
	def testSimplePipelinePart(self):
		self.baseTest(Simple, "A", [
			('part', Simple.__name__, Base.__name__, 1),
			('part', Simple.__name__, Simple.__name__, 2)
		])
	def testSimplePipelineNonPart(self):
		self.baseTest(Simple, "B", [
			('nonpart', Simple.__name__, Base.__name__, 1),
			('nonpart', Simple.__name__, Simple.__name__, 2)
		])
	def testRedefinedWithBaseImplementationForPart(self):
		self.baseTest(BaseImplementationRedefined, "A", [
			('part', BaseImplementationRedefined.__name__, Base.__name__, 1),
			('part', BaseImplementationRedefined.__name__, Simple.__name__, 2),
			('part', BaseImplementationRedefined.__name__, Base.__name__, 3)
		])
	def testNotRedefinedWithBaseImplementationForNonPart(self):
		self.baseTest(BaseImplementationRedefined, "B", [
			('nonpart', BaseImplementationRedefined.__name__, Base.__name__, 1),
			('nonpart', BaseImplementationRedefined.__name__, Simple.__name__, 2),
			('nonpart', BaseImplementationRedefined.__name__, Simple.__name__, 3)
		])
	def testRedefinedWithBaseImplementationForPartDegenerate(self):
		self.baseTest(BaseImplementationRedefinedDegenerate, "A", [
			('part', BaseImplementationRedefinedDegenerate.__name__, Base.__name__, 1),
			('part', BaseImplementationRedefinedDegenerate.__name__, Base.__name__, 2)
		])
	def testNotRedefinedWithBaseImplementationForNonPartDegenerate(self):
		self.baseTest(BaseImplementationRedefinedDegenerate, "B", [
			('nonpart', BaseImplementationRedefinedDegenerate.__name__, Base.__name__, 1),
			('nonpart', BaseImplementationRedefinedDegenerate.__name__, Base.__name__, 2)
		])
	def testErroredRedefinedWithBaseImplementation(self):
		self.exceptionTest(Errored, "A", Errored, TestException)
	def testErroredNotRedefinedWithBaseImplementation(self):
		self.exceptionTest(Errored, "B", Errored, TestException)


if __name__ == '__main__':
	unittest.main()
