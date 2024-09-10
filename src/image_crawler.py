import asyncio
import json
import os
from collections import defaultdict
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.crawler import WebCrawler

UPLOAD_DATA_LOCK = asyncio.Lock()
PROCESS_PAGE_LOCK = asyncio.Lock()

IMAGE_DATA_JSON = 'image_data.json'


class ImageCrawler(WebCrawler):
    def __init__(self, max_depth, max_urls, start_urls, check_robots_txt=True):
        super().__init__(max_depth=max_depth,
                         max_urls=max_urls,
                         start_urls=start_urls,
                         check_robots_txt=check_robots_txt)
        super()._initialize_json_file(IMAGE_DATA_JSON)
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


async def main():
    async with ImageCrawler(
            start_urls=['https://ru.wikipedia.org/wiki/Заглавная_страница'],
            max_urls=100,
            max_depth=5) as crawler:
        await crawler.run()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
