import json

import aiohttp
import pytest
import os
import tests.html_constants as html_constants

from src.image_crawler import ImageCrawler


class TestImageLinks:
    BASE_URL = 'https://www.base_url.org/'

    @pytest.mark.parametrize("url,expected_images", [
        ("https://www.image_url.org/", ['https://www.image_url.org/image1.jpg',
                                        'https://www.image_url.org/image2.jpg',
                                        'https://www.image_url.org/image3.jpg']),
        ("https://www.other_url.org/",
         ["https://www.other_url.org/image_other1.png",
          "https://www.other_url.org/image_other2.png",
          "https://www.other_url.org/image_other5.jpg"]),
        (
        "https://www.base_url.org/foo1", ["https://www.base_url.org/image1.png",
                                          "https://www.base_url.org/image2.png"]),
        (BASE_URL, "")
    ])
    @pytest.mark.asyncio
    async def test_html_img_valid(self, url, expected_images):
        crawler = ImageCrawler(max_urls=1, max_depth=1,
                               start_urls=[self.BASE_URL],
                               check_robots_txt=False)
        await self._check(crawler, url, expected_images)


    @pytest.mark.parametrize("url", [
        "", "https://www.bar_url.org", "https://www.base_url.org/foo5"
    ])
    @pytest.mark.asyncio
    async def test_html_img_invalid(self, url):
        crawler = ImageCrawler(max_urls=1, max_depth=1,
                               start_urls=[self.BASE_URL],
                               check_robots_txt=False)
        with pytest.raises(aiohttp.ClientError):
            await self._check(crawler, url)

    async def _check(self, crawler, url, expected_images=None):
        if url not in html_constants.TEST_RESPONSE or \
                html_constants.TEST_RESPONSE[url]['status'] == 404:
            raise aiohttp.ClientResponseError(history=None, request_info=None, status=404)
        content = html_constants.TEST_RESPONSE[url]['html_content']
        await crawler._process_page(url, content)
        actual_images = crawler.data[url]
        assert len(actual_images) == len(expected_images)
        assert set(actual_images) == set(expected_images)


class TestCrawlerImages:
    BASE_URL = 'https://www.base_url.org/'
    OTHER_URL = 'https://www.other_url.org/'

    @pytest.mark.parametrize(
        "max_depth, max_urls, start_urls", [
            (1, 1, [BASE_URL]),
            (2, 2, [BASE_URL]),
            (2, 1, [BASE_URL]),
            (2, 10, [BASE_URL, OTHER_URL])
        ])
    @pytest.mark.asyncio
    async def test_crawler_without_robots_txt(self, max_depth, max_urls,
                                              start_urls,
                                              monkeypatch):
        #TODO: посмотреть как мокать на aiohttp
        #TODO: тесты доделать

        async def mock_get_html_content(_, url):
            if url not in html_constants.TEST_RESPONSE:
                raise aiohttp.ClientResponseError(history=None, request_info=None, status=404)
            html_content = html_constants.TEST_RESPONSE[url]["html_content"]
            if html_content == 'error':
                raise aiohttp.ClientResponseError(history=None, request_info=None, status=404)
            return html_content

        monkeypatch.setattr("src.crawler.WebCrawler._get_html_content",
                            mock_get_html_content, raising=True)
        async with ImageCrawler(max_depth=max_depth, max_urls=max_urls,
                                start_urls=start_urls,
                                check_robots_txt=False) as crawler:
            await crawler.run()
        self._check_only_image()

    def _check_only_image(self):
        assert os.path.exists('image_data.json')
        IMG_FORMAT = {'.png', '.jpg'}
        with open("image_data.json", 'r') as file:
            data = json.load(file)
        for url in data:
            for link in data[url]:
                _, file_extension = os.path.splitext(link)
                assert file_extension in IMG_FORMAT