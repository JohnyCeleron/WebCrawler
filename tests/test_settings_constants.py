import pytest
import random
from src.settings_constants import SettingConstants


class TestAssertionError:

    @pytest.mark.parametrize("constant_name", [
        'MAX_SIZE_QUEUE', 'TIMEOUT_CONNECTION', 'CONSUMERS_COUNT',
        'MAX_NEXT_URLS', 'NODE_SIZE', 'START_NODE_SIZE'
    ])
    def test_invalid_non_positive(self, constant_name):
        constant_non_positive_value = random.randint(-100, 0)
        with pytest.raises(AssertionError) as exc_info:
            constant_dict = {constant_name: constant_non_positive_value}
            SettingConstants(**constant_dict)
        assert str(exc_info.value) == f'{constant_name} must be positive'

    @pytest.mark.parametrize("value", [-100, 0.35, 100, 4.5])
    def test_invalid_arrow_head(self, value):
        with pytest.raises(AssertionError) as exc_info:
            SettingConstants(ARROW_HEAD=value)
        assert str(
            exc_info.value) == 'ARROW_HEAD must be integer in range from 0 to 8'

    def test_invalid_arrow_size(self):
        value = random.uniform(-100, 0.2)
        with pytest.raises(AssertionError) as exc_info:
            SettingConstants(ARROW_SIZE=value)
        assert str(
            exc_info.value) == 'ARROW_SIZE must be great or equal than 0.3'

    def test_invalid_arrow_width(self):
        value = random.uniform(-100, 0)
        with pytest.raises(AssertionError) as exc_info:
            SettingConstants(ARROW_WIDTH=value)
        assert str(
            exc_info.value) == 'ARROW_WIDTH must be great or equal than 0.1'
