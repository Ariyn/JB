import unittest
import os

from datetime import datetime

from mako.template import Template
from mako.lookup import TemplateLookup

from src.skin import SkinManager

rootPath = "/tmp/JB/"
path = "/tmp/JB-Blog/skins"
articleKeys = ["content", "path", "birthDate", "birthDateStr", "name", "title", "heading", "bgImage"]
newStyleArticle = {
	"site":{
		"tagline":"tagline sample text",
		"author" : {
			"nickname":"T",
			"name": "Testio Testo",
			"email":"Test@mail.example.org"
		},
		"domainName":"example.org",
		"name":"sample web site",
		"description":"this is sample page for JB."
	},
	"post":{
		"date":datetime.now(),
		"title":"sample page"
	},
	"contents":"this is a sample article"
}

class SkinTester(unittest.TestCase):
	def test_importSkin(self):
		s = SkinManager(path, "simple-blog-theme")
		skinData = s.get("article")

	def test_compile(self):
		article = {k:k for k in articleKeys}

		s = SkinManager(path, "simple-blog-theme")
		skin = s.compile("article", newStyleArticle)
# 		print(skin.file)

	def test_makoTemplate(self):
# 		mylookup = TemplateLookup(directories=['/home/wssh/JB/samples/'])
		mytemplate = Template(filename="samples/template.html")
		print(mytemplate.render(site={
"related_posts":[{"title":"test", "date":datetime.now().strftime("%Y/%m/%d"), "url":"test.html"}]}))
