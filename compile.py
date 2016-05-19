import os, sys
import codecs
import re
# import markdown

### inspired by https://gist.github.com/jbroadway/2836900
### MIT License

class markdown:
	mdSyntax = [
		(r"\*\*(.+?)\*\*", r"<strong>\1</strong>"),
		(r"(---|___|\*\*\*)", r"<hr>\n"),
		(r"(\*|_)(.+?)(\*|_)", r"<em>\2</em>"),
		(r"~~(.+?)~~", r"<del>\1</del>"),
		(r"\n{2,}([\*\+-] (.+?)(?=\n\n))", "uiList"),
		(r"((<(.+?)>)?.+(<\/\3>)?)",r"<p>\1</p>")
	]
	
	def __init__(self):
		# print(dir(self))
		pass

	def searchFolder(self, path):
		for (path, dir, files) in os.walk(path):
			for file in files:
				fullPath = path+"/"+file
				ext = file.split(".")[-1]

				if ext in ["md", "MD"]:
					print(fullPath)
					f = self.parseMD(fullPath)
					print(f)

	def parseMD(self, path):
		content = codecs.open(path, "r", "UTF-8").read()
		for (pattern, repl) in self.mdSyntax:
			if hasattr(self, repl):

				func = self.__getattribute__(repl)
				# print(func, type(func), dir(func))
				search = re.findall(pattern, content, flags=re.M|re.S)
				for find in search:
					d = func.__call__(find)
					content = content.replace(find[0], d)
			else:
				content = re.sub(pattern, repl, content)

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


if __name__ == "__main__":
	md = markdown()
	md.searchFolder("C:\/Users\/ariyn\/Documents\/JB-Wiki")
