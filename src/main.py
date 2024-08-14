import asyncio
import time

from src.image_crawler import ImageCrawler


async def main():
    start_time = time.time()
    async with ImageCrawler(start_urls=["https://blog.skillfactory.ru/parsing-saytov-na-python/",
                                        "https://ru.wikipedia.org/wiki/Заглавная_страница"],
                            max_urls=1000,
                            max_depth=5) as crawler:
        await crawler.run()
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
