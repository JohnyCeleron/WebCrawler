import os.path
import pickle
from dataclasses import dataclass, asdict
from src.metadata_controller import CONSTANTS_PICKLE

PATH = os.path.join(os.getcwd(), CONSTANTS_PICKLE)

CONSTANTS_DESCRIPTION = {
    'MAX_SIZE_QUEUE': "Максимальный размер асинхронной очереди",
    'TIMEOUT_CONNECTION': "Максимальное время между отправкой запроса на получение страницы",
    'CONSUMERS_COUNT': "Количество 'асинхронных потоков', которые будут обрабатывать страницы",
    'MAX_NEXT_URLS': "Максимальное количество следующих url, которые будут "
                     "добавлены в очередь обхода после обработки текущего url ",
    'NODE_SIZE': "Размер не стартовых вершин",
    'START_NODE_SIZE': "Размер стартовых вершин",
    'ARROW_HEAD': "Стиль стрелки (принимает целые значения от 0 до 8)",
    'ARROW_SIZE': "Размер конца стрелки, относительно 'ARROW_WIDTH'",
    'ARROW_WIDTH': "Ширина линии стрелки"
}


@dataclass
class SettingConstants:
    MAX_SIZE_QUEUE: int = 20
    TIMEOUT_CONNECTION: float = 5
    CONSUMERS_COUNT: int = 1
    MAX_NEXT_URLS: int = 5

    NODE_SIZE: float = 10
    START_NODE_SIZE: float = 50
    ARROW_HEAD: int = 5
    ARROW_SIZE: float = 1.5
    ARROW_WIDTH: float = 0.5

    def __post_init__(self):
        if self.MAX_SIZE_QUEUE <= 0:
            raise AssertionError('MAX_SIZE_QUEUE must be positive')
        if self.TIMEOUT_CONNECTION <= 0:
            raise AssertionError('TIMEOUT_CONNECTION must be positive')
        if self.CONSUMERS_COUNT <= 0:
            raise AssertionError('CONSUMERS_COUNT must be positive')
        if self.MAX_NEXT_URLS <= 0:
            raise AssertionError('MAX_NEXT_URLS must be positive')
        if self.NODE_SIZE <= 0:
            raise AssertionError('NODE_SIZE must be positive')
        if self.START_NODE_SIZE <= 0:
            raise AssertionError('START_NODE_SIZE must be positive')
        if self.ARROW_HEAD not in {x for x in range(0, 9)}:
            raise AssertionError('ARROW_HEAD must be integer in range from 0 to 8')
        if self.ARROW_SIZE < 0.3:
            raise AssertionError('ARROW_SIZE must be great or equal than 0.3')
        if self.ARROW_WIDTH < 0.1:
            raise AssertionError('ARROW_WIDTH must be great or equal than 0.1')

    def __str__(self):
        constants_dict = asdict(self)
        return '\n'.join(
            f'{key}: {value}' for key, value in constants_dict.items())


def init_constants_file():
    if not (os.path.exists(PATH)):
        with open(PATH, 'wb') as f:
            pickle.dump(SettingConstants(), f)


def reset():
    set_constants()


def get_constants():
    if not (os.path.exists(PATH)):
        init_constants_file()
    with open(PATH, 'rb') as f:
        constants = pickle.load(f)
    return constants


def set_constants(**kwargs):
    constant = SettingConstants(**kwargs)
    with open(PATH, 'wb') as f:
        pickle.dump(constant, f)


def print_constants():
    constants = get_constants()
    print(str(constants))
    print()
