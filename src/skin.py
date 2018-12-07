import os
import sys
import json
import codecs
import copy
import re

from datetime import datetime
import importlib.machinery

from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions

from .tools import DotAccessibleDict

class NoSkinConfigException(Exception):
	pass

def preFunction(t):
	setattr(t, "skinCallOrder", "pre")
	return t
def postFunction(t):
	setattr(t, "skinCallOrder", "post")
	return t
def replaceData(t):
	setattr(t, "skinCallOrder", "any")
	setattr(t, "functionType", "replaceData")
	return t
# def multiArticles(t):
# 	setattr(t, "articleNumber", "multy")
# 	return t
# def singleArticle(t):
# 	setattr(t, "articleNumber", "1")
# 	return t

def test(**kwa):
	for i in kwa:
		print(i, kwa[i] if type(kwa[i]) == DotAccessibleDict else "", type(kwa[i]))

class Skin:
	def __init__(self, data):
		self.data = data
		self.file = self.data["file"]
		mylookup = TemplateLookup(directories=[data["rootPath"]])
		self.template = Template(self.file, lookup=mylookup)
		self.varReg = re.compile("(?:{{)(.+?)(?:}})")
		self.variables = {}
# 		self.html = self.data["html"]
		self.parseVariables()
	
	def compile(self, kwargs):
		try:
			self.rendered = self.template.render(**DotAccessibleDict(kwargs))
		except:
			open("exceptions/exception", "wb").write(exceptions.html_error_template().render())
		return self.rendered
		
	def parseVariables(self):
		vars = self.findAllVar()
		for v in vars:
			name = v[1].strip()
			if name not in self.variables:
				self.variables[name] = []
			self.variables[name].append(v)
	
	def findAllVar(self):
		vars = []
		pos = 0
		
		v = True
		while pos < len(self.file) and v:
			v = self.varReg.search(self.file, pos=pos)
			if v:
				text = v.group(1)
				if "|" in text:
					text = [i.strip() for i in text.split("|")]
					text, func = text[0], text[1]
					if func == "date_to_string":
						func = lambda x:x.strftime("%Y/%m/%d")
				else:
					func = lambda x:x
				vars.append((v.group(0), text, func, v.start(), v.end()))
				pos = v.end()
		return vars

	def replace(self, name, target):
		if name in self.variables:
			for var in self.variables[name]:
				cTarget = var[2](target)
				size = var[4] - var[3] - len(cTarget)
				front, end = self.file[:var[3]], self.file[var[4]:]
				try:
					self.file = front + cTarget + end
				except TypeError as e:
					print(e)
					print(front)
					print(cTarget)
					print(end)
				for i,k,v in [(i,k,v) for k,j in self.variables.items() for i, v in enumerate(j) if var[3] < v[3]]:
					self.variables[k][i] = (v[0], v[1], v[2], v[3]-size, v[4]-size)
			del self.variables[name]
			
	def removeReplaceTags(self):
		for i,v in self.variables.items():
			for var in v:
				self.file = self.file.replace(var[0], "")

class SkinManager:
	folderDelimiter = "/" if os.name == "posix" else "\\" if os.name == "nt" else ""
	# preSkinDatas = ["{%static files/css%}"]
	def __init__(self, root, path):
		self.rootPath = root
		self.location = os.path.join(self.rootPath, path)
# 		print(self.location)
		self.fileList = []
		self.skinData = {}
		self.config = {}
		self.staticData = []

		for i in os.listdir(self.location):
			self.fileList.append(i)

		self.parseConfig()
		self.importLibraries()
		self.parseSkinData()
	
	def parseSkinData(self):
		pass
# 		print(len(self.skinData))
# 		print(self.skinData.keys())

	def parseConfig(self):
		if "config.json" not in self.fileList:
			raise NoSkinConfigException

		configRawData = self.readFile("config.json")
		self.config = json.loads(configRawData)
		self.code = self.config["code"]
		
		for i in self.config:
			if i in ["static files"]:
				for key, value in self.config[i].items():
					path = self.toAbsPath(value)
					for newPath, dirs, files in os.walk(path):
						relPath = self.toRelativePath(newPath)
						if relPath[0] == "/":
							relPath = relPath[1:]
						_staticData = {
							"key":key,
							"path":newPath,
							"relativePath":relPath,
							"files":files,
							"folders":dirs
						}
						self.staticData.append(_staticData)
				
			elif i == "skin":
				for name in self.config[i]:
					newPath = self.toAbsPath(self.config[i][name])
					_skinData = {
						"rootPath":self.location+"/html/",
						"path":newPath,
						"name":".".join(self.config[i][name].split(".")[:-1]),
						"file":self.readFile(self.config[i][name])
					}
					self.skinData[name] = _skinData
			for i,v in self.config["skin"].items():
				if i.isdigit():## 404, 501, etc...
					path = self.toAbsPath(v)
					self.staticData.append({
						"key":i,
						"path":path,
						"files":[v]
					})
	
	def runSkinCodes(self, datas, articles, target):
		for name in self.code[target]:
			func = getattr(self, name)
			func(datas, articles)
			
	def importLibraries(self):
		import types
		JBModule = types.ModuleType('JB', 'JB module for JB skins')
		setattr(JBModule, "preFunction", preFunction)
		setattr(JBModule, "postFunction", postFunction)
		setattr(JBModule, "replaceData", replaceData)
		# types.MethodType(preFunction, JBModule))
		# test_context_module.__dict__.update(context)
		sys.modules['JB'] = JBModule
		
		self.code["pre"], self.code["post"] = [], []
		self.code["any"] = []
		
		for i in self.code["files"]:
			path = os.path.join(self.location,self.code["path"],i)
			sfl = importlib.machinery.SourceFileLoader(i, path)
			d = sfl.load_module()
			dirD = dir(d)
			
			for funcName in [e for e in dirD if e[0:2] != "__"]:
				func = getattr(d, funcName)
				if hasattr(func, "__call__"):
					if hasattr(func, "skinCallOrder"):
						category = func.skinCallOrder
						name = func.__name__
						
					elif hasattr(func, "functionType"):
						category = func.functionType
						name = func.__name__
						
						if name == "replaceData":
							name = name+len(self.code[category])
					
					self.code[category].append(funcName)
					setattr(self, name, types.MethodType(func, self))

	def readFile(self, *path):
		with codecs.open(self.toAbsPath(*path), "r", "utf-8") as f:
			return f.read()

	def toAbsPath(self, *path):
		path = (self.location,)+path
		osPath = os.path.join(*path)
		return osPath.replace("/", self.folderDelimiter).replace("\\", self.folderDelimiter)
	
	def toRelativePath(self, path):
		return path.replace(self.location, "")
	
	def get(self, name):
		if name in self.skinData:
			return Skin(self.skinData[name])
		else:
			return None
		
	def compile(self, tagName, article):
		s = self.get(tagName)
		rendered = s.compile(article)

		return rendered
	
	def replaceData(self, datas, article):
		for name in self.code["replaceData"]:
			func = getattr(self, name)
			article = func(datas, article)
		
		return article
if __name__ == "__main__":
	s = Skin("/Users/hwangminuk/Documents/Ariyn JB WebSite/","skins/clean blog gh pages")
	
# 	for i in s.staticData:
# 		print(s.toAbsPath(i))
	s.replaceData("ss")