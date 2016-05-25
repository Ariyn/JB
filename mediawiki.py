# media wiki parser
from compiler import Compiler
import re
import codecs

# change compiler to parser
# and compiler get parser as variable
class mw(Compiler):
	def __init__(self, path):
		super().__init__(path)

		self.mdSyntax = [
			(r"((?:(\*+) *(?:.+)\n?)+)", "ulList"),
			(r"((?:(#+) *(?:.+)\n?)+)", "olList"),

			(r"(?:''')(.+?)(?:''')", r"<strong>\1</strong>"),
			(r"(----)", r"<hr>\n"),
			(r"('')(.+?)('')", r"<em>\2</em>"),
			(r"(?:~~|<strike>)(.+?)(?:~~|</strike>)", r"<del>\1</del>"),

			(r"(^(={1,6}) *(.+?) *(={1,6}))", "title"),

			# (r"\n?((<(.+?)>)?(.+?)(<\/\3>)?\n)","pSign"),
		]

	def first(self, data):
		return 

	def ulList(self, find):
		return self.list(find, type="ul", char="*")

	def olList(self, find):
		d = self.list(find, type="ol", char="#")
		return d

	def list(self, find, type="ul", char="*"):
		print(find)
		newFind = re.findall("((\%s+) ?(.+?)\n)"%char, find[0], re.M)
		
		retVal,level = [], 0

		for i, v in enumerate(newFind):
			length = v[1].count(char)
			v = "<li>%s</li>"%v[0][length:].replace("\r","").replace("\n", "")

			if level < length:
				v = "<{?:0}><li>"*(length-level)+v[4:]
			elif length < level:
				v = "</{?:0}>"+"</li></{?:0}>"*(level-length-1)+v

			level = length
			retVal.append(v)

		retVal = "\n".join(retVal)+"</{?:0}>"+"</li></{?:0}>"*(level-1)
		retVal = retVal.replace("{?:0}", type)

		return retVal

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
			# print(self.fileLists)

			if path in self.fileLists:

				for i in self.fileLists[path]:
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

	def title(self, find):
		print(find)
		return "<h%d>%s</h%d>"%(find[1].count("="), find[2], find[1].count("="))

if __name__ == "__main__":
	windowsPath = "C:\\Users/ariyn/Documents/JB-Wiki"
	osxPath = "/Users/hwangminuk/Documents/JB-Wiki"

	md = mw(windowsPath)
	md.parse("/test")
