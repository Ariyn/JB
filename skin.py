import os, sys
import json, codecs
import copy
import importlib.machinery

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

class Skin:
	folderDelimiter = "/" if os.name == "posix" else "\\" if os.name == "nt" else ""
	# preSkinDatas = ["{%static files/css%}"]
	def __init__(self, root, path):
		self.root = root
		self.location = os.path.join(self.root, path)
		self.fileList = []
		self.skinData = {}
		self.config = {}
		self.staticData = {}

		for i in os.listdir(self.location):
			self.fileList.append(i)

		self.parseConfig()
		self.importLibraries()

		# print(self.config)
		# print(self.staticData)

	def parseConfig(self):
		if "config.json" not in self.fileList:
			raise NoSkinConfigException

		configRawData = self.readFile("config.json")
		self.config = json.loads(configRawData)
		self.code = self.config["code"]
		
		for i in self.config:
			if i in ["static files"]:
				for name in self.config[i]:
					_staticData = {
						"path":self.realLocation(self.config[i][name]),
						"files":[]
					}
					# print(_staticData)
					for file in os.listdir(_staticData["path"]):
						_staticData["files"].append(file)

					self.staticData[name] = _staticData
				
			elif i == "skin":
				for name in self.config[i]:
					newPath = self.realLocation(self.config[i][name])
					_skinData = {
						"path":newPath,
						"name":".".join(self.config[i][name].split(".")[:-1]),
						"file":self.readFile(self.config[i][name])
					}

					#############################################################################################
					# _skinData["file"] = _skinData["file"].replace("{%static files/css%}",
					# "/"+ self.config["static files"]["css"])
					# # print(self.config["static files"]["css"])
					# _skinData["file"] = _skinData["file"].replace("{%static files/image%}",
					# "/"+ self.config["static files"]["image"])
					#############################################################################################

					self.skinData[name] = _skinData
		# print(self.staticData)
	
	def runSkinCodes(self, datas, articles, target):
		# if type == "pre":		
		for name in self.code[target]:
			func = getattr(self, name)
			# print(func)
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
		return codecs.open(self.realLocation(*path), "r", "utf-8").read()

	def realLocation(self, *path):
		path = (self.location,)+path
		osPath = os.path.join(*path)
		return osPath.replace("/", self.folderDelimiter).replace("\\", self.folderDelimiter)

	def get(self, name):
		if name in self.skinData:
			return copy.copy(self.skinData[name]["file"])
		else:
			return None
			
	def replaceData(self, datas, article):
		for name in self.code["replaceData"]:
			func = getattr(self, name)
			article = func(datas, article)
		
		return article

if __name__ == "__main__":
	s = Skin("/Users/hwangminuk/Documents/Ariyn JB WebSite/","skins/clean blog gh pages")
	
	for i in s.staticData:
		print(s.realLocation(i))
	s.replaceData("ss")