import unittest
import os
import re

from src.blogparser import BlogParser, mdSyntax


def openSampleFile(fileName):
	testFolder = os.path.dirname(__file__)
	with open(os.path.join(testFolder, "sampleFiles/%s"%fileName), "r") as f:
		retVal = f.read()
	return retVal

class BlogParserTester(unittest.TestCase):
	def test_preEscape2(self):
		self.test_preEscape(level=2)
	
	def test_preEscape(self, level=1):
		syntax = mdSyntax[0]
		func = syntax[1]
		if hasattr(BlogParser, func):
			func = getattr(BlogParser, func)
		
		option = None
		if 2 < len(syntax):
			option = syntax[2]
	
		mdFile = openSampleFile("preTest.%d.md"%level)
		
		searchedPreTags = re.findall(syntax[0], mdFile, flags=option)
		for i, v in enumerate(searchedPreTags):
			compilledMarkdown = BlogParser.escapePre(None, v)
			answer = openSampleFile("preTest.%d.%d.html"%(level, i+1))
			self.assertEqual(compilledMarkdown, answer)
			print(v[0], compilledMarkdown)
			mdFile = mdFile.replace(v[0], compilledMarkdown, 1)
		self.assertEqual(openSampleFile("preTest.%d.html"%level), mdFile)