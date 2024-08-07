import requests
import logging
import abc

from bs4 import BeautifulSoup
from collections import deque


logging.basicConfig(level=logging.DEBUG, filename="py_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')


class WebCrawler(abc.ABC):
    def __init__(self, start_url, max_urls, max_depth, crawl_delay=None):
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.start_url = start_url
        self.crawl_delay = crawl_delay

    def start(self):
        visited_url = set()
        count_url = 1
        queue = deque()
        queue.append((0, self.start_url))
        while 0 < len(queue) and count_url <= self.max_urls:
            depth, current_url = queue.popleft()

            visited_url.add(current_url)
            if depth + 1 > self.max_depth:
                continue

            try:
                response = requests.get(current_url)
            except Exception:
                # TODO: постараться обработать это исключение нормально
                continue

            logging.info(current_url)
            content = response.content
            self._process_page(current_url, content)
            for url in self._get_links(content):
                if url not in visited_url :
                    logging.info(count_url)
                    count_url += 1
                    queue.append((depth + 1, url))
        logging.info('end')

    def _get_links(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        for link_element in soup.select('a[href]'):
            yield link_element['href']

    @abc.abstractmethod
    def _unload_data(self, data):
        # Выгружает данные
        pass

    @abc.abstractmethod
    def _process_page(self, url, content):
        # Обрабатывает страницу
        pass