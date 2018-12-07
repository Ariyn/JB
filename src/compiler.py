import os, sys, shutil
import codecs, unicodedata
import re
import json
import argparse
import subprocess
import datetime
import urllib.parse

from .nestedDict import nested_set
from .escapeList import escapeList
from .skin import SkinManager
from .tools import traversal

# oldPrint = print
# print = (lambda *x:sys.stdout.buffer.write((str(x)+"\n").encode("utf-8")))

union = lambda a,b:list(set(traversal(a).keys())&set(traversal(b).keys()))

class NoPathException(Exception):
	pass
	
class Compiler:	
	def __init__(self, root, mdSyntax = [], isLambda=False):
		self.mdSyntax = mdSyntax

		self.metaLists = [
			("redirect",'<meta http-equiv="refresh" content="0; url={?:0}">\n<link rel="canonical" href="{?:0}" />'),
			("title", "<title>{?:0}</title>")
		]

		self.folders = {}
		self.root = root

		self.configParse()
		self.skin = SkinManager(self.root, self.config["path"]["skin"])
		if not isLambda:
			self.searchFolder()

	def configParse(self):
		configPath = os.path.join(self.root, "config.json")

		with codecs.open(configPath, "r", "utf-8") as f:
			config = json.loads(f.read())
		self.config = config

		self.build = config["path"]["build"]
# 		print(self.build)
# 		if self.build[-1] != "/":
# 			self.build += "/"
# 		print(self.build)

		self.isabs = os.path.isabs(config["path"]["build"])
		
		self.author = config["site"]["author"]
		self.contentsPath = config["path"]["contents"]
		self.resourcePath = config["path"]["resource"]
		self.domainName = config["site"]["domainName"]
		self.name = config["site"]["name"]
		self.description = config["site"]["description"]
		prefix = self.config["site"]["prefix"]
		if prefix and prefix[0] != "/":
			self.config["site"]["prefix"] = "/"+prefix
		
		self.absContentPath = os.path.join(self.root,self.contentsPath)
		if not self.isabs:
			self.buildPath = os.path.join(self.root,self.build)
		else:
			self.buildPath = self.build
		
	def searchHtmlFiles(self):
		for i in self.html:
			path = self.html[i]
			if path:
				self.html[i+" path"] = os.path.join(self.root,path)
				file = open(self.html[i+" path"], "r").read()
				self.html[i+" content"] = file

	def searchFolder(self):
		self.fileLists = []
		self.absContentPath = (self.absContentPath).replace("\/", "/").replace("\\", "/")
		dirs = []

		for (path, dir, files) in os.walk(self.absContentPath):
			path = path.replace("\/", "/").replace("\\", "/")

			if path[-1] != "/":
				path+="/"

			for i in dirs:
				path = path.replace(i[0], i[1])

			dir = [(i,unicodedata.normalize("NFC", i)) for i in dir]
			for i in dir:
				if i[0] != i[1]:
					dirs.append(i)


			relPath = "/".join(path.replace(self.absContentPath, "").split("/")[:-1])
			if not relPath:
				relPath = "/"

			if relPath[-1] != "/":
				relPath += "/"

			if relPath not in self.folders:
				self.folders[relPath] = []

			for file in files:
				fullPath = path+file

				if self.isabs:
					# print(path, path.replace(self.root, ""))
					relFolder = path.replace(self.absContentPath, "")
					if relFolder and relFolder[0] == "/":
						relFolder = relFolder[1:]

					buildPath = os.path.join(self.build, relFolder, file)
					# print(buildPath, os.path.join(self.build,relFolder,file))
				else:
					buildPath = fullPath.replace(self.contentsPath, self.build)

				ext = file.split(".")[-1]
				fileName = ".".join(file.split(".")[:-1])

				if ext.lower() in ["md"]:
					with codecs.open(fullPath, "r", "UTF-8") as f:
						contentString = f.read()
					fInfo = os.stat(fullPath)
					self.folders[relPath].append({
						"fileName":fileName,
						"path":relPath+file,
						"fullPath":fullPath,
						"buildPath":buildPath,
						"ext":ext,
						"fileInfo":{
							"createTime":fInfo.st_ctime
						},
						"contentString":contentString
					})
					self.fileLists.append((relPath if relPath[0]!="/" else relPath[1:])+file)
					
	def createFolderStructure(self):
		for i, folder in self.folders.items():
			for md in folder:
				d = "/".join(md["buildPath"].split("/")[:-1])
				if not os.path.exists(d):
						os.makedirs(d)
						
	def escape(self, target):
		for key, value in escapeList.items():
			target = target.replace(key, value)
		return target
		
	def compile(self, folder = None):
		self.skin.runSkinCodes({
			"buildPath":self.buildPath,
			"site":self.domainName,
			"author":self.author
		}, None, "pre")
		
		self.emptyDirectory()
		self.createFolderStructure()
		
		articles = []
		for i in self.folders:
			folders = self.folders[i]
			if i != "/":
				i += "/"

			for md in folders:
				article = self._compile(md)
				articles.append(article)
				with codecs.open(md["buildPath"].replace(md["ext"], "html"), "w", "utf-8") as file:
					file.write(article["compiled"])
				
		self.skin.runSkinCodes({
			"buildPath":self.buildPath,
			"site":self.domainName,
			"author":self.author
		}, articles, "post")
		
		self.copyResource()

	def _compile(self, markdown):
		article = self.compileContent(markdown)

		article["path"] = unicodedata.normalize("NFC", article["path"])
		article["path"] = urllib.parse.quote(article["path"]).replace(markdown["ext"], "html")
		return article
	def emptyDirectory(self):
		for f in os.listdir(self.buildPath):
			path = os.path.join(self.buildPath, f)
			if os.path.isdir(path):
