import abc
import logging
import time
from urllib.robotparser import RobotFileParser
from collections import defaultdict
from collections import deque
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG, filename="py_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')


class WebCrawler(abc.ABC):
    def __init__(self, max_depth, max_urls, start_urls):
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.start_urls = set(start_urls)
        self.data = defaultdict(list)
        self._robots = self._prepare_robot_txt_parsers()
        self._crawl_delays = self._get_crawl_delays()

    def _prepare_robot_txt_parsers(self):
        robots = dict()
        for url in self.start_urls:
            base_url = self._get_base_url(url)
            robots[base_url] = RobotFileParser()
            robots[base_url].set_url(f"{base_url}/robots.txt")
            robots[base_url].read()
        return robots

    def _make_delay(self, url):
        base_url = self._get_base_url(url)
        delay = self._crawl_delays[base_url]
        if delay is not None:
            time.sleep(delay)

    def _get_base_url(self, url):
        return f"{urlparse(url).scheme}://{urlparse(url).netloc}/"

    def _get_crawl_delays(self):
        crawl_delays = dict()
        for url in self.start_urls:
            base_url = self._get_base_url(url)
            crawl_delays[base_url] = self._robots[base_url].crawl_delay('*')
        return crawl_delays

    def _can_fetch(self, url):
        base_url = self._get_base_url(url)
        return self._robots[base_url].can_fetch('*', url)

    def start_crawl(self):
        visited_url = set()
        count_url = 1
        queue = deque()
        for url in self.start_urls:
            if self._can_fetch(url):
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
            self._make_delay(current_url)
        logging.info('end')

    def _get_links(self, content, current_url):
        soup = BeautifulSoup(content, 'html.parser')
        base_url = self._get_base_url(current_url)
        for link_element in soup.select('a[href]'):
            link = urljoin(current_url, link_element['href'])
            if base_url in link and self._can_fetch(link):
                yield link

    @abc.abstractmethod
    def _unload_data(self, data):
        # Выгружает данные
        pass

    @abc.abstractmethod
    def _process_page(self, url, content):
        # Обрабатывает страницу
        pass


if __name__ == '__main__':
    rp = RobotFileParser()
    rp.set_url("https://www.schoolsw3.com/robots.txt")
    rp.read()
    print(rp.can_fetch('*', 'https://www.schoolsw3.com/images/'))