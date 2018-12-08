import unittest
import os
import json

from src.compiler import Compiler
from src.skin import SkinManager

sampleConfig = {
	"path":{
		"build":"build",
		"contents":"contents",
		"resource":"resources"
	},
	"site":{
		"author":{
			"nickname":"ariyn",
			"name":"MinUk Hwang",
			"email":"himnowxz@gmail.com"
		},
		"domainName":"this.ismin.uk",
		"name":"this is\nmin-uk",
		"description":"this is min-uk's personal web site.",
		"prefix":"JB-build"
	},
	"skin":"/home/wssh/JB-Blog/skins/clean blog gh pages/"
}

# print =None
class CompileTester(unittest.TestCase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.rootPath = "/tmp/JB-Blog/"
		
		if not os.path.exists(self.rootPath):
			os.mkdir(self.rootPath)
		for path in [os.path.join(self.rootPath,i) for i in sampleConfig["path"].keys()]:
			try:
				os.mkdir(path)
			except:
				pass
		with open(os.path.join(self.rootPath, "config.json"), "w") as f:
			f.write(json.dumps(sampleConfig))
			
		
	def test_init(self):
		c = Compiler(self.rootPath)
		c.compile()
		
	def test_path(self):
		c = Compiler(self.rootPath)
		self.assertEqual(c.build, "build")
		self.assertEqual(c.contentsPath, "contents")
		self.assertEqual(c.resourcePath, "resources")
		self.assertEqual(c.absContentPath, "/tmp/JB-Blog/contents")
		self.assertEqual(c.buildPath, "/tmp/JB-Blog/build")