import asyncio
import time
import yappi
from src.image_crawler import ImageCrawler


async def main():
    start_time = time.time()
    async with ImageCrawler(start_urls=["https://blog.skillfactory.ru/parsing-saytov-na-python/",
                                        "https://ru.wikipedia.org/wiki/Заглавная_страница"],
                            max_urls=100,
                            max_depth=5) as crawler:
        await crawler.run()
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    yappi.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    func_stats = yappi.get_func_stats()  # Собираем статистику выполненных функций
    func_stats.print_all()  # Выведем в консоль собранную статистику
    func_stats.save('yappi_output.pstats',
                    'PSTAT')  # Сохраняем в формате pstat
    func_stats.save('yappi_output.callgrind',
                    'CALLGRIND')  # Сохраняем в формате callgrind
    yappi.stop()  # Останавливаем наблюдение
    yappi.clear_stats()  # Очищаем статистик
