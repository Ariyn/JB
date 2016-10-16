
from compiler import Compiler
import re
import codecs
import sys

class BlogParser(Compiler):
	def __init__(self, path):
		super().__init__(path)

		self.allowTags = ["ins", "u", "s", "del", "code", "tt", "blockquote", "!--", "pre", "br", "div"]

		self.mdSyntax = [
			(r"#{1,6}.+?\n((?:  )?[\*\+-] (.+?)(?=\n\n))", "uiList", re.M|re.S),
			(r"\n{2,}([\*\+-] (.+?)(?=\n\n))", "uiList", re.M|re.S),
			(r"(?:\*\*|''')(.+?)(?:\*\*|''')", r"<strong>\1</strong>"),
			(r"(----|---|___|\*\*\*)", r"<hr>\n"),
			(r"(\*|_|'')(.+?)(\*|_|'')", r"<em>\2</em>"),
			(r"~~(.+?)~~", r"<del>\1</del>"),
			(r"((!)?\[(.+?)(?<!\\)\]\((.+?)\))", "anchor"),
			(r"\[(.+?)\]", "localAnchor"),

			(r"(^(#{1,6})(.+?\n))", r"header"),
			(r"(^(>+)(.+?)(?=\n\n))", "block", re.M|re.S),

			(r"(?:\n\n)?((<(.+?)>)?(.+?)(<\/\3>)?(?:\n\n))","pSign", re.S|re.M),
			(r"\n\n\n", "<br>")
		]
	
	def uiList(self, find, depth=0):
		# r"<li>\1\2</li>"
		find = find[0]
		# print(find)
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

		# print(repr(retVal))
		retVal = retVal.replace("\n\n", "\n").replace("\n", "<br> ")+"".join(["\n"]*count);
		return retVal

	def anchor(self, find):
		# <a href="#chapter-3">Chapter 3</a>
		targetPath = find[3]
		retVal = ""
		# print(find)
		# print("anchor", targetPath)
		if find[1] == "!":
			# print(find)
			# original : ![image explain](url)
			retVal = "<img src=\"%s\" alt=\"%s\">" % (find[3], find[2])
			# changed : ![image url](explain)
			# retVal = "<img src=\"%s\" alt=\"%s\">" % (find[2], find[3])
		else:
			if targetPath[0] == '$':
				targetPath = targetPath[1:]
				path = "/%s/"%"/".join(targetPath.split("/")[:-1])

				if path in self.fileLists:
					for i in self.fileLists[path]:
						if i["path"] == "/%s"%targetPath+".md":
							targetPath = "./"+targetPath+(".html" if not self.options["hideExt"] else "")
							# print(targetPath)
							break
				
			elif targetPath.find('#') == 0:
				# html tag link
				pass
			else:
				# external link
				pass

			# print(targetPath)
			retVal = "<a href=\"%s\">%s</a>" % (targetPath, find[2])
		return retVal
		
	def localAnchor(self, find):
		return ""
		# find

	def header(self, find):
		header = re.search(r"(?:<.+?>)? ?(.+?)(?:<\/.+?>)?\n", find[2]).groups()[0]
		count, nlCount = find[1].count("#"), find[2].count("\n")


		retVal = ("<h%d id=\"%s\"><a href=\"#%s\">%s</a></h%d>"% (count, header, "Table of Contents", find[2], count)).replace("\n", "")
		retVal = ("<h%d id=\"%s\">%s</h%d>"% (count, header, find[2], count)).replace("\n", "")
		# print("header : ",header, "retVal : ", retVal)

		retVal = retVal+"".join(["\n"]*nlCount);
		return retVal

	def block(self, find, depth = 1):
		print(find)
		find = find[0]
		htmlList = []
		newFind = re.findall("((>*)(.+))\s?", find)
		print(newFind)

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

if __name__ == "__main__":
	windowsPath = "C:/Users/ariyn/Documents/JB-Wiki"
	osxPath = "/Users/hwangminuk/Documents/JB-Wiki"
	
	
	if 2 <= len(sys.argv):
		path = sys.argv[-1]
	else:
		path = osxPath
	
	bp = BlogParser(path)
	bp.compile()
