from crawler import WebCrawler


class DefaultCrawler(WebCrawler):
    async def _process_page(self, queue):
        while True:
            _, _ = await queue.get()
            queue.task_done()

    async def _unload_data(self, data):
        pass