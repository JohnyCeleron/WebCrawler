import abc
import asyncio
import logging
from collections import deque
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import aiohttp
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG, filename="py_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s",
                    encoding='utf-8')


class WebCrawler(abc.ABC):
    def __init__(self, max_depth, max_urls, start_urls, check_robots_txt=True):
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.start_urls = start_urls
        self._check_robots_txt = check_robots_txt
        self._robots = self._prepare_robot_txt_parsers()
        self._crawl_delays = self._get_crawl_delays()

    @property
    def max_depth(self):
        return self._max_depth

    @max_depth.setter
    def max_depth(self, depth):
        assert depth > 0
        self._max_depth = depth

    @property
    def max_urls(self):
        return self._max_urls

    @max_urls.setter
    def max_urls(self, count_urls):
        assert count_urls > 0
        self._max_urls = count_urls

    @property
    def start_urls(self):
        return self._start_urls

    @start_urls.setter
    def start_urls(self, urls):
        assert urls is not None
        self._start_urls = set(urls)

    async def __aenter__(self):
        self.session = await aiohttp.ClientSession().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.__aexit__(exc_type, exc_val, exc_tb)

    async def run(self):
        tasks = []
        for url in self._start_urls:
            if self._can_fetch(url):
                tasks.append(asyncio.create_task(self.start_crawl(url)))
        await asyncio.gather(*tasks)

    async def start_crawl(self, start_url):
        visited_url = set()
        count_url = 1
        queue = deque()
        queue.append((0, start_url))
        while 0 < len(queue) and count_url <= self._max_urls:
            depth, current_url = queue.popleft()
            count_url += 1
            logging.info(current_url)
            visited_url.add(current_url)

            if depth + 1 > self._max_depth:
                continue

            try:
                html_content = await self.try_get_html_content(current_url)
            except aiohttp.ClientError as e:
                logging.warning(e)
                continue
            await self._process_page(current_url, html_content)

            for url in self._get_links(html_content, current_url):
                if url not in visited_url:
                    queue.append((depth + 1, url))

            await self._make_delay(current_url)
        logging.info('end')

    async def try_get_html_content(self, current_url):
        async with self.session.get(current_url) as response:
            html_content = await response.text()
        return html_content

    def _prepare_robot_txt_parsers(self):
        if not self._check_robots_txt:
            return None
        robots = dict()
        for url in self._start_urls:
            base_url = self._get_base_url(url)
            robots[base_url] = RobotFileParser()
            robots[base_url].set_url(f"{base_url}/robots.txt")
            robots[base_url].read()
        return robots

    async def _make_delay(self, url):
        if not self._check_robots_txt:
            return
        base_url = self._get_base_url(url)
        delay = self._crawl_delays[base_url]
        if delay is not None:
            await asyncio.sleep(delay)

    def _get_base_url(self, url):
        return f"{urlparse(url).scheme}://{urlparse(url).netloc}/"

    def _get_crawl_delays(self):
        if not self._check_robots_txt:
            return None
        crawl_delays = dict()
        for url in self._start_urls:
            base_url = self._get_base_url(url)
            crawl_delays[base_url] = self._robots[base_url].crawl_delay('*')
        return crawl_delays

    def _can_fetch(self, url):
        if not self._check_robots_txt:
            return True
        base_url = self._get_base_url(url)
        return self._robots[base_url].can_fetch('*', url)

    def _get_links(self, content, current_url):
        soup = BeautifulSoup(content, 'html.parser')
        base_url = self._get_base_url(current_url)
        for link_element in soup.select('a[href]'):
            link = urljoin(current_url, link_element['href'])
            logging.info(link)
            logging.info(base_url)
            if link.startswith(base_url) and self._can_fetch(link):
                yield link

    @abc.abstractmethod
    async def _unload_data(self, data):
        # Выгружает данные
        pass

    @abc.abstractmethod
    async def _process_page(self, url, content):
        # Обрабатывает страницу
        pass


if __name__ == '__main__':
    rp = RobotFileParser()
    rp.set_url("https://www.schoolsw3.com/robots.txt")
    rp.read()
    print(rp.crawl_delay('*'))
