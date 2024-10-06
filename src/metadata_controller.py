import asyncio
import json
import os
import pickle
from collections import deque

from src.enums import InitType, FileType

METADATA_LOCK = asyncio.Lock()

HASHED_URL_JSON = 'hashed_url.json'
ADJESENT_EDGES_URL = 'adjesent_edges_url'
CRAWLER_META = 'metadata'
CONSTANTS_PICKLE = 'constants'


class Builder:
    '''
    Класс, который создаёт файлы для метаданных
    '''
    def __init__(self, crawler):
        self.crawler = crawler

    def create_files(self):
        self.initialize_file(HASHED_URL_JSON, FileType.JSON, InitType.DICT)
        if not self.crawler._do_continue:
            if os.path.exists(os.path.join(os.getcwd(), ADJESENT_EDGES_URL)):
                os.remove(os.path.join(os.getcwd(), ADJESENT_EDGES_URL))
            if os.path.exists(os.path.join(os.getcwd(), CRAWLER_META)):
                os.remove(os.path.join(os.getcwd(), CRAWLER_META))
        self.initialize_file(ADJESENT_EDGES_URL, FileType.PICKLE,
                             InitType.DICT)
        self.create_metadata_file()

    def create_metadata_file(self):
        path = os.path.join(os.getcwd(), CRAWLER_META)
        if not os.path.exists(path):
            with open(path, 'wb') as f:
                metadata = {
                    "max_depth": self.crawler._max_depth,
                    "max_urls": self.crawler._max_urls,
                    "visited_urls": set(),
                    "count_crawled_urls": 0,
                    "crawl_queue": {url: deque() for url in self.crawler.start_urls}
                }
                pickle.dump(metadata, f)

    @staticmethod
    def initialize_file(file_name, file_type, init_type):
        path = os.path.join(os.getcwd(), file_name)
        mode = {
            FileType.JSON: 'w',
            FileType.PICKLE: 'wb'
        }
        if not os.path.exists(path):
            with open(path, mode[file_type]) as f:
                init_object = {
                    InitType.LIST: list(),
                    InitType.SET: set(),
                    InitType.DICT: dict()
                }
                module = {
                    FileType.JSON: json,
                    FileType.PICKLE: pickle
                }
                module[file_type].dump(init_object[init_type], f)


class Updater:
    '''
    Класс, который обновляет данные в файлах и в самом Краулере
    '''
    def __init__(self, crawler):
        self.crawler = crawler
        self.getter_meta = crawler.getter_meta

    async def add_to_queue(self, start_url, queue, element):
        async with METADATA_LOCK:
            queue.append(element)
            metadata = self.getter_meta.get_metadata()
            metadata['crawl_queue'][start_url].append(element)
            self._save_metadata(metadata)
            self.crawler._count_url_in_queues += 1

    async def remove_from_queue(self, start_url, queue):
        async with METADATA_LOCK:
            metadata = self.getter_meta.get_metadata()
            metadata['crawl_queue'][start_url].popleft()
            removed_element = queue.popleft()
            self._save_metadata(metadata)
            self.crawler._count_url_in_queues -= 1
            return removed_element

    async def add_to_visited_urls(self, url):
        self.crawler._visited_url.add(url)
        async with METADATA_LOCK:
            metadata = self.getter_meta.get_metadata()
            metadata['visited_urls'].add(url)
            self._save_metadata(metadata)

    async def update_count_crawled_urls(self):
        async with METADATA_LOCK:
            metadata = self.getter_meta.get_metadata()
            metadata['count_crawled_urls'] += 1
            self._save_metadata(metadata)

    @staticmethod
    def _add_edge(start, end, start_vertix):
        path = os.path.join(os.getcwd(), ADJESENT_EDGES_URL)
        with open(path, 'rb') as f:
            edges = pickle.load(f)
        if start_vertix not in edges:
            edges[start_vertix] = list()
        edges[start_vertix].append((start, end))
        with open(path, 'wb') as f:
            pickle.dump(edges, f)

    @staticmethod
    def _save_metadata(data):
        with open(CRAWLER_META, 'wb') as f:
            pickle.dump(data, f)


class Getter:
    '''
    Класс, который выдавать данные из файлов
    '''
    def get_count_crawled_urls(self):
        metadata = self.get_metadata()
        return metadata['count_crawled_urls']

    def get_count_url_in_queues(self):
        metadata = self.get_metadata()
        return sum(len(queue) for queue in metadata['crawl_queue'].values())

    def get_queue(self, url):
        metadata = self.get_metadata()
        return metadata['crawl_queue'][url]

    def get_start_visited_url(self):
        metadata = self.get_metadata()
        return metadata['visited_urls']

    @staticmethod
    def get_metadata():
        metadata_path = os.path.join(os.getcwd(), CRAWLER_META)
        with open(metadata_path, 'rb') as f:
            return pickle.load(f)