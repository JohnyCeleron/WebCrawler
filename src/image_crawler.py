from src.crawler import WebCrawler
from collections import defaultdict
from bs4 import BeautifulSoup
import asyncio
from urllib.parse import urljoin
import json
from lxml import etree


# TODO: оптимизировать, добавить асинхронности

class ImageCrawler(WebCrawler):
    def __init__(self, max_depth, max_urls, start_urls):
        super().__init__(max_depth=max_depth,
                         max_urls=max_urls,
                         start_urls=start_urls)
        self.data = defaultdict(list)

    async def _unload_data(self, data):
        with open('image_data.json', 'w') as f:
            json.dump(data, f, indent=4)

    async def _process_page(self, url, content):
        soup = BeautifulSoup(content, 'lxml')
        img_urls = {urljoin(url, item['src'])
                    for item in soup.find_all('img', src=True)
                    if item is not None}
        async with asyncio.Lock():
            self.data[url] = list(img_urls)
        await self._unload_data(self.data)


if __name__ == '__main__':
    import time

    # start_time = time.time()
    # crawler = ImageCrawler(start_urls=["https://www.amazon.com/"],
    #                       max_urls=1000,
    #                       max_depth=10)
    # crawler.start_crawl()
    # print("--- %s seconds ---" % (time.time() - start_time))
