BASE_URL = "https://www.base_url.org/"


HTML_WITHOUT_URL = f"""
<!DOCTYPE html>
<html lang="en">
  <body>
    <h1>without url</h1>
  </body>
</html>
"""


HTML_WITH_URL = f"""
<!DOCTYPE html>
<html>
<body>
    <a href="https://www.base_url.org/">
        Click Here to Open in Same Tab
    </a>
</body>
</html>
"""


HTML_WITH_MORE_THAN_FIVE_URLS = f"""
<!DOCTYPE html>
<html>
  <body>
    <a href="https://www.base_url.org/foo1">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.base_url.org/foo2">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.base_url.org/foo3">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.base_url.org/foo4">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.base_url.org/foo5">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.base_url.org/foo6">
      Click Here to Open in Same Tab
    </a>
  </body>
</html>
"""

HTML_WITH_OTHER_URL = f"""
<!DOCTYPE html>
<html>
  <body>
    <a href="https://www.other_url.org/foo1">
        <img src="image_other1.png" alt="Andrej Kesely&#39;s user avatar" width="32" height="32" class="bar-sm">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.other_url.org/foo2">
        <img src="image_other2.png" alt="Andrej Kesely&#39;s user avatar" width="32" height="32" class="bar-sm">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.other_url.org/foo3">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.other_url.org/foo4/other/base_url.org">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.other_url.org/foo5">
        <img src="image_other5.jpg" alt="Andrej Kesely&#39;s user avatar" width="32" height="32" class="bar-sm">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.other_url.org/foo6">
      Click Here to Open in Same Tab
    </a>
  </body>
</html>
"""


HTML_WITH_IMG = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Пример HTML страницы с картинками</title>
</head>
<body>
    <header>
        <h1>Пример HTML страницы с картинками</h1>
    </header>
    <main>
        <p>Ниже приведены несколько изображений:</p>
        <img src="image1.jpg" alt="Изображение 1" width="300" height="200">
        <img src="image2.jpg" alt="Изображение 2" width="300" height="200">
        <img src="image3.jpg" alt="Изображение 3" width="300" height="200">
    </main>
</body>
</html>
"""


HTML_FOO1 = f"""
<!DOCTYPE html>
<html>
  <body>
    <a href="https://www.base_url.org/bar1">
        <img src="image1.png" alt="Andrej Kesely&#39;s user avatar" width="32" height="32" class="bar-sm">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.base_url.org/bar2">
        <img src="image2.png" alt="Andrej Kesely&#39;s user avatar" width="32" height="32" class="bar-sm">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.other.org/foo3">
      Click Here to Open in Same Tab
    </a>
  </body>
</html>
"""


HTML_FOO2 = HTML_WITHOUT_URL
HTML_FOO3 = HTML_WITH_OTHER_URL
HTML_FOO4 = f"""
<!DOCTYPE html>
<html>
  <body>
    <a href="https://www.base_url.org/">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.base_url.org/foo1">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.other.org/foo3">
      Click Here to Open in Same Tab
    </a>
  </body>
</html>
"""
HTML_BAR1 = f"""
<!DOCTYPE html>
<html>
  <body>
    <a href="https://www.base_url.org/bar1">
      Click Here to Open in Same Tab
    </a>
  </body>
</html>
"""
HTML_BAR2 = HTML_BAR1

TEST_RESPONSE = {
    BASE_URL: {
        "status": 200,
        "html_content": HTML_WITH_MORE_THAN_FIVE_URLS
    },
    "https://www.base_url.org/foo1": {
        "status": 200,
        "html_content": HTML_FOO1
    },
    "https://www.base_url.org/foo2": {
        "status": 200,
        "html_content": HTML_FOO2
    },
    "https://www.base_url.org/foo3": {
        "status": 200,
        "html_content": HTML_FOO3
    },
    "https://www.base_url.org/foo4": {
        "status": 200,
        "html_content": HTML_FOO4
    },
    "https://www.base_url.org/foo5": {
        "status": 404,
        "html_content": ""
    },
    "https://www.base_url.org/foo6": {
        "status": 200,
        "html_content": HTML_WITHOUT_URL
    },
    "https://www.base_url.org/bar1": {
        "status": 200,
        "html_content": HTML_BAR1
    },
    "https://www.base_url.org/bar2": {
        "status": 200,
        "html_content": HTML_BAR2
    },
    "https://www.other_url.org/": {
        "status": 200,
        "html_content": HTML_WITH_OTHER_URL
    },
    "https://www.image_url.org/": {
        "status": 200,
        "html_content": HTML_WITH_IMG
    },
    "https://www.other.org/foo3":{
        "status": 403,
        "html_content": ""
    },
    "https://www.other_url.org/foo1":{
        "status": 404,
        "html_content": ""
    },
    "https://www.other_url.org/foo2":{
        "status": 404,
        "html_content": ""
    },
    "https://www.other_url.org/foo3":{
        "status": 404,
        "html_content": ""
    },
    "https://www.other_url.org/foo4/other/base_url.org":{
        "status": 404,
        "html_content": ""
    },
    "https://www.other_url.org/foo5":{
        "status": 404,
        "html_content": ""
    }
}