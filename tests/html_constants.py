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
    <a href="https://www.geeksforgeeks.org/">
        Click Here to Open in Same Tab
    </a>
</body>
</html>
"""


HTML_WITH_MOREO_THAN_FIVE_URLS = f"""
<!DOCTYPE html>
<html>
  <body>
    <a href="https://www.geeksforgeeks.org/">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.geeksforgeeks.org/">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.geeksforgeeks.org/">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.geeksforgeeks.org/">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.geeksforgeeks.org/">
      Click Here to Open in Same Tab
    </a>
    <br />
    <a href="https://www.geeksforgeeks.org/">
      Click Here to Open in Same Tab
    </a>
  </body>
</html>
"""