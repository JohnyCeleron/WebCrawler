import aiohttp
import pytest

import html_constants
from src.default_crawler import DefaultCrawler


#TODO:написать тесты для image crawler

class TestLinks:
    BASE_URL = 'https://www.base_url.org/'

    @pytest.mark.parametrize("content,expected_links", [
        (html_constants.HTML_WITHOUT_URL, []),
        (html_constants.HTML_WITH_URL, ["https://www.base_url.org/"]),
        (html_constants.HTML_WITH_MORE_THAN_FIVE_URLS,
         ["https://www.base_url.org/foo1",
          "https://www.base_url.org/foo2",
          "https://www.base_url.org/foo3",
          "https://www.base_url.org/foo4",
          "https://www.base_url.org/foo5",
          "https://www.base_url.org/foo6"]),
        (html_constants.HTML_WITH_OTHER_URL, [])
    ])
    def test_html_url(self, content, expected_links):
        crawler = DefaultCrawler(max_urls=1, max_depth=1,
                                 start_urls=[self.BASE_URL],
                                 check_robots_txt=False)
        self._check(crawler, content, expected_links)

    def _check(self, crawler, content, expected_links):
        actual_links = [link for link in
                        crawler._get_links(content, self.BASE_URL)]
        assert actual_links == expected_links


class TestCrawler:
    BASE_URL = 'https://www.base_url.org/'
    OTHER_URL = 'https://www.other_url.org/'
    IMG_URL = "https://www.image_url.org/"

    @pytest.mark.parametrize("max_depth,max_urls, start_urls", [
        (-1, 5, [BASE_URL]),
        (0, 5, [BASE_URL]),
        (1, 0, [BASE_URL]),
        (1, -1, [BASE_URL]),
        (1, 1, None),
        (1, 1, [])
    ])
    def test_invalid_data(self, max_depth, max_urls, start_urls):
        with pytest.raises(AssertionError):
            _ = DefaultCrawler(max_depth=max_depth, max_urls=max_urls,
                               start_urls=start_urls)

    @pytest.mark.parametrize(
        "max_depth, max_urls, start_urls, expected_count_crawled_urls", [
            (1, 1, [BASE_URL], 1),
            (2, 2, [BASE_URL], 2),
            (2, 1, [BASE_URL], 1),
            (2, 10, [BASE_URL, OTHER_URL], 8),
            (2, 1, [BASE_URL, OTHER_URL, IMG_URL], 1)
        ])
    @pytest.mark.asyncio
    async def test_crawler_without_robots_txt(self, max_depth, max_urls,
                                              start_urls,
                                              expected_count_crawled_urls,
                                              monkeypatch):
        count_crawled_urls = 0

        async def mock_get_html_content(_, url):
            nonlocal count_crawled_urls
            count_crawled_urls += 1
            if url not in html_constants.TEST_RESPONSE:
                raise aiohttp.ClientError()
            html_content = html_constants.TEST_RESPONSE[url]["html_content"]
            if html_content == 'error':
                raise aiohttp.ClientError()
            return html_content

        monkeypatch.setattr("crawler.WebCrawler._get_html_content",
                            mock_get_html_content, raising=True)
        async with DefaultCrawler(max_depth=max_depth, max_urls=max_urls,
                                  start_urls=start_urls, check_robots_txt=False) as crawler:
            await crawler.run()
        assert count_crawled_urls == expected_count_crawled_urls
