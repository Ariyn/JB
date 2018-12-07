#!python3
import re
import codecs
import sys
import os
import argparse

from .compiler import Compiler

mdSyntax = [
		(r"(!(?!\[| +).+?) ", "escapeTag"),
		(r"(<<)", "&#60"),
		(r"(>>)", "&#62"),
		(r"(?:<pre>)(.+?)(?:<\/pre>)", "escape", re.M|re.S),

		(r"#{1,6}.+?\n((?:  )?[\*\+-] (.+?)(?=\n\n))", "uiList", re.M|re.S),
		(r"\n{1,}([\*\+-] (.+?)(?=\n\n))", "uiList", re.M|re.S),
		(r"(?:\*\*|''')(.+?)(?:\*\*|''')", r"<strong>\1</strong>"),
		(r"(----|---|___|\*\*\*)", r"<hr>\n"),
		(r"(\*|_|'')(.+?)(\*|_|'')", r"<em>\2</em>"),
		(r"~~(.+?)~~", r"<del>\1</del>"),
		(r"((!)?\[(.+?)(?<!\\)\]\((.+?)\))", "anchor"),
		(r"\[(.+?)\]", "localAnchor"),

		(r"(^(#{1,6})(.+?\n))", r"header"),
		(r"(^(>+)(.+?)(?=\n\n))", "block", re.M|re.S),

		(r"(?:\n\n)?((<(.+?)>)?(.+?)(<\/\3>)?(?:\n\n))","pSign", re.M|re.S),
		(r"((?:&#60code(.+?)(?:&#62))(.+?)(?:&#60\/code&#62))", "unescape", re.M|re.S),
		(r"\n\n\n", "<br>"),
	]

# original pSign regex
# (?:\n\n)?((<(.+?)>)?(.+?)(<\/\3>)?(?:\n\n))
class BlogParser(Compiler):
	def __init__(self, path, mdSyntax=mdSyntax):
		super().__init__(path)
		self.allowTags = ["ins", "u", "s", "del", "code", "tt", "blockquote", "!--", "pre", "br", "div", "ul", "li", "ol", "h1", "h2", "h3", "h4", "h5", "h6" ,"hr"]

		self.mdSyntax = mdSyntax
	
	def escapeTag(self, find):
		escapingHtmlTag = re.search("!(<\/?.+?>)(.*)", find)
		escapingMdCmd = re.search("!(\-+|\*+|~+|&+)(.*)", find)
		
		if escapingHtmlTag:
			tag = escapingHtmlTag.groups()
		if escapingMdCmd:
			tag = escapingMdCmd.groups()
	
		return self.escape("%s%s"%tag)
	def escapePre(self, find):
		return self.escape(find)
	def unescape(self, find):
		return "<code%s>%s</code>"%find[1:]

	def uiList(self, find, depth=0):
		find = find[0]
		newFind = re.findall("((\t*)[\*\+-] (.+))\s?", find)
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
		return "<ul>"+"".join(retVal)+"</ul>" if depth == 0 else retVal;

	def pSign(self, find):
		if find[1] in self.allowTags or find[1].find("!--") == 0:
			return None

		match = re.match("\s+", find[0])
		if match:
			return find[0]

		retVal = "<p>%s</p>"%find[0]
		count = retVal.count("\n")

		newLines = list(set(re.findall("(\n+ *\t*)$", retVal)))
		newLines = sorted(newLines, key=lambda x:len(x))
		for i in newLines:
			retVal = retVal.replace(i, "\n")
		retVal = re.sub("(\n+)", "<br />", retVal)+"\n"
# 		retVal = retVal.replace("\n", "<br>")+"".join("\n");
		return retVal

	def anchor(self, find):
		targetPath = find[3]
		retVal = ""
		if find[1] == "!":
			# original : ![image explain](url)
			url = os.path.join("/", self.config["site"]["prefix"]+"/", find[3])
			retVal = "<img src=\"%s\" alt=\"%s\">" % (url, find[2])
			# changed : ![image url](explain)
		else:
			
			if targetPath[0] == '$':
				targetPath = targetPath[1:]
				filePath = os.path.join(self.absContentPath, targetPath+".md")
				folderPath = os.path.join(self.absContentPath, targetPath+"/")
# "/JB-build/"
				if targetPath+".md" in self.fileLists:
					targetPath = os.path.join("/", self.config["site"]["prefix"]+"/", targetPath+".html")
				elif targetPath+"/index.md" in self.fileLists:
					targetPath = os.path.join("/", self.config["site"]["prefix"], targetPath, "index.html")
					print(targetPath)
				else:
# 					print(self.config["site"]["prefix"])
					targetPath = os.path.join("/", self.config["site"]["prefix"]+"/","404.html")
			elif targetPath.find('#') == 0:
				# html tag link
				pass
			elif targetPath.find('@') == 0:
				targetPath = "javascript:history.back(%s)"%(targetPath[1:])
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
		find = find[0]
		htmlList = []
		newFind = re.findall("((>*)(.+))\s?", find)

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
	argParser = argparse.ArgumentParser(description="compile JB web sites")
	argParser.add_argument('path', metavar='path', type=str, help='full and absolute path to web site root directory')
	
	args = argParser.parse_args()
	bp = BlogParser(args.path, mdSyntax)
	bp.compile()
