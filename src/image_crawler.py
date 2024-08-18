import asyncio
import json
import os
from collections import defaultdict
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from crawler import WebCrawler


class ImageCrawler(WebCrawler):
    def __init__(self, max_depth, max_urls, start_urls, check_robots_txt=True):
        super().__init__(max_depth=max_depth,
                         max_urls=max_urls,
                         start_urls=start_urls,
                         check_robots_txt=check_robots_txt)
        self.data = defaultdict(list)

    async def _unload_data(self, data):
        with open(f'{os.getcwd()}/image_data.json', 'w') as f:
            json.dump(data, f, indent=4)

    async def _process_page(self, url, content):
        soup = BeautifulSoup(content, 'lxml')
        img_urls = {urljoin(url, item['src'])
                    for item in soup.find_all('img', src=True)
                    if item is not None}
        async with asyncio.Lock():
            self.data[url] = list(img_urls)
        await self._unload_data(self.data)
