from src.crawler import WebCrawler
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin
import json


class ImageCrawler(WebCrawler):
    def _unload_data(self, data):
        with open('data.json', 'a') as f:
            json.dump(data, f, indent=4)

    def _process_page(self, url, content):
        soup = BeautifulSoup(content, 'html.parser')
        data = {url: []}
        for item in soup.find_all('img', src=True):
            if item is not None:
                logging.info(item)
                data[url].append(urljoin(url, item['src']))
        self._unload_data(data)


if __name__ == '__main__':
    crawler = ImageCrawler(fr"https://timeweb.com/", 100, 10)
    crawler.start()