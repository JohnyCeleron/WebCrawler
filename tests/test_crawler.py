import aiohttp
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

    @pytest.mark.parametrize("max_depth,max_urls, start_urls", [
        (-1, 5, [BASE_URL]),
        (0, 5, [BASE_URL]),
        (1, 0, [BASE_URL]),
        (1, -1, [BASE_URL]),
        (1, 1, None)
    ])
    def test_invalid_data(self, max_depth, max_urls, start_urls):
        with pytest.raises(AssertionError):
            _ = DefaultCrawler(max_depth=max_depth, max_urls=max_urls,
                               start_urls=start_urls)

    @pytest.mark.parametrize(
        "max_depth, max_urls, start_urls, expected_crawled_urls", [
            (1, 1, [BASE_URL], ["https://www.base_url.org/"]),
            (2, 2, [BASE_URL], ["https://www.base_url.org/", "https://www.base_url.org/foo1"]),
            (2, 1, [BASE_URL], ["https://www.base_url.org/"])
        ])
    @pytest.mark.asyncio
    async def test_crawler_without_robots_txt(self, max_depth, max_urls,
                                              start_urls, expected_crawled_urls,
                                              monkeypatch):
        crawled_urls = []

        async def mock_get_html_content(_, url):
            crawled_urls.append(url)
            html_content = html_constants.TEST_RESPONSE[url]["html_content"]
            if html_content == 'error':
                raise aiohttp.ClientError()
            return html_content

        monkeypatch.setattr("src.crawler.WebCrawler.try_get_html_content",
                            mock_get_html_content, raising=True)
        async with DefaultCrawler(max_depth=max_depth, max_urls=max_urls,
                                  start_urls=start_urls, check_robots_txt=False) as crawler:
            await crawler.run()
        assert crawled_urls == expected_crawled_urls
