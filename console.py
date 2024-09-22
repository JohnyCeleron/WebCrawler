import argparse
import asyncio
import os.path
import pickle
import aiohttp

import colorama
from colorama import Style, Fore
from src.default_crawler import DefaultCrawler
from src.image_crawler import ImageCrawler
from src.graph_builder import draw_graph
from src.crawler import CRAWLER_META

DEFAULT_MAX_URLS = 100
DEFAULT_MAX_DEPTH = 5


async def run(crawler):
    print(f"{Style.BRIGHT}{Fore.LIGHTGREEN_EX}Start{Style.RESET_ALL}")
    async with crawler:
        await crawler.run()
    print(f"{Style.BRIGHT}{Fore.LIGHTGREEN_EX}End{Style.RESET_ALL}")
    draw_graph()


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


def _check_to_continue(metadata):
    return any(len(metadata['crawl_queue'][url]) > 0 for url in
               metadata['crawl_queue'])


def _get_start_urls(metadata):
    return {url for url in metadata['crawl_queue'] if
            len(metadata['crawl_queue'][url]) > 0}


def _get_parametres(args):
    metadata_path = os.path.join(os.getcwd(), CRAWLER_META)
    do_continue = False
    start_urls = args.start_urls
    max_urls = args.max_urls
    max_depth = args.max_depth
    if os.path.exists(metadata_path):
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        if _check_to_continue(metadata):
            answer = input('You have previously used Crawler, but it has '
                           f'finished the job of completing page processing. '
                           f'It has been processed '
                           f'{metadata["count_crawled_urls"]}/{metadata["max_urls"]} '
                           'Do you want to continue?(Yes/No)').lower()
            while answer not in ('yes', 'no'):
                answer = input(
                    'Please answer the previous question either yes or no.').lower()
            if answer == 'yes':
                print(f'The crawler will continue from the moment the program '
                      f'is interrupted with the parameters:')
                print(f'max_urls: {metadata["max_urls"]}')
                print(f'max_depth: {metadata["max_depth"]}')
                do_continue = True
                start_urls = _get_start_urls(metadata)
                max_depth = metadata['max_depth']
                max_urls = metadata['max_urls']
    return do_continue, max_depth, max_urls, start_urls


def main():
    parser = _get_parser()

    args = parser.parse_args()

    crawler = {
        "default": DefaultCrawler,
        "image": ImageCrawler
    }

    try:
        do_continue, max_depth, max_urls, start_urls = _get_parametres(args)
        crawler = crawler[args.mode](start_urls=start_urls,
                                     max_urls=max_urls,
                                     max_depth=max_depth,
                                     do_continue=do_continue)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run(crawler))
    except AssertionError as e:
        print(f'{colorama.Fore.YELLOW}{e}')
    except KeyboardInterrupt:
        print(f'{Style.RESET_ALL} The program was prematurely stopped')
    except asyncio.TimeoutError:
        print(f'{Style.RESET_ALL} The time expired when sending or receiving the request')
    finally:
        print(colorama.Style.RESET_ALL)
        exit()


if __name__ == "__main__":
    main()
