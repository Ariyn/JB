import json, codecs
import binascii
import sys, os
from xml.etree.ElementTree import parse

posts = {}
def hex_to_binary(h):
	return ''.join(byte_to_binary(ord(b)) for b in binascii.unhexlify(h))

if __name__ == "__main__":
	windowsPath = "C:\\Users/ariyn/Documents/JB-Wiki/mediawiki/"
	osxPath = "/Users/hwangminuk/Documents/JB-Wiki/mediawiki/"

	postNames = json.loads(codecs.open(osxPath+"postNames.json", "r", "utf-8").read())
	
	revision = json.loads(codecs.open(osxPath+"revision.json", "r", "utf-8").read())

	# text = json.loads(codecs.open(osxPath+"text.json", "r", "utf-8").read())
	text = parse(osxPath+"text.xml").getroot()

	for i in postNames:
		posts[i["id"]] = {
			"title":i["title"]
		}

	for i in revision:
		i["rev_page"] = int(i["rev_page"])
		i["rev_text_id"] = int(i["rev_text_id"])
		revPage = i["rev_page"]

		if revPage in posts:
			if ("rev" in posts[revPage] and posts[revPage]["rev"]["rev_text_id"] < int(i["rev_text_id"])) or "rev" not in posts[revPage]:
				posts[revPage]["rev"] = i

	for i in posts:
		for row in text.findall("row"):
			e = {}
			for j in row.getchildren():
				e[j.get("name")] = j.text

			e["old_id"] = int(e["old_id"])
			if e["old_id"] == posts[i]["rev"]["rev_text_id"]:
				posts[i]["text"] = e

	for i in posts:
		post = posts[i]
	# post = posts[1]
		textData = post["text"]["old_text"]
		print(post["title"])
		# sys.stdout.buffer.write(d)
		path = osxPath+"backups/"+post["title"]+".md"

		try:
			os.makedirs("/".join(path.split("/")[:-1]))
		except:
			pass
			
		file = open(path, "w")
		file.write(textData)

	# for i in text:
	# 	print(i)

