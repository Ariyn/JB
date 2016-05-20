import os, sys
import codecs
import re
# import markdown

### inspired by https://gist.github.com/jbroadway/2836900
### MIT License

class markdown:
	# skip escaped bracket with backward lookahead
	# (\[.+?(?<!\\)\])
# <a href=\"#\1\">\1</a>
	mdSyntax = [
		(r"#{1,6} .+?\n((?:  )?[\*\+-] (.+?)(?=\n\n))", "uiList"),
		(r"\n{2,}([\*\+-] (.+?)(?=\n\n))", "uiList"),
		
		(r"\*\*(.+?)\*\*", r"<strong>\1</strong>"),
		(r"(---|___|\*\*\*)", r"<hr>\n"),
		(r"(\*|_)(.+?)(\*|_)", r"<em>\2</em>"),
		(r"~~(.+?)~~", r"<del>\1</del>"),
		(r"(\[(.+?)(?<!\\)\]\((.+?)\))", "anchor"),

		(r"((#{1,6}) (.+?\n))", r"header"),
		(r"(^(>+)(.+?)(?=\n\n))", "block"),

		(r"\n?((<(.+?)>)?(.+?)(<\/\3>)?\n)","pSign"),
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
					# print(f)

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
		return "<a href=\"%s\">%s</a>" % (find[2], find[1])

	def header(self, find):
		header = re.search(r"(?:<.+?>)?(.+?)(?:<\/.+?>)?\n", find[2]).groups()[0]
		count, nlCount = find[1].count("#"), find[2].count("\n")


		retVal = ("<h%d id=\"%s\"><a href=\"#%s\">%s</a></h%d>"% (count, header, header, find[2], count)).replace("\n", "")
		# print("header : ",header, "retVal : ", retVal)

		retVal = retVal+"".join(["\n"]*nlCount);
		return retVal

	def block(self, find, oriDepth = 1):
		# find = find[0]
		# newFind = re.findall("(>{%d}(.+))\s?"%oriDepth, find)
		# print(newFind)
		pass

if __name__ == "__main__":
	md = markdown()
	md.searchFolder("C:\/Users\/ariyn\/Documents\/JB-Wiki")