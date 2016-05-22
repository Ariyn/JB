import json, codecs
import binascii
import sys

posts = {}
def hex_to_binary(h):
	return ''.join(byte_to_binary(ord(b)) for b in binascii.unhexlify(h))

if __name__ == "__main__":
	windowsPath = "C:\\Users/ariyn/Documents/JB-Wiki/mediawiki/"

	postNames = json.loads(codecs.open(windowsPath+"postNames.json", "r", "utf-8").read())
	
	revision = json.loads(codecs.open(windowsPath+"revision.json", "r", "utf-8").read())

	text = json.loads(codecs.open(windowsPath+"text.json", "r", "utf-8").read())

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
		for e in text:
			e["old_id"] = int(e["old_id"])
			if e["old_id"] == posts[i]["rev"]["rev_text_id"]:
				posts[i]["text"] = e

	# for i in posts[1]:

	post = posts[1]
	textData = post["text"]["old_text"]
	print(textData)
	sys.stdout.buffer.write(data)

	# for i in text:
	# 	print(i)