# 				print("deleting", path)
				shutil.rmtree(path)
			else:
				os.remove(path)
		
	def copyResource(self):
		resourcePath = os.path.join(self.root, self.resourcePath,"")
		
		for (path, dir, files) in os.walk(resourcePath):
			for i in files:
				originalPath = os.path.join(path, i)
				folder = path.replace(resourcePath, "")
				targetPath = os.path.join(self.root, self.build, self.resourcePath, folder)
				try:
					os.makedirs(targetPath)
				except Exception as e:
					print("exception", e)
					print(targetPath, self.root, self.build, self.resourcePath, folder)
				shutil.copy(originalPath, os.path.join(targetPath, i))
# 				print(targetPath)
		
		for i in self.skin.staticData:
			targetPath = os.path.join(self.root, self.build, i["relativePath"])
			
			if not os.path.isdir(targetPath):
				os.makedirs(targetPath)
			for f in [os.path.join(targetPath, folder) for folder in i["folders"]]:
				if not os.path.exists(f):
					os.mkdir(f)

			for file in i["files"]:
				shutil.copy(os.path.join(i["path"], file), os.path.join(targetPath, file))

	def preCompile(self, article):
		article["meta"] = {"redirect":(None, "")}
		pattern = r"(^---\n((?:[A-Za-z0-9\._\-]+\s*(?::\s*.+?(?!---))?\n)*)^---\n)"
		repl = "infoParse"
		option = re.MULTILINE | re.DOTALL
			
		d = re.search(pattern, article["content"], flags = option)
		if d:
			for i in [i for i in d.group(2).split("\n") if i]:
				metas = re.search(r"(.+?)\s*:\s*(.+)\s*", i)
				if metas:
					meta, value = metas.group(1), metas.group(2)
				else:
					metas = re.search(r"(.+)\s*", i)
					meta, value = metas.group(1), True
				
				if meta == "title":
					article["post"]["title"] = value
				string = ""
				for metaName, metaRep in self.metaLists:
					if metaName == meta:
						string = metaRep.replace("{?:0}", value)
						break
				article["meta"][meta] = (value, string)
			article["content"] = article["content"].replace(d.group(0), "")
		else:
			article["meta"]["title"] = (article["fileName"], "title")
