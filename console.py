import argparse
import asyncio
import time

import colorama
from colorama import Style, Fore
from src.default_crawler import DefaultCrawler
from src.image_crawler import ImageCrawler

DEFAULT_MAX_URLS = 100
DEFAULT_MAX_DEPTH = 5


async def run(crawler):
    start_time = time.time()
    print(f"{Style.BRIGHT}{Fore.LIGHTGREEN_EX}Start{Style.RESET_ALL}")
    async with crawler:
        await crawler.run()
    print(f"{Style.BRIGHT}{Fore.LIGHTGREEN_EX}End{Style.RESET_ALL}")
    print("--- %s seconds ---" % (time.time() - start_time))


def _get_parser():
    # Создаем парсер
    parser = argparse.ArgumentParser(description="Свой краулер",
                                     formatter_class=argparse.RawTextHelpFormatter)
    MODE_DESCRIPTION = {
        'default': "Краулер просто проходит по url ссылкам и ничего больше не делает",
        'image': "Краулер с url ссылок выкачивает ссылки на картинки"
    }
    # Добавляем аргументы
    parser.add_argument("start_urls", type=str, nargs='+',
                        help="URL, с которых будет происходить обход")
    parser.add_argument('mode', choices=MODE_DESCRIPTION,
                        help='\n'.join(
                            f"{key}: {value}" for key, value in
                            MODE_DESCRIPTION.items()))
    parser.add_argument("--max_urls", type=int, default=DEFAULT_MAX_URLS,
                        help="Максимальное количество url, которое может обойти краулер")
    parser.add_argument("--max_depth", type=int, default=DEFAULT_MAX_DEPTH,
                        help="Максимальная глубина обхода")
    return parser


def main():
    parser = _get_parser()

    args = parser.parse_args()

    crawler = {
        "default": DefaultCrawler,
        "image": ImageCrawler
    }

    try:
        crawler = crawler[args.mode](start_urls=args.start_urls,
                               max_urls=args.max_urls,
                               max_depth=args.max_depth)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run(crawler))
    except AssertionError as e:
        print(f'{colorama.Fore.YELLOW}{e}')
        exit()
    finally:
        print(colorama.Style.RESET_ALL)


if __name__ == "__main__":
    main()