from unittest.mock import patch
from unittest.mock import Mock

from wazimap_ng.datasets.models import Indicator
# import pytest.mark.django_db
import pytest


class TestIndicator:
    # def setup_method(self):
    #     self.good_input = [
    #         {"geography": "XXX", "count": 111},
    #         {"geography": "YYY", "count": 222},
    #     ]

    # @pytest.mark.django_db
    @patch("wazimap_ng.datasets.models.indicator.super")
    @patch("wazimap_ng.datasets.models.Indicator.get_unique_subindicators")
    def test_first_save(self, mock_get_unique_subindicators, mock_super):
        indicator = Indicator()
        mock_get_unique_subindicators.return_value = "first"

        indicator.save()

        assert indicator.subindicators == "first"

    @patch("wazimap_ng.datasets.models.indicator.super")
    @patch("wazimap_ng.datasets.models.Indicator.get_unique_subindicators")
    def test_second_save(self, mock_get_unique_subindicators, mock_super):
        indicator = Indicator()
        indicator.subindicators = "second"
        mock_get_unique_subindicators.return_value = "first"

        indicator.save()

        assert indicator.subindicators == "second"

    @patch("wazimap_ng.datasets.models.indicator.super")
    @patch("wazimap_ng.datasets.models.Indicator.get_unique_subindicators")
    def test_force_update(self, mock_get_unique_subindicators, mock_super):
        indicator = Indicator()
        indicator.subindicators = "existing subindicators"
        mock_get_unique_subindicators.return_value = "new subindicators"

        indicator.save(force_subindicator_update=True)

        assert indicator.subindicators == "new subindicators"
