from src.crawler import WebCrawler
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin
import json


# TODO: оптимизировать, добавить асинхронности

class ImageCrawler(WebCrawler):
    def _unload_data(self, data):
        with open('image_data.json', 'w') as f:
            json.dump(data, f, indent=4)

    def _process_page(self, url, content):
        soup = BeautifulSoup(content, 'html.parser')
        for item in soup.find_all('img', src=True):
            if item is not None:
                logging.info(item)
                self.data[url].append(urljoin(url, item['src']))


if __name__ == '__main__':
    import time

    start_time = time.time()
    crawler = ImageCrawler(start_urls=[fr"https://journal.tinkoff.ru/"],
                           max_urls=1000,
                           max_depth=1)
    crawler.start_crawl()
    print("--- %s seconds ---" % (time.time() - start_time))
