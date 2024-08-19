import asyncio
import json
import os
from collections import defaultdict
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from crawler import WebCrawler


LOCK = asyncio.Lock()

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

    async def _process_page(self, queue):
        while True:
            url, content = await queue.get()
            soup = BeautifulSoup(content, 'lxml')
            img_urls = {urljoin(url, item['src'])
                        for item in soup.find_all('img', src=True)
                        if item is not None}
            async with LOCK: #TODO: написать норм lock
                self.data[url] = list(img_urls)
            await self._unload_data(self.data)
            queue.task_done()


async def main():
    async with ImageCrawler(start_urls=['https://ru.wikipedia.org/wiki/Заглавная_страница,'
                                        'https://www.geeksforgeeks.org/python-programming-language-tutorial/'],
                            max_urls=100,
                            max_depth=5) as crawler:
        await crawler.run()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
