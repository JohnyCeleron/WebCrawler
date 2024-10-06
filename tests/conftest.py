import html_constants
import pytest
from aioresponses import aioresponses


@pytest.fixture
def mock_urls():
    with aioresponses() as m:
        for url, response_data in html_constants.TEST_RESPONSE.items():
            status = response_data['status']
            html_content = response_data['html_content']
            m.get(url, body=html_content, status=status)
        yield m