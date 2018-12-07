---
title : JB 시작하기
---
###### 첫걸음
이 문서에서는 JB의 기본 구성과 사용법에 대해 설명합니다. 문서를 따라하면 완성된 형태의 블로그 프로젝트를 만들 수 있습니다.

프로젝트를 시작하려면 폴더가 있어야겠죠. /path/to/your/blog-project 폴더를 가상의 프로젝트 폴더로 사용하겠습니다. 프로젝트 폴더안에 config.json파일과 contents 폴더 하나를 만듭니다.
<pre>
blog-project
	- config.json
	+ contents
</pre>

config.json을 열어서 기본적인 설정들을 해보도록 하겠습니다. <pre><code class="json">{
	"path":{
		"build":"build",
		"contents":"contents",
		"resource":"resources",
		"skin":"skins/clean blog gh pages"
	},
	"site":{
		"author":{
			"nickname":"ariyn",
			"name":"MinUk Hwang",
			"email":"gmail.com"
		},
		"domainName":"this.ismin.uk",
		"name":"this is\nmin-uk",
		"description":"this is min-uk's personal web site.",
		"prefix":""
	}
}</code></pre>
너무 길군요. 한줄한줄 설명해 보도록 하겠습니다.

###### config.json
"path"는 필요한 경로들을 정의합니다.
* **"build"**는 컴파일된 파일들이 어디로 저장될 것인지.
* **"contents"**는 컴파일 될 파일의 경로입니다. 우리의 경우 "/path/.../blog-project/contents/" 입니다.
* **"resource"**는 리소스들의 위치입니다. 이미지, 음악, 동영상, 이 안에 들어있는것들은 "build/resource/"로 복사됩니다.
* **"skin"**은 컴파일할때 사용할 스킨이 있는 경로입니다.


"site"는 이 페이지에 대한 메타정보입니다.
* author는 페이지 작성자에 대한 정보입니다. nickname, name, email을 기본으로 지원합니다.
* domainName은 이 웹사이트의 도메인 이름입니다.
* name과 description은 각각 이 웹사이트에 대한 이름과 설명을 나타냅니다.
* prefix는 웹사이트의 기본으로 붙는 접두사입니다. 가령 호스팅된 웹사이트의 주소가 **this.ismin.uk/JB-sample/index.html**과 같은 형식이라면 prefix는 "JB-sample"이 됩니다. 만약 root에서 호스팅된다면 prefix는 빈 문자열("")이면 됩니다.

###### 파서
새 폴더에서 빈 파이썬 코드를 하나 만들고, compiler.Compiler를 임포트 해줍니다.
그리고 Compiler를 상속받는 새 파서 클래스를 선언합니다.
<pre><code class="python">import JB.compiler import Compiler

class BlogParser(Compiler):
  def __init__(self):
		self.path = "/path/to/your/blog-project"
		super().__init__(self.path)</code></pre>
이제 우리의 웹사이트를 파싱할 규칙들을 작성해 봅시다.

<pre><code class="python">
		self.mdSyntax = [
			(r"---", "<hr>"\n),
			(r"~~(.+?)~~", "<del>\1</del>"\n),
		]</code></pre>


###### 포스팅
좋아요! 이제 재미없는 부분은 다 끝나고 재밌는 부분이군요.