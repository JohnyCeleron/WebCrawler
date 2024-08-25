from src.crawler import WebCrawler


class DefaultCrawler(WebCrawler):
    async def _process_page(self, url, content):
        pass

    async def _unload_data(self, data):
        pass