import os, sys
import codecs, unicodedata
import re
import json
# import markdown

### inspired by https://gist.github.com/jbroadway/2836900
### MIT License

# skip escaped bracket with backward lookahead
# (\[.+?(?<!\\)\])

# TODO

# dynamically class name and id
# to make css custom module possible

# image

# addon and code embeded template
	# recently updated

# ajax comment system

# iframe dynamic change
#	recently changed

# wiki parsing extension
# (r"(==(.+?)==)", r"header"),
# https://www.mediawiki.org/wiki/Help:Formatting/ko

class markdown:
	mdSyntax = [
		(r"#{1,6} .+?\n((?:  )?[\*\+-] (.+?)(?=\n\n))", "uiList"),
		(r"\n{2,}([\*\+-] (.+?)(?=\n\n))", "uiList"),
		
		(r"(?:\*\*|''')(.+?)(?:\*\*|''')", r"<strong>\1</strong>"),
		(r"(----|---|___|\*\*\*)", r"<hr>\n"),
		(r"(\*|_|'')(.+?)(\*|_|'')", r"<em>\2</em>"),
		(r"~~(.+?)~~", r"<del>\1</del>"),
		(r"(\[(.+?)(?<!\\)\]\((.+?)\))", "anchor"),

		(r"(^(#{1,6})(.+?\n))", r"header"),
		(r"(^(>+)(.+?)(?=\n\n))", "block"),

		(r"\n?((<(.+?)>)?(.+?)(<\/\3>)?\n)","pSign"),
	]
	
	def __init__(self, root):
		self.mdLists = {}
		self.root = root

		self.configParse()

	def configParse(self):
		configPath = self.root+"/config.json"

		print(configPath)
		config = codecs.open(configPath, "r", "utf-8").read()
		config = json.loads(config)

		self.config = config
		self.build = config["build"]
		self.options = config["options"]
		self.contents = config["contents"]
		self.name = config["name"]

	def searchFolder(self):
		rootPath = (self.root+"/%s/"%self.contents).replace("\/", "/").replace("\\", "/")
		# buildPath = (self.root+"/%s/"%self.build).replace("\/", "/").replace("\\", "/")
		# print(rootPath)
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


			relPath = path.replace(rootPath, "/")

			if relPath not in self.mdLists:
				self.mdLists[relPath] = []

			for file in files:
				fullPath = path+file
				ext = file.split(".")[-1]
				buildPath = fullPath.replace(self.contents, self.build)

				if ext in ["md", "MD"]:
					
					self.mdLists[relPath].append({
						"fild":file,
						"path":relPath+file,
						"fullPath":fullPath,
						"buildPath":buildPath,
						"ext":ext,
					})

	def parse(self):
		for i in self.mdLists:
			folders = self.mdLists[i]

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
		for (pattern, repl) in self.mdSyntax:
			if hasattr(self, repl):
				func = self.__getattribute__(repl)
				# print(func, type(func), dir(func))
				
				search = re.findall(pattern, content, flags=re.M|re.S)
				for find in search:
					d = func.__call__(find)

					if d:
						content = content.replace(find[0], d)
			else:
				content = re.sub(pattern, repl, content)

		content = "<head><meta charset=\"utf-8\"></head>\n<body>"+content+"\n</body>"
		return content

	def uiList(self, find, depth=0):
		# r"<li>\1\2</li>"
		find = find[0]
		newFind = re.findall("((\t*)[\*\+-] (.+))\s?", find)

		# print(find, newFind)

		skip = False
		newList, retVal = [], []

		for i, v in enumerate(newFind):
			length = v[1].count("\t")

			# print(v[0], length)
			if depth < length:
				# print("newList '"+v[0]+"'")
				newList.append(v[0])
				# ret = self.uiList([newList], depth+1)
				skip = True

			if skip and (i == len(newFind)-1 or v[1].count("\t") <= depth):
				newList = "\n".join(newList)
				ret = self.uiList([newList], depth+1)

				retVal.append("<ul>"+"\n".join(ret)+"</ul>")
				skip, newList = False, []

				if i == len(newFind)-1:
					continue

			if not skip:
				ori = v[0]
				ret ="<li>%s</li>"%v[2]

				retVal.append(ret)
		return "<ul>"+"\n".join(retVal)+"</ul>" if depth == 0 else retVal;

	def pSign(self, find):
		if find[2] in ["ul", "li", "ol", "h1", "h2", "h3", "h4", "h5", "h6" ,"hr"] or find[2].find("!--") == 0:
			return None

		match = re.match("\s+", find[0])
		if match:
			return find[0]

		retVal = "<p>%s</p>"%find[0]
		count = retVal.count("\n")

		retVal = retVal.replace("\n", "")+"".join(["\n"]*count);
		return retVal

	def anchor(self, find):
		# <a href="#chapter-3">Chapter 3</a>
		targetPath = find[2]

		if targetPath[0] == '$':
			# internal page link
			targetPath = targetPath[1:]
			# osx targetPath = "일기/1-1"

			path = "/%s/"%"/".join(targetPath.split("/")[:-1])
			# print(targetPath, path)
			# print(self.mdLists)

			if path in self.mdLists:

				for i in self.mdLists[path]:
					if i["path"] == "/%s"%targetPath+".md":
						print(self.options["hideExt"])
						targetPath = "./"+targetPath+(".html" if not self.options["hideExt"] else "")
						break
			
		elif targetPath.find('#') == 0:
			# html tag link
			pass
		else:
			# external link
			pass
		return "<a href=\"%s\">%s</a>" % (targetPath, find[1])

	def header(self, find):
		header = re.search(r"(?:<.+?>)? ?(.+?)(?:<\/.+?>)?\n", find[2]).groups()[0]
		count, nlCount = find[1].count("#"), find[2].count("\n")


		retVal = ("<h%d id=\"%s\"><a href=\"#%s\">%s</a></h%d>"% (count, header, "Table of Contents", find[2], count)).replace("\n", "")
		# print("header : ",header, "retVal : ", retVal)

		retVal = retVal+"".join(["\n"]*nlCount);
		return retVal

	def block(self, find, depth = 1):
		find = find[0]
		htmlList = []
		newFind = re.findall("((>*)(.+))\s?", find)
		# print(newFind)

		skip, newList = False, []
		newDepth = depth
		# TODO:
		# to much nested if and for loop

		for i, v in enumerate(newFind):
			
			# if v[2] == "sample":
			# 	print(v, newDepth, depth)
			if skip:
				newCount = v[1].count(">")

				if 0 != newCount < newDepth:
					# print("block newList", newList)
					d = self.block(["\n".join(newList)], newDepth)
					# print("d", d)
					htmlList.append(d)
					skip, newList, newDepth = False, [], depth
					newText = re.sub(">{%d}(.+)"%newDepth, r"\1", v[0])
					htmlList.append(newText)
				else:
					newList.append(v[0])
			elif depth < v[1].count(">"):
				# print("inside!")
				skip, newDepth = True, v[1].count(">")

				# print(newList)
				newList.append(v[0])
			else:
				newText = re.sub(">{%d}(.+)"%newDepth, r"\1", v[0])
				htmlList.append(newText)

		# print(htmlList)

		return "<blockquote><p>"+"<br />".join(htmlList)+"</p></blockquote>"

