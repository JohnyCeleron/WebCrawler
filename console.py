import argparse
import asyncio
import os.path
import pickle

import colorama
from colorama import Style, Fore

from src.metadata_controller import CRAWLER_META
from src.settings_constants import CONSTANTS_DESCRIPTION, get_constants, \
    set_constants, print_constants, reset

DEFAULT_MAX_URLS = 100
DEFAULT_MAX_DEPTH = 5

MODE_DESCRIPTION = {
    'default': "Краулер просто проходит по url ссылкам и ничего больше не "
               "делает",
    'image': "Краулер с url ссылок выкачивает ссылки на картинки"
}


async def run(crawler):
    from src.graph_builder import draw_graph

    print(f"{Style.BRIGHT}{Fore.LIGHTGREEN_EX}Start{Style.RESET_ALL}")
    async with crawler:
        await crawler.run()
    print(f"{Style.BRIGHT}{Fore.LIGHTGREEN_EX}End{Style.RESET_ALL}")
    draw_graph()


def _get_parser():
    # Создаем парсер
    parser = argparse.ArgumentParser(description="Свой краулер",
                                     formatter_class=argparse.RawTextHelpFormatter)
    command_subparser = parser.add_subparsers(dest='command',
                                              help='Доступные команды')

    _create_run_parser(command_subparser)
    _create_settings_parser(command_subparser)
    _create_reset_settings_parser(command_subparser)
    return parser


def _get_description_from_dictionary(dictionary):
    return '\n'.join(f"{key}: {value}" for key, value in dictionary.items())


def _create_reset_settings_parser(command_subparser):
    command_subparser.add_parser('reset_settings',
                                 help='Устанавливает настройки по умолчанию')


def _create_settings_parser(command_subparser):
    constants = get_constants()

    settings_data = {
        'MAX_SIZE_QUEUE': int,
        'TIMEOUT_CONNECTION': float,
        'CONSUMERS_COUNT': int,
        'MAX_NEXT_URLS': int,
        'ARROW_HEAD': int,
        'NODE_SIZE': float,
        'START_NODE_SIZE': float,
        'ARROW_SIZE': float,
        'ARROW_WIDTH': float
    }

    settings_parser = command_subparser.add_parser('settings',
                                                   help='Установить значения для констант Краулера')

    for key, _type in settings_data.items():
        settings_parser.add_argument(f'--{key}', type=_type,
                                     default=getattr(constants, key),
                                     help=CONSTANTS_DESCRIPTION[key])


def _create_run_parser(command_subparser):
    run_parser = command_subparser.add_parser('run', help='Запустить Краулер')
    run_parser.add_argument("start_urls", type=str, nargs='+',
                            help="URL, с которых будет происходить обход")
    run_parser.add_argument('mode', choices=MODE_DESCRIPTION,
                            help=_get_description_from_dictionary(
                                MODE_DESCRIPTION))
    run_parser.add_argument("--max_urls", type=int, default=DEFAULT_MAX_URLS,
                            help="Максимальное количество url, которое может обойти краулер")
    run_parser.add_argument("--max_depth", type=int, default=DEFAULT_MAX_DEPTH,
                            help="Максимальная глубина обхода")


def _check_to_continue(metadata):
    return any(len(metadata['crawl_queue'][url]) > 0 for url in
               metadata['crawl_queue'])


def _get_start_urls(metadata):
    return {url for url in metadata['crawl_queue'] if
            len(metadata['crawl_queue'][url]) > 0}


def _get_run_parametres(args):
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


def _get_crawler(args):
    from src.image_crawler import ImageCrawler
    from src.default_crawler import DefaultCrawler

    crawler = {
        "default": DefaultCrawler,
        "image": ImageCrawler
    }
    return crawler[args.mode]


def main():
    parser = _get_parser()

    args = parser.parse_args()

    try:
        if args.command == 'run':
            crawler = _get_crawler(args)
            _handle_run_command(args, crawler)
        elif args.command == 'settings':
            _handle_settings_command(args)
        elif args.command == 'reset_settings':
            _handle_reset_command()
    except AssertionError as e:
        print(f'{colorama.Fore.YELLOW}{e}')
    except KeyboardInterrupt:
        print(f'{Style.RESET_ALL} The program was prematurely stopped')
    except asyncio.TimeoutError:
        print(
            f'{Style.RESET_ALL} The time expired when sending or receiving the request')
    finally:
        print(colorama.Style.RESET_ALL)
        exit()


def _handle_reset_command():
    reset()
    print_constants()
    print('Настройки успешно сброшены')


def _handle_settings_command(args):
    set_constants(MAX_SIZE_QUEUE=args.MAX_SIZE_QUEUE,
                  TIMEOUT_CONNECTION=args.TIMEOUT_CONNECTION,
                  CONSUMERS_COUNT=args.CONSUMERS_COUNT,
                  MAX_NEXT_URLS=args.MAX_NEXT_URLS,
                  NODE_SIZE=args.NODE_SIZE,
                  START_NODE_SIZE=args.START_NODE_SIZE,
                  ARROW_HEAD=args.ARROW_HEAD,
                  ARROW_SIZE=args.ARROW_SIZE,
                  ARROW_WIDTH=args.ARROW_WIDTH)
    print_constants()
    print(f'The constants have been successfully set')


def _handle_run_command(args, crawler):
    do_continue, max_depth, max_urls, start_urls = _get_run_parametres(args)
    crawler = crawler(start_urls=start_urls,
                      max_urls=max_urls,
                      max_depth=max_depth,
                      do_continue=do_continue)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(crawler))


if __name__ == "__main__":
    main()
