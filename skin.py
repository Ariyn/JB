import os
import json, codecs

class NoSkinConfigException(Exception):
	pass

class Skin:
	folderDelimiter = "/" if os.name == "posix" else "\\" if os.name == "nt" else ""
	# preSkinDatas = ["{%static files/css%}"]
	def __init__(self, root, path):
		self.root = root
		self.location = os.path.join(self.root, path)
		self.fileList = []
		self.skinData = {}
		self.config = {}
		self.staticData = {}

		for i in os.listdir(self.location):
			self.fileList.append(i)

		self.parseConfig()

		# print(self.config)
		# print(self.staticData)

	def parseConfig(self):
		if "config.json" not in self.fileList:
			raise NoSkinConfigException

		configRawData = self.readFile("config.json")
		self.config = json.loads(configRawData)

		for i in self.config:
			if i in ["static files"]:
				for name in self.config[i]:
					_staticData = {
						"path":self.realLocation(self.config[i][name]),
						"files":[]
					}
					# print(self.staticData[name])
					for file in os.listdir(_staticData["path"]):
						_staticData["files"].append(file)

					self.staticData[name] = _staticData

			elif i == "skin":
				for name in self.config[i]:
					newPath = self.realLocation(self.config[i][name])
					_skinData = {
						"path":newPath,
						"name":".".join(self.config[i][name].split(".")[:-1]),
						"file":self.readFile(self.config[i][name])
					}

					#############################################################################################
					_skinData["file"] = _skinData["file"].replace("{%static files/css%}",
					"/"+ self.config["static files"]["css"])
					# print(self.config["static files"]["css"])
					_skinData["file"] = _skinData["file"].replace("{%static files/image%}",
					"/"+ self.config["static files"]["image"])
					#############################################################################################

					self.skinData[name] = _skinData

	def readFile(self, *path):
		return codecs.open(self.realLocation(*path), "r", "utf-8").read()

	def realLocation(self, *path):
		path = (self.location,)+path
		osPath = os.path.join(*path)
		return osPath.replace("/", self.folderDelimiter).replace("\\", self.folderDelimiter)

	def get(self, name):
		if name in self.skinData:
			return self.skinData[name]["file"]
		else:
			return None

if __name__ == "__main__":
	s = Skin("skins/default")
	
	for i in s.staticData:
		print(s.realLocation(i))
