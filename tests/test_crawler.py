import pytest
from src.crawler import WebCrawler
import html_constants


class DefaultCrawler(WebCrawler):
    async def _process_page(self, url, content):
        pass

    async def _unload_data(self, data):
        pass


class TestLinks:
    BASE_URL = 'https://www.base_url.org/'

    @pytest.mark.parametrize("content,expected_links", [
        (html_constants.HTML_WITHOUT_URL, []),
        (html_constants.HTML_WITH_URL, ["https://www.base_url.org/"]),
        (html_constants.HTML_WITH_MORE_THAN_FIVE_URLS, ["https://www.base_url.org/foo1",
                                                        "https://www.base_url.org/foo2",
                                                        "https://www.base_url.org/foo3",
                                                        "https://www.base_url.org/foo4",
                                                        "https://www.base_url.org/foo5",
                                                        "https://www.base_url.org/foo6"]),
        (html_constants.HTML_WITH_OTHER_URL, [])
    ])
    def test_html_url(self, content, expected_links):
        crawler = DefaultCrawler(max_urls=0, max_depth=0,
                                 start_urls=[self.BASE_URL], check_robots_txt=False)
        self._check(crawler, content, expected_links)

    def _check(self, crawler, content, expected_links):
        actual_links = [link for link in crawler._get_links(content, self.BASE_URL)]
        assert actual_links == expected_links