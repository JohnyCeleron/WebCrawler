import aiohttp, asyncio
from src.image_crawler import ImageCrawler
import time


async def main():
    start_time = time.time()
    async with ImageCrawler(start_urls=["https://www.amazon.com/",
                                        "https://ru.wikipedia.org/wiki/Заглавная_страница"],
                            max_urls=5000,
                            max_depth=10) as crawler:
        await crawler.run()
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
