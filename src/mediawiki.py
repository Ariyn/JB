# media wiki parser
from compiler import Compiler
import re
import codecs

# change compiler to parser
# and compiler get parser as variable
class mw(Compiler):
	def __init__(self, path):
		super().__init__(path)

		self.allowTags = ["ins", "u", "s", "del", "code", "tt", "blockquote", "!--", "pre", "br"]

		self.mdSyntax = [
			(r"(<(/?)(.+?)>)", "escapeTag", re.M|re.S),
			# (r"\t", "&nbsp;&nbsp;&nbsp;&nbsp;"),
			(r"((?:(\*+) *(?:.+)\n?)+)", "ulList"),
			(r"((?:(#+) *(?:.+)\n?)+)", "olList"),
			# (r"((?:(;|:)+ *(?:.+)\n?)+)", "defList"),

			(r"(?:''')(.+?)(?:''')", r"<strong>\1</strong>"),
			(r"(----)", r"<hr>\n"),
			(r"('')(.+?)('')", r"<em>\2</em>"),
			(r"(?:~~|<strike>)(.+?)(?:~~|</strike>)", r"<del>\1</del>"),

			(r"(^(={1,6}) *(.+?) *(={1,6}))", "title"),

			(r"(?:<nowiki>)(.+?)(?:</<nowiki>>)", r"<pre>\1</pre>"),

			(r"\n?((<(.+?)>)?(.+?)(<\/\3>)?\n)","pSign"),
		]

	def first(self, data):
		return 

	def ulList(self, find):
		newFind = re.findall("((\*+) ?(.+?)\n)", find[0], re.M)
		newFind = [v+(v[1].count("*"),) for v in newFind]

		return self.list(newFind, type="ul")

	def olList(self, find):
		newFind = re.findall("((\#+) ?(.+?)\n)", find[0], re.M)
		newFind = [v+(v[1].count("#"),) for v in newFind]
		d = self.list(newFind, type="ol")
		return d

	def list(self, find, type="ul", item="li"):
		retVal,level = [], 0

		for i, v in enumerate(find):
			length = v[-1]
			# .count(char)
			v = "<{?:1}>%s</{?:1}>"%v[0][length:].replace("\r","").replace("\n", "")
			if level < length:
				v = "<{?:0}><{?:1}>"*(length-level)+v[7:]
				# print("lev<len", v)
			elif length < level:
				v = "</{?:0}>"+"</{?:1}></{?:0}>"*(level-length-1)+v

			level = length
			retVal.append(v)

		retVal = "\n".join(retVal)+"</{?:0}>"+"</{?:1}></{?:0}>"*(level-1)
		# print(retVal)
		retVal = retVal.replace("{?:0}", type).replace("{?:1}", item)

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
# 						print(self.options["hideExt"])
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

	def title(self, find):
		return "<h%d>%s</h%d>"%(find[1].count("="), find[2], find[1].count("="))

	def escapeTag(self, find):
		allowed = False

		retVal = find[0]
		for e in self.allowTags:
			if find[2].split(" ")[0] == e:
				allowed = True
				break

		if not allowed:
			retVal = retVal.replace("<", "&lt;").replace(">","&gt;")

		return retVal


if __name__ == "__main__":
	windowsPath = "C:\\Users/ariyn/Documents/JB-Wiki"
	osxPath = "/Users/hwangminuk/Documents/JB-Wiki"

	md = mw(windowsPath)
	md.parse("/test")
