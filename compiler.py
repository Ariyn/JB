import os, sys, shutil
import codecs, unicodedata
import re
import json

class Compiler:
	def __init__(self, root, mdSyntax = []):
		self.mdSyntax = mdSyntax
		self.metaSyntax = [
			(r"(^---\n((?:[A-Za-z0-9\._\-]+:[ A-Za-z0-9\._\-]+\n)*)^---\n)", "infoParse", re.MULTILINE | re.DOTALL)
		]
		self.metaLists = [
			("redirect",'<meta http-equiv="refresh" content="0; url={?:0}">\n<link rel="canonical" href="{?:0}" />'),
			("title", "<title>{?:0}</title>")
		]

		self.fileLists = {}
		self.root = root

		self.configParse()
		self.searchFolder()
		self.searchHtmlFiles()

	def configParse(self):
		configPath = self.root+"/config.json"

		config = codecs.open(configPath, "r", "utf-8").read()
		config = json.loads(config)

		self.config = config

		self.build = config["path"]["build"]
		if self.build[-1] != "/":
			self.build += "/"

		self.isabs = os.path.isabs(config["path"]["build"])

		self.options = config["options"]
		self.contents = config["path"]["contents"]
		self.resource = config["path"]["resource"]
		self.name = config["name"]
		self.defines = config["defines"]
		self.html = config["html"]
		
		self.contentPath = os.path.join(self.root,self.contents)
		
	def searchHtmlFiles(self):
		for i in self.html:
			path = self.html[i]
			if path:
				self.html[i+" path"] = os.path.join(self.root,path)
				file = open(self.html[i+" path"], "r").read()
				self.html[i+" content"] = file

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


			relPath = "/".join(path.replace(self.contentPath, "/").split("/")[:-1])
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

					buildPath = os.path.join(self.build,relFolder,file)
					# print(buildPath, os.path.join(self.build,relFolder,file))
				else:
					buildPath = fullPath.replace(self.contents, self.build)

				ext = file.split(".")[-1]	

				if ext in ["md", "MD"]:
					self.fileLists[relPath].append({
						"fild":file,
						"path":relPath+file,
						"fullPath":fullPath,
						"buildPath":buildPath,
						"ext":ext,
					})

	def compile(self, folder = None):
		for i in self.fileLists:
			folders = self.fileLists[i]
			if i != "/":
				i += "/"

			for md in folders:
				article = self.compileContent(md["fullPath"])
				f = article["content"]
				try:
					os.makedirs("/".join(md["buildPath"].split("/")[:-1]))
				except:
					pass

				codecs.open(md["buildPath"].replace(md["ext"], "html"), "w", "utf-8").write(f)

		self.copyResource()

	def copyResource(self):
		resourcePath = os.path.join(self.root, self.resource)
		for (path, dir, files) in os.walk(resourcePath):
			# print(path)
			for i in files:
				originalPath = os.path.join(path, i)
				folder = path.replace(resourcePath, "")
				targetPath = os.path.join(self.build, self.resource, folder, i)
				try:
					os.makedirs( os.path.join(self.build, self.resource, folder))
				except:
					pass
				# print(originalPath, targetPath)
				shutil.copy(originalPath, targetPath)

	def preCompile(self, article):
		article["meta"] = {}

		for i in self.defines:
			print(i, self.defines[i])
			article["content"] = article["content"].replace("{{%s}}" % i, self.defines[i])

		for pattern, repl, option in self.metaSyntax:
			# print(content)
			d = re.search(pattern, article["content"], flags = option)
			if d:
				for i in [i for i in d.group(2).split("\n") if i]:
					metas = re.search(r"(.+?)\s*:\s*(.+)\s*", i)
					meta, value = metas.group(1), metas.group(2)

					for metaName, metaRep in self.metaLists:
						if metaName == meta:
							# print(meta, value)
							string = metaRep.replace("{?:0}", value)
							break

					article["meta"][meta] = (value, string)
				article["content"] = article["content"].replace(d.group(0), "")

		return article

	def compileContent(self, path):
		article = {"content":codecs.open(path, "r", "UTF-8").read()+"\n\n"}
		article = self.preCompile(article)
		
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

		content = "<head>"+"<meta charset=\"utf-8\">"+"\n".join([article["meta"][i][1] for i in article["meta"]])+"</head>\n<body>"+content+"\n</body>"

		article["content"] = content

		return article


if __name__ == "__main__":
	windowsPath = "C:/Users/ariyn/Documents/JB-Wiki"
	c = Compiler(windowsPath)
	c.copyResource()