# 			print(article["content"])

		return article

	def compileContent(self, data):
		fileInfo = data["fileInfo"]
		contentString = data["contentString"]
		
		article = {
			"content":contentString+"\n\n",
			"site":{
				"tagline":"",
				"author":{
					"nickname":"",
					"name":"",
					"email":""
				},
				"domainName":"",
				"name":"",
				"description":"",
				"related_posts":[],
				"prefix":self.config["site"]["prefix"]
			},
			"post":{
				"date":datetime.datetime.now(),
				"title":"",
				"hasCode":False
			},
			"fileName":data["fileName"],
			"meta":{
				"redirect":""
			}
		}
		tConfig = traversal(self.config)
		commonConfig = union(article, self.config)
		for configName in commonConfig:
			nested_set(article, configName.split("."), tConfig[configName])
		
		article = self.preCompile(article)
		article["path"] = data["path"]
		article["post"]["date"] = datetime.datetime.fromtimestamp(fileInfo["createTime"]).strftime("%Y/%m/%d")
		
		content = article["content"]
		for d in self.mdSyntax:
			option = None
			if len(d) == 3:
				pattern, repl, option = d
			elif len(d) == 2:
				pattern, repl = d
			if hasattr(self, repl):
				func = self.__getattribute__(repl)
# 				print(func, type(func), dir(func))

				if not option:
					option = re.M
				search = re.findall(pattern, content, flags=option)
				for find in search:
					d = func.__call__(find)
					if d:
						if type(find) == tuple:
							target = find[0]
						elif type(find) == str:
							target = find
						content = content.replace(target, d, 1)
			else:
				content = re.sub(pattern, repl, content)
		
		article["content"] = content
		article["name"] = ".".join(article["path"].split("/")[-1].split(".")[:-1])
		
		if "meta" in article:
			if "title" in article["meta"]:
				article["post"]["title"] = article["meta"]["title"][0]
			if "redirect" in article["meta"]:
				article["meta"]["redirect"] = article["meta"]["redirect"][1]
			if "heading" in article["meta"]:
				article["heading"] = article["meta"]["heading"][0]
			else:
				article["heading"] = ""
			
			if "bgImage" in article["meta"]:
				article["bgImage"] = article["meta"]["bgImage"][0]
			else:
				article["bgImage"] = "/static/img/post-bg.jpg"
		
		if "<code" in article["content"]:
			article["post"]["hasCode"] = True
		
		article["compiled"] = self.skin.compile("article", article)

		return article
	
	def afterRun(self):
		for i in self.afterRunList:
			newPath = os.path.join(self.root,i)
			if not os.path.isfile(newPath):
				newPath = i
				
			process = subprocess.Popen(newPath, stdout=sys.stdout, stderr=sys.stderr, shell=True)
			process.wait()
			# stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			# stdout=sys.stdout, stderr=sys.stderr)
	
	@staticmethod
	def encodeUtfUri(text):
		koreans = [Compiler.breakeKoreanUtf8(i) if 0xAC00 <= ord(i) <= 0xD7A3 else i for i in text]
		oldPrint(koreans)
		oldPrint(urllib.parse.quote("".join(koreans)))
	
	@staticmethod
	def breakeKoreanUtf8(t):
		d = ord(t) - 0xAc00
		first = d//21//28
		middle = (d%(21*28))//28
		last = d%28

		return "".join([chr(first+0x1100), chr(middle+0x1161), chr(last+0x11A8-1) if last != 0 else ""])
if __name__ == "__main__":
	# just for test
	# windowsPath = "C:/Users/ariyn/Documents/JB/sample"
	# c = Compiler(windowsPath)
	# c.copyResource()
	# c.compile()
	# for i in range(0, 256):
	# 	oldPrint("%x"%(0x1100+i), chr(0x1100+i))
	Compiler.encodeUtfUri("생각")
	print(hex(3131))
	print(0xe1848b)
	# %E1%84%89 %E1%85%A6 %E1%84%8B %E1%85%AF %E1%86%AF
	# %E1%84%89 %E1%85%A6 %E1%84%8B %E1%85%AF %E1%86%AF
	# %E1%84%89 %E1%85%A2 %E1%86%BC %E1%84%80 %E1%85%A1 %E1%86%A8
	# %E1%84%89 %E1%85%A2 %E1%86%BC %E1%84%80 %E1%85%A1 %E1%86%A8
	# %E1%84%89 %E1%85%A6 %E1%84%8B %E1%85%AF%E1%86%AF
	# (9, 5, 0)
	# (11, 14, 8)