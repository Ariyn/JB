import os, sys, shutil
import codecs, unicodedata
import re
import json
import argparse
import subprocess
import datetime
import urllib.parse

from skin import Skin

oldPrint = print
print = (lambda *x:sys.stdout.buffer.write((str(x)+"\n").encode("utf-8")))

class NoPathException(Exception):
	pass
	
class Compiler:
	argParser = argparse.ArgumentParser(description="compile JB web sites")
	
	argParser.add_argument('path', metavar='path', type=str, help='full and absolute path to web site root directory')
	
	def __init__(self, root, mdSyntax = []):
		self.mdSyntax = mdSyntax

		# ("charset", "<meta charset=\"utf-8\">")
		self.metaLists = [
			("redirect",'<meta http-equiv="refresh" content="0; url={?:0}">\n<link rel="canonical" href="{?:0}" />'),
			("title", "<title>{?:0}</title>")
		]

		self.fileLists = {}
		self.args = self.argParser.parse_args()

		if not root: 
			if "path" in self.args:
				root = self.args.path
			else:
				# compiler will read it's own config file
				# and search previout path
				raise NoPathException
		
			
		self.root = root
		self.skin = Skin(self.root, "skins/clean blog gh pages")

		self.configParse()
		self.searchFolder()
		# self.searchHtmlFiles()

	def configParse(self):
		configPath = self.root+"/config.json"

		config = codecs.open(configPath, "r", "utf-8").read()
		config = json.loads(config)

		self.config = config

		self.build = config["path"]["build"]
		if self.build[-1] != "/":
			self.build += "/"

		self.isabs = os.path.isabs(config["path"]["build"])
		
		print(config)
		self.author = config["author"]
		self.options = config["options"]
		self.contents = config["path"]["contents"]
		self.resource = config["path"]["resource"]
		self.site = config["site"]
		self.defines = config["defines"]
		self.afterRunList = config["afterRun"]
		
		self.contentPath = os.path.join(self.root,self.contents)
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
	
	# TODO:
	# to run on lambda
	# this function should not run
	def searchFolder(self):
		self.contentPath = (self.contentPath).replace("\/", "/").replace("\\", "/")

		dirs = []

		for (path, dir, files) in os.walk(self.contentPath):
			path = path.replace("\/", "/").replace("\\", "/")

			if path[-1] != "/":
				path+="/"

			for i in dirs:
				path = path.replace(i[0], i[1])

			dir = [(i,unicodedata.normalize("NFC", i)) for i in dir]
			for i in dir:
				if i[0] != i[1]:
					dirs.append(i)


			relPath = "/".join(path.replace(self.contentPath, "").split("/")[:-1])
			if not relPath:
				relPath = "/"

			if relPath[-1] != "/":
				relPath += "/"

			if relPath not in self.fileLists:
				self.fileLists[relPath] = []

			for file in files:
				fullPath = path+file

				if self.isabs:
					# print(path, path.replace(self.root, ""))
					relFolder = path.replace(self.contentPath, "")
					if relFolder and relFolder[0] == "/":
						relFolder = relFolder[1:]

					# print(self.build+relFolder+file)
					if self.build[-1] != "/":
						self.build += "/"

					buildPath = os.path.join(self.build, relFolder, file)
					# print(buildPath, os.path.join(self.build,relFolder,file))
				else:
					buildPath = fullPath.replace(self.contents, self.build)

				ext = file.split(".")[-1]

				if ext.lower() in ["md"]:
					self.fileLists[relPath].append({
						"fild":file,
						"path":relPath+file,
						"fullPath":fullPath,
						"buildPath":buildPath,
						"ext":ext,
					})

	def compile(self, folder = None):
		self.skin.runSkinCodes({
			"buildPath":self.buildPath,
			"site":self.site,
			"author":self.author
		}, None, "pre")
		
		self.emptyDirectory()
		
		articles = []
		for i in self.fileLists:
			folders = self.fileLists[i]
			if i != "/":
				i += "/"
				
			for md in folders:
				article = self.compileContent(md)
				articles.append(article)
				f = article["content"]
				
				try:
					os.makedirs("/".join(md["buildPath"].split("/")[:-1]))
				except:
					pass
					
				article["path"] = unicodedata.normalize("NFC", article["path"])
				article["path"] = urllib.parse.quote(article["path"]).replace(md["ext"], "html")
				# print(article["path"].replace(md["ext"], "html"))
				codecs.open(md["buildPath"].replace(md["ext"], "html"), "w", "utf-8").write(f)
		
		self.skin.runSkinCodes({
			"buildPath":self.buildPath,
			"site":self.site,
			"author":self.author
		}, articles, "post")
		
		self.copyResource()
		self.afterRun()
	
	def emptyDirectory(self):
		self.buildPath
	def copyResource(self):
		resourcePath = os.path.join(self.root, self.resource)
		# print(resourcePath)
		for (path, dir, files) in os.walk(resourcePath):
			# print(path)
			for i in files:
				# print(i)
				originalPath = os.path.join(path, i)
				folder = path.replace(resourcePath, "")
				targetPath = os.path.join(self.root, self.build, self.resource, folder, i)
				try:
					os.makedirs( os.path.join(self.root, self.build, self.resource, folder))
				except Exception as e:
					print(e)
				shutil.copy(originalPath, targetPath)
		
		for i in self.skin.staticData:
			targetPath = os.path.join(self.root, self.build, "static", i)
			if not os.path.isdir(targetPath):
				os.makedirs(targetPath)
			
			for file in self.skin.staticData[i]["files"]:
				# originalPath = self.skin.realLocation(i, file)
				originalPath = self.skin.realLocation(self.skin.staticData[i]["path"], file)
				# print(originalPath)
				targetPath = os.path.join(self.root, self.build, "static", i, file)
				# print(originalPath, "to", targetPath)
				shutil.copy(originalPath, targetPath)

	def preCompile(self, article):
		article["meta"] = {}

		for i in self.defines:
			# print(i, self.defines[i])
			article["content"] = article["content"].replace("{{%s}}" % i, self.defines[i])
		
		pattern = r"(^---\n((?:[A-Za-z0-9\._\-]+\s*(?::\s*.+)?\n)*)^---\n)"
		repl = "infoParse"
		option = re.MULTILINE | re.DOTALL
			
		d = re.search(pattern, article["content"], flags = option)
		# print(pattern, article, d)
		if d:
			for i in [i for i in d.group(2).split("\n") if i]:
				metas = re.search(r"(.+?)\s*:\s*(.+)\s*", i)
				if metas:
					meta, value = metas.group(1), metas.group(2)
				else:
					metas = re.search(r"(.+)\s*", i)
					meta, value = metas.group(1), True
					
				string = ""
				for metaName, metaRep in self.metaLists:
					if metaName == meta:
						# print(meta, value)
						string = metaRep.replace("{?:0}", value)
						break

				article["meta"][meta] = (value, string)
			article["content"] = article["content"].replace(d.group(0), "")

		return article

	def compileContent(self, data):
		fileInfo = os.stat(data["fullPath"])
		article = {"content":codecs.open(data["fullPath"], "r", "UTF-8").read()+"\n\n"}
		# print("here", path.split("/")[-1], article["name"])
		article = self.preCompile(article)
		article["path"] = data["path"]
		article["birthDate"] = datetime.datetime.fromtimestamp(fileInfo.st_birthtime)
		article["birthDateStr"] = article["birthDate"].strftime("%Y-%m-%d")
		
		content = article["content"]
		for d in self.mdSyntax:
			option = None
			if len(d) == 3:
				pattern, repl, option = d
			elif len(d) == 2:
				pattern, repl = d

			if hasattr(self, repl):
				func = self.__getattribute__(repl)
				# print(func, type(func), dir(func))

				if not option:
					option = re.M
				search = re.findall(pattern, content, flags=option)
				# print(search)
				for find in search:
					d = func.__call__(find)
					# print("find", find)
					if d:
						# print("replace", find[0], d)
						content = content.replace(find[0], d, 1)
			else:
				content = re.sub(pattern, repl, content)
		
		article["name"] = ".".join(article["path"].split("/")[-1].split(".")[:-1])
		
		if "meta" in article:
			if "title" in article["meta"]:
				article["name"] = article["meta"]["title"][0]
		
			if "heading" in article["meta"]:
				article["heading"] = article["meta"]["heading"][0]
			else:
				article["heading"] = ""
			
			if "bgImage" in article["meta"]:
				article["bgImage"] = article["meta"]["bgImage"][0]
			else:
				article["bgImage"] = "/static/img/post-bg.jpg"
			
		skinData = self.skin.get("contents")
		# print(article)
		# print("\n".join([article["meta"][i][1] for i in article["meta"]]))
		# print(article["birthDate"])
		# if article["name"] == "JB":
			# print(fileInfo)
			# (os.stat_result(st_mode=33188, st_ino=13505834, st_dev=16777220, st_nlink=1, st_uid=501, st_gid=20, st_size=1137, st_atime=1482408015, st_mtime=1474744169, st_ctime=1474744169),)

		
		content = skinData.replace("{%contents%}", content)
		article["content"] = content
		article = self.skin.replaceData({
			"buildPath":self.buildPath,
			"site":self.site,
			"author":self.author
		}, article)

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
		# oldPrint(first, middle, last)
		# oldPrint(chr(first+0x1100), chr(middle+0x1161), chr(last+0x11A8-1) if last != 0 else "")
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