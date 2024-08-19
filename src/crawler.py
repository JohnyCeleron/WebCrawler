import abc
import asyncio
import logging
import urllib.error
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from collections import deque

import aiohttp
import colorama
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s",
                    encoding='utf-8')


# TODO: попробовать написать реализацию паттерна producer-consumer

LOCK1 = asyncio.Lock()
LOCK2 = asyncio.Lock()
LOCK3 = asyncio.Lock()

class WebCrawler(abc.ABC):
    def __init__(self, max_depth, max_urls, start_urls, check_robots_txt=True):
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.start_urls = start_urls
        self._check_robots_txt = check_robots_txt
        self._robots = self._prepare_robot_txt_parsers()
        self._crawl_delays = self._get_crawl_delays()
        self._count_crawled_urls = 0
        self._visited_url = set()

    @property
    def max_depth(self):
        return self._max_depth

    @max_depth.setter
    def max_depth(self, depth):
        if depth <= 0:
            raise AssertionError('Max depth must be positive')
        self._max_depth = depth

    @property
    def max_urls(self):
        return self._max_urls

    @max_urls.setter
    def max_urls(self, count_urls):
        if count_urls <= 0:
            raise AssertionError('Max urls must be positive')
        self._max_urls = count_urls

    @property
    def start_urls(self):
        return self._start_urls

    @start_urls.setter
    def start_urls(self, urls):
        if urls is None:
            raise AssertionError('Start urls must not be None')
        if len(urls) == 0:
            raise AssertionError('Count start urls must be positive')
        self._start_urls = set(urls)

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=200)
        self.session = await aiohttp.ClientSession(
            connector=connector).__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.__aexit__(exc_type, exc_val, exc_tb)

    async def run(self):
        queue_process_page = asyncio.Queue()
        producers = [asyncio.create_task(self.start_crawl(url, queue_process_page))
                     for url in self._start_urls]
        consumers = [asyncio.create_task(self._process_page(queue_process_page))
                    for _ in range(3)]

        await asyncio.gather(*producers)
        await queue_process_page.join()
        for consumer in consumers:
            consumer.cancel()
        logging.info('end')

    async def start_crawl(self, start_url, queue_process_page):
        queue = deque()
        queue.append((0, start_url))
        self._visited_url.add(start_url)

        while True:
            async with LOCK1:  # TODO: написать норм lock
                if self._count_crawled_urls >= self._max_urls or len(queue) == 0:
                    break
            depth, current_url = queue.popleft()

            if depth + 1 > self._max_depth:
                continue

            async with LOCK1:  # TODO: написать норм lock
                self._count_crawled_urls += 1
                try:
                    html_content = await self._get_html_content(current_url)
                except aiohttp.ClientError:
                    print(f'{colorama.Fore.YELLOW}WARNING: Could not get the '
                          f'html code for {current_url}')
                    continue
                logging.info(f'{self._count_crawled_urls} {current_url}')
                print(
                    f'{colorama.Fore.GREEN}{self._count_crawled_urls} {current_url}')

            await queue_process_page.put((current_url, html_content))
            await self._queue_crawl_page_put(current_url, depth, html_content,
                                             queue)
            await self._make_delay(start_url)

    async def _queue_crawl_page_put(self, current_url, depth, html_content,
                                    queue_crawl_page):
        async with LOCK1:
            MAX_NEXT_URLS = 10
            next_url_count = 1
            for url in self._get_links(html_content, current_url):
                if len(queue_crawl_page) + self._count_crawled_urls >= self._max_urls\
                        or next_url_count > MAX_NEXT_URLS:
                    break
                if url not in self._visited_url:
                    next_url_count += 1
                    self._visited_url.add(url)
                    queue_crawl_page.append((depth + 1, url))

    async def _get_html_content(self, current_url):
        async with self.session.get(current_url) as response:
            html_content = await response.text()
        return html_content

    def _prepare_robot_txt_parsers(self):
        if not self._check_robots_txt:
            return None
        robots = dict()
        for url in self._start_urls:
            try:
                base_url = self._get_base_url(url)
                robots[base_url] = RobotFileParser()
                robots[base_url].set_url(f"{base_url}/robots.txt")
                robots[base_url].read()
            except urllib.error.URLError:
                print(
                    f'{colorama.Fore.RED}Could not get data from robots.txt{colorama.Style.RESET_ALL}')
                exit()
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
        soup = BeautifulSoup(content, 'lxml')
        base_url = self._get_base_url(current_url)
        for link_element in soup.select('a[href]'):
            link = urljoin(current_url, link_element['href'])
            if link.startswith(base_url) and self._can_fetch(link):
                yield link

    @abc.abstractmethod
    async def _unload_data(self, data):
        # Выгружает данные
        pass

    @abc.abstractmethod
    async def _process_page(self, queue):
        # Обрабатывает страницу
        pass