import abc
import asyncio
import os
import urllib.error
import json
import hashlib
from collections import deque
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import aiohttp
import colorama
from bs4 import BeautifulSoup

CRAWLER_LOCK = asyncio.Lock()
MAX_SIZE_QUEUE = 20
HASHED_URL_JSON = 'hashed_url.json'  # json, в котором хранятся пары url: <hash>
ADJESENT_EDGES_URL = 'adjesent_edges_url.json'  # json, который понадобится для того, чтобы граф сделать


class WebCrawler(abc.ABC):
    def __init__(self, max_depth, max_urls, start_urls, check_robots_txt=True):
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.start_urls = start_urls
        self._check_robots_txt = check_robots_txt
        self._robots = self._prepare_robot_txt_parsers()
        self._crawl_delays = self._get_crawl_delays()
        self._count_crawled_urls = 0
        self._count_url_in_queues = 0
        self._visited_url = set()

        self._initialize_json_file(HASHED_URL_JSON)
        if os.path.exists(os.path.join(os.getcwd(), ADJESENT_EDGES_URL)):
            os.remove(os.path.join(os.getcwd(), ADJESENT_EDGES_URL))
        self._initialize_json_file(ADJESENT_EDGES_URL)

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
        # TODO: ограничить размер очереди
        # TODO: проверять что страница обновилась
        # TODO: научиться продолжать работу краулера после остановки + написать это в README
        # TODO: строить граф обход

        queue_process_page = asyncio.Queue(maxsize=MAX_SIZE_QUEUE)
        producers = [
            asyncio.create_task(self.start_crawl(url, queue_process_page))
            for count, url in enumerate(self._start_urls) if
            count < self._max_urls]
        consumers = [
            asyncio.create_task(self._get_consumer_task(queue_process_page))
            for _ in range(3)]

        await asyncio.gather(*producers)
        await queue_process_page.join()
        for consumer in consumers:
            consumer.cancel()

    @staticmethod
    def _check_update(url, content):
        # Проверяет, что url обновилась
        path = os.path.join(os.getcwd(), HASHED_URL_JSON)
        with open(path, 'r') as f:
            hash_urls = json.load(f)
        if url not in hash_urls:
            return True
        old_hash = hash_urls[url]
        new_hash = hashlib.sha256(content.encode()).hexdigest()
        return old_hash != new_hash  # При проверке мы пренебрегаем коллизиями

    @staticmethod
    def _hash_url(url, content):
        path = os.path.join(os.getcwd(), HASHED_URL_JSON)
        with open(path, 'r') as f:
            hash_urls = json.load(f)
        hash_urls[url] = hashlib.sha256(content.encode()).hexdigest()
        with open(path, 'w') as f:
            json.dump(hash_urls, f, indent=4)

    @staticmethod
    def _add_edge(start, end):
        path = os.path.join(os.getcwd(), ADJESENT_EDGES_URL)
        with open(path, 'r') as f:
            edges = json.load(f)
        if start not in edges:
            edges[start] = []
        edges[start].append(end)
        with open(path, 'w') as f:
            json.dump(edges, f, indent=4)

    async def start_crawl(self, start_url, queue_process_page):
        async with CRAWLER_LOCK:
            queue = deque()
            queue.append((0, start_url, None))
            self._count_url_in_queues += 1
            self._visited_url.add(start_url)

        while len(queue) > 0:
            depth, current_url, previous_url = queue.popleft()
            async with CRAWLER_LOCK:
                self._count_url_in_queues -= 1

            if depth + 1 > self._max_depth:
                continue

            async with CRAWLER_LOCK:
                self._count_crawled_urls += 1
                try:
                    html_content = await self._get_html_content(current_url)
                except aiohttp.ClientError:
                    print(f'{colorama.Fore.YELLOW}WARNING: Could not get the '
                          f'html code for {current_url}')
                    continue
                print(
                    f'{colorama.Fore.GREEN}{self._count_crawled_urls} {current_url}')

            if previous_url is not None:
                self._add_edge(previous_url, current_url)
            if self._check_update(current_url, html_content):
                print(f'{colorama.Fore.YELLOW}UPDATE {current_url}')
                self._hash_url(current_url, html_content)
                await queue_process_page.put((current_url, html_content))
            await self._queue_crawl_page_put(current_url, depth, html_content,
                                             queue)
            await self._make_delay(start_url)

    async def _queue_crawl_page_put(self, current_url, depth, html_content,
                                    queue_crawl_page):
        async with CRAWLER_LOCK:
            MAX_NEXT_URLS = 10
            next_url_count = 1
            for url in self._get_links(html_content, current_url):
                if self._count_url_in_queues + self._count_crawled_urls >= self._max_urls \
                        or next_url_count > MAX_NEXT_URLS:
                    break
                if url not in self._visited_url:
                    next_url_count += 1
                    self._visited_url.add(url)
                    self._count_url_in_queues += 1
                    queue_crawl_page.append((depth + 1, url, current_url))

    async def _get_consumer_task(self, queue):
        while True:
            url, content = await queue.get()
            await self._process_page(url, content)
            queue.task_done()

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
                self._set_robots(robots, url)
            except urllib.error.URLError:
                print(
                    f'{colorama.Fore.RED}Could not get data from robots.txt{colorama.Style.RESET_ALL}')
                exit()
        return robots

    def _set_robots(self, robots, url):
        base_url = self._get_base_url(url)
        robots[base_url] = RobotFileParser()
        robots[base_url].set_url(f"{base_url}/robots.txt")
        robots[base_url].read()

    async def _make_delay(self, url):
        if not self._check_robots_txt:
            return
        base_url = self._get_base_url(url)
        delay = self._crawl_delays[base_url]
        if delay is not None:
            await asyncio.sleep(delay)

    @staticmethod
    def _get_base_url(url):
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

    @staticmethod
    def _initialize_json_file(file_name):
        path = os.path.join(os.getcwd(), file_name)
        if not os.path.exists(path):
            with open(path, 'w+') as f:
                json.dump(dict(), f, indent=4)

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
    async def _process_page(self, url, html_content):
        # Обрабатывает страницу
        pass