def i2h(int):
	return "".join("{:02x}".format(int))

def osxCombine(text):
	letters, i, position = [], 0, 0
	combine = (lambda x:chr(0xAC00+ x[0]*21*28 + x[1]*28 + x[2]))

	while i < len(text):
		v = text[i]
		index = ord(v) - 0x3131

		if 0 <= index <= 29:
			consonant, vowel = True, False
		elif 30 <= index <= 50:
			index-=30
			consonant, vowel = False, True
		else: # not korean
			consonant, vowel = False, False

		if len(letters) <= position:
			letters.append([None,None,None])
		
		l = letters[position]
		# print(index, vowel, consonant)
		# print(l)

		if vowel:
			l[1] = index
		elif consonant:
			if l[1]:
				l[2] = index+1
			else:
				l[0] = index
			

		# letters[position] = [v if v else 0 for ind,v in enumerate(l)]
		print(letters[position])
		i+=1

	# print(combine(letters[0]))

"""
osx 한글 인코딩
UTF-8을 쓰며 풀어서 적는다.

# 한글 자모
- ㄱ - ㅎ : U+3131 - U+314e
- ㅏ - ㅣ : U+314f - U+3163
"""

if __name__ == "__main__":
	windowsPath = "C:\\Users/ariyn/Documents/JB-Wiki"
	osxPath = "/Users/hwangminuk/Documents/JB-Wiki"

	md = markdown(osxPath)
	md.searchFolder()
	md.parse()
