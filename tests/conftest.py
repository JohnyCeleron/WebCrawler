import html_constants
import pytest
from aioresponses import aioresponses


def pass_function(*args, **kwargs):
    pass


def none_function(*args, **kwargs):
    return None

async def async_pass_function(*args, **kwargs):
    pass

@pytest.fixture
def mock_urls():
    with aioresponses() as m:
        for url, response_data in html_constants.TEST_RESPONSE.items():
            status = response_data['status']
            html_content = response_data['html_content']
            m.get(url, body=html_content, status=status)
        yield m


@pytest.fixture
def mock_robots_txt(monkeypatch):
    monkeypatch.setattr('src.crawler.WebCrawler._make_delay', async_pass_function)
    monkeypatch.setattr('src.crawler.WebCrawler._get_crawl_delays',
                        none_function)
    monkeypatch.setattr('src.crawler.WebCrawler._prepare_robot_txt_parsers',
                        pass_function)

    def mock_can_fetch(_, url):
        return html_constants.TEST_RESPONSE[url]['can_fetch']

    monkeypatch.setattr('src.crawler.WebCrawler._can_fetch', mock_can_fetch)
