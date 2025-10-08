"""Shared pytest fixtures and configuration for the test suite."""

import pytest
from aggregator.models.data_models import Volume5mItem, Volume5m


@pytest.fixture
def sample_volume_5m_item():
    """Fixture providing a sample Volume5mItem."""
    return Volume5mItem(
        avgHighPrice=1000, highPriceVolume=100, avgLowPrice=900, lowPriceVolume=120
    )


@pytest.fixture
def sample_volume_5m_data():
    """Fixture providing sample Volume5m data with multiple items."""
    return Volume5m(
        data={
            "1": Volume5mItem(
                avgHighPrice=100, highPriceVolume=1000, avgLowPrice=90, lowPriceVolume=1200
            ),
            "2": Volume5mItem(
                avgHighPrice=200, highPriceVolume=2000, avgLowPrice=180, lowPriceVolume=2400
            ),
            "3": Volume5mItem(
                avgHighPrice=300, highPriceVolume=3000, avgLowPrice=270, lowPriceVolume=3600
            ),
        }
    )


@pytest.fixture
def sample_items_with_none():
    """Fixture providing Volume5mItem list with None values."""
    return [
        Volume5mItem(avgHighPrice=100),
        Volume5mItem(avgHighPrice=None),
        Volume5mItem(avgHighPrice=200),
        Volume5mItem(avgHighPrice=None),
        Volume5mItem(avgHighPrice=300),
    ]
