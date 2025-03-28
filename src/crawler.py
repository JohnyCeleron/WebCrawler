import abc
import asyncio
import hashlib
import json
import os
import urllib.error
from urllib.parse import urljoin, urlparse, unquote
from urllib.robotparser import RobotFileParser

import aiohttp
import colorama
from bs4 import BeautifulSoup

from src.metadata_controller import Builder, Getter, Updater, HASHED_URL_JSON
from src.settings_constants import get_constants

CRAWLER_LOCK = asyncio.Lock()
METADATA_LOCK = asyncio.Lock()

# TODO: конфигурировать выгрузку данных
settings_constants = get_constants()


class WebCrawler(abc.ABC):
    MAX_SIZE_QUEUE = settings_constants.MAX_SIZE_QUEUE
    TIMEOUT_CONNECTION = settings_constants.TIMEOUT_CONNECTION
    CONSUMERS_COUNT = settings_constants.CONSUMERS_COUNT
    MAX_NEXT_URLS = settings_constants.MAX_NEXT_URLS

    def __init__(self, max_depth, max_urls, start_urls, do_continue=False,
                 check_robots_txt=True):
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.start_urls = start_urls
        self._check_robots_txt = check_robots_txt
        self._robots = self._prepare_robot_txt_parsers()
        self._crawl_delays = self._get_crawl_delays()
        self._do_continue = do_continue

        Builder(self).create_files()
        self.getter_meta = Getter()
        self.updater_meta = Updater(self)
        self._count_url_in_queues = self.getter_meta.get_count_url_in_queues()
        self._visited_url = self.getter_meta.get_start_visited_url()

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
        connector = aiohttp.TCPConnector()
        self.session = await aiohttp.ClientSession(
            connector=connector).__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.__aexit__(exc_type, exc_val, exc_tb)

    async def run(self):
        queue_process_page = asyncio.Queue(maxsize=self.MAX_SIZE_QUEUE)
        producers = [
            asyncio.create_task(self.start_crawl(url, queue_process_page))
            for count, url in enumerate(self._start_urls) if
            count < self._max_urls and self._can_fetch(url)]
        consumers = [
            asyncio.create_task(self._get_consumer_task(queue_process_page))
            for _ in range(self.CONSUMERS_COUNT)]

        await asyncio.gather(*producers)
        await queue_process_page.join()
        for consumer in consumers:
            consumer.cancel()

    async def start_crawl(self, start_url, queue_process_page):
        queue = self.getter_meta.get_queue(start_url)
        async with CRAWLER_LOCK:
            if len(queue) == 0:
                start_url = self._decode_url_to_utf8(start_url)
                await self.updater_meta.add_to_queue(start_url, queue,
                                                     (0, start_url, None))
                await self.updater_meta.add_to_visited_urls(start_url)

        while len(queue) > 0:
            async with CRAWLER_LOCK:
                depth, current_url, previous_url = await self.updater_meta.remove_from_queue(
                    start_url, queue)
                if depth + 1 > self._max_depth:
                    continue

                try:
                    html_content = await self._get_html_content(current_url)
                except aiohttp.ClientResponseError as e:
                    await self._except_client_response_error(current_url, e)
                    continue
                else:
                    await self.updater_meta.update_count_crawled_urls()
                    count_crawled_urls = self.getter_meta.get_count_crawled_urls()
                    print(
                        f'{colorama.Fore.GREEN}{count_crawled_urls} {current_url}')
            self.updater_meta._add_edge(previous_url, current_url, start_url)
            if self._check_update(current_url, html_content):
                print(f'{colorama.Fore.YELLOW}UPDATE {current_url}')
                self._hash_url(current_url, html_content)
                await queue_process_page.put((current_url, html_content))
            await self._queue_crawl_page_put(current_url, depth, html_content,
                                             queue, start_url)
            await self._make_delay(start_url)

    async def _except_client_response_error(self, current_url, e):
        await self.updater_meta.update_count_crawled_urls()
        count_crawled_urls = self.getter_meta.get_count_crawled_urls()
        if e.status == 404:
            print(f'{colorama.Fore.YELLOW}{count_crawled_urls} '
                  f'WARNING: The page was not found (error 404): {current_url}')
        else:
            print(f'{colorama.Fore.YELLOW}{count_crawled_urls} '
                  f'WARNING: Error receiving the response {e}')

    async def _queue_crawl_page_put(self, current_url, depth, html_content,
                                    queue_crawl_page, start_url):
        async with CRAWLER_LOCK:
            next_url_count = 1
            for url in self._get_links(html_content, current_url):
                count_crawled_urls = self.getter_meta.get_count_crawled_urls()
                url = self._decode_url_to_utf8(url)
                if self._count_url_in_queues + count_crawled_urls >= self._max_urls \
                        or next_url_count > self.MAX_NEXT_URLS:
                    break
                if url not in self._visited_url:
                    next_url_count += 1
                    await self.updater_meta.add_to_visited_urls(url)
                    await self.updater_meta.add_to_queue(start_url,
                                                         queue_crawl_page,
                                                         (depth + 1, url,
                                                          current_url))

    async def _get_consumer_task(self, queue):
        while True:
            url, content = await queue.get()
            await self._process_page(url, content)
            queue.task_done()

    async def _get_html_content(self, current_url):
        async with self.session.get(current_url,
                                    timeout=self.TIMEOUT_CONNECTION) as response:
            if not response.ok:
                raise aiohttp.ClientResponseError\
                    (history=None, request_info=None, status=response.status)
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
        if base_url not in robots:
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

    @staticmethod
    def _decode_url_to_utf8(url):
        return unquote(url)

    @staticmethod
    def _get_base_url(url):
        return f"{urlparse(url).scheme}://{urlparse(url).netloc}/"

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

    @abc.abstractmethod
    async def _unload_data(self, data):
        # Выгружает данные
        pass

    @abc.abstractmethod
    async def _process_page(self, url, html_content):
        # Обрабатывает страницу
        pass
