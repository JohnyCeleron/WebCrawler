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
    <a href="https://www.other.org/foo1">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.other.org/foo2">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.other.org/foo3">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.other.org/foo4/other/base_url.org">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.other.org/foo5">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.other.org/foo6">
      Click Here to Open in Same Tab
    </a>
  </body>
</html>
"""