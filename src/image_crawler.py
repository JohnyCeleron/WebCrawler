import asyncio
import json
import os
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup

from src.crawler import WebCrawler
from src.enums import FileType, InitType
from src.metadata_controller import Builder
UPLOAD_DATA_LOCK = asyncio.Lock()
PROCESS_PAGE_LOCK = asyncio.Lock()

IMAGE_DATA_JSON = 'image_data.json'


class ImageCrawler(WebCrawler):
    def __init__(self, max_depth, max_urls, start_urls, do_continue=False, check_robots_txt=True):
        super().__init__(max_depth=max_depth,
                         max_urls=max_urls,
                         start_urls=start_urls,
                         do_continue=do_continue,
                         check_robots_txt=check_robots_txt)
        Builder(self).initialize_file(IMAGE_DATA_JSON, FileType.JSON, InitType.DICT)
        path = os.path.join(os.getcwd(), IMAGE_DATA_JSON)
        with open(path, 'r') as f:
            old_data = json.load(f)
        self.data = old_data

    async def _unload_data(self, data):
        async with UPLOAD_DATA_LOCK:
            path = os.path.join(os.getcwd(), IMAGE_DATA_JSON)
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)

    async def _process_page(self, url, content):
        soup = BeautifulSoup(content, 'lxml')
        img_urls = {urljoin(url, item['src'])
                    for item in soup.find_all('img', src=True)
                    if item is not None}
        async with PROCESS_PAGE_LOCK:
            if url not in self.data:
                self.data[url] = list(img_urls)
            else:
                old_data = set(self.data[url])
                new_data = list(old_data | img_urls)
                self.data[url] = new_data
            await self._unload_data(self.data)
