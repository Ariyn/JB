import os, sys
import codecs, unicodedata
import re
import json

class Compiler:
	def __init__(self, root, mdSyntax = []):
		self.mdSyntax = mdSyntax
		self.fileLists = {}
		self.root = root

		self.configParse()
		self.searchFolder()

	def configParse(self):
		configPath = self.root+"/config.json"

		config = codecs.open(configPath, "r", "utf-8").read()
		config = json.loads(config)

		self.config = config
		self.build = config["build"]
		self.options = config["options"]
		self.contents = config["contents"]
		self.name = config["name"]

	def searchFolder(self):
		rootPath = (self.root+"/%s/"%self.contents).replace("\/", "/").replace("\\", "/")
		dirs = []

		for (path, dir, files) in os.walk(rootPath):
			path = path.replace("\/", "/").replace("\\", "/")
			if path[-1] != "/":
				path+="/"

			for i in dirs:
				path = path.replace(i[0], i[1])

			dir = [(i,unicodedata.normalize("NFC", i)) for i in dir]

			for i in dir:
				if i[0] != i[1]:
					dirs.append(i)


			relPath = "/".join(path.replace(rootPath, "/").split("/")[:-1])
			if not relPath:
				relPath = "/"
			
			if relPath not in self.fileLists:
				self.fileLists[relPath] = []

			for file in files:
				fullPath = path+file
				ext = file.split(".")[-1]
				buildPath = fullPath.replace(self.contents, self.build)

				if ext in ["md", "MD"]:
					
					self.fileLists[relPath].append({
						"fild":file,
						"path":relPath+file,
						"fullPath":fullPath,
						"buildPath":buildPath,
						"ext":ext,
					})

	def parse(self, folder = None):
		if folder and folder in self.fileLists:
			folders = self.fileLists[folder]
			if folder != "/":
				folder += "/"

			for md in folders:
				# print(md["fullPath"])
				f = self.parseMD(md["fullPath"])

				try:
					os.makedirs("/".join(md["buildPath"].split("/")[:-1]))
				except:
					pass

				codecs.open(md["buildPath"].replace(md["ext"], "html"), "w", "utf-8").write(f)
		else:
			for i in self.fileLists:
				folders = self.fileLists[i]
				if i != "/":
					i += "/"

				for md in folders:
					# print(md["fullPath"])
					f = self.parseMD(md["fullPath"])

					try:
						os.makedirs("/".join(md["buildPath"].split("/")[:-1]))
					except:
						pass

					codecs.open(md["buildPath"].replace(md["ext"], "html"), "w", "utf-8").write(f)

	def parseMD(self, path):
		content = codecs.open(path, "r", "UTF-8").read()+"\n\n"
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

		content = "<head><meta charset=\"utf-8\"></head>\n<body>"+content+"\n</body>"
		return content

def test():
	pass

if __name__ == "__main__":
	windowsPath = "C:\\Users/ariyn/Documents/JB-Wiki"
	c = Compiler(windowsPath)

