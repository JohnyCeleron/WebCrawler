import abc
import logging
from collections import defaultdict
from collections import deque
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG, filename="py_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')


class WebCrawler(abc.ABC):
    def __init__(self, max_depth, max_urls, start_urls, crawl_delay=None):
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.start_urls = start_urls
        self.crawl_delay = crawl_delay
        self.data = defaultdict(list)

    def start_crawl(self):
        visited_url = set()
        count_url = 1
        queue = deque()
        for url in self.start_urls:
            queue.append((0, url))
        while 0 < len(queue) and count_url <= self.max_urls:
            depth, current_url = queue.popleft()

            visited_url.add(current_url)
            if depth + 1 > self.max_depth:
                continue
            try: # TODO: выбросить нормально исключение
                response = requests.get(current_url)
            except requests.ConnectionError:
                continue

            logging.info(current_url)
            content = response.content
            self._process_page(current_url, content)
            for url in self._get_links(content, current_url):
                if url not in visited_url:
                    count_url += 1
                    queue.append((depth + 1, url))
        self._unload_data(self.data)
        logging.info('end')

    def _get_links(self, content, current_url):
        soup = BeautifulSoup(content, 'html.parser')
        domain = urlparse(current_url).netloc
        for link_element in soup.select('a[href]'):
            link = urljoin(current_url, link_element['href'])
            if domain in link:
                yield link

    @abc.abstractmethod
    def _unload_data(self, data):
        # Выгружает данные
        pass

    @abc.abstractmethod
    def _process_page(self, url, content):
        # Обрабатывает страницу
        pass