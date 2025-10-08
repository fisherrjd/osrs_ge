import pytest
from aggregator.util.averages import get_average_field
from aggregator.models.data_models import Volume5mItem, Volume5m


class TestGetAverageField:
    """Test the get_average_field function for calculating averages."""

    def test_basic_average_calculation(self):
        """Test basic average calculation with valid values."""
        items = [
            Volume5mItem(avgHighPrice=100),
            Volume5mItem(avgHighPrice=200),
            Volume5mItem(avgHighPrice=300),
        ]
        result = get_average_field(items, "avgHighPrice")
        assert result == 200.0

    def test_single_item(self):
        """Test average with a single item."""
        items = [Volume5mItem(avgHighPrice=150)]
        result = get_average_field(items, "avgHighPrice")
        assert result == 150.0

    def test_all_none_values(self):
        """Test when all values are None."""
        items = [
            Volume5mItem(avgHighPrice=None),
            Volume5mItem(avgHighPrice=None),
            Volume5mItem(avgHighPrice=None),
        ]
        result = get_average_field(items, "avgHighPrice")
        assert result is None

    def test_empty_list(self):
        """Test with an empty list."""
        items = []
        result = get_average_field(items, "avgHighPrice")
        assert result is None

    def test_mixed_none_and_valid_values(self):
        """Test with mix of None and valid values."""
        items = [
            Volume5mItem(avgHighPrice=100),
            Volume5mItem(avgHighPrice=None),
            Volume5mItem(avgHighPrice=200),
            Volume5mItem(avgHighPrice=None),
            Volume5mItem(avgHighPrice=300),
        ]
        result = get_average_field(items, "avgHighPrice")
        # Average of 100, 200, 300 = 600 / 3 = 200
        assert result == 200.0

    def test_avg_low_price_field(self):
        """Test with avgLowPrice field."""
        items = [
            Volume5mItem(avgLowPrice=50),
            Volume5mItem(avgLowPrice=100),
            Volume5mItem(avgLowPrice=150),
        ]
        result = get_average_field(items, "avgLowPrice")
        assert result == 100.0

    def test_high_price_volume_field(self):
        """Test with highPriceVolume field."""
        items = [
            Volume5mItem(highPriceVolume=1000),
            Volume5mItem(highPriceVolume=2000),
            Volume5mItem(highPriceVolume=3000),
        ]
        result = get_average_field(items, "highPriceVolume")
        assert result == 2000.0

    def test_low_price_volume_field(self):
        """Test with lowPriceVolume field."""
        items = [
            Volume5mItem(lowPriceVolume=500),
            Volume5mItem(lowPriceVolume=1500),
        ]
        result = get_average_field(items, "lowPriceVolume")
        assert result == 1000.0

    def test_zero_values(self):
        """Test with zero values (which are valid, not None)."""
        items = [
            Volume5mItem(avgHighPrice=0),
            Volume5mItem(avgHighPrice=0),
            Volume5mItem(avgHighPrice=0),
        ]
        result = get_average_field(items, "avgHighPrice")
        assert result == 0.0

    def test_mix_of_zero_and_positive(self):
        """Test with mix of zero and positive values."""
        items = [
            Volume5mItem(avgHighPrice=0),
            Volume5mItem(avgHighPrice=100),
            Volume5mItem(avgHighPrice=200),
        ]
        result = get_average_field(items, "avgHighPrice")
        # Average of 0, 100, 200 = 300 / 3 = 100
        assert result == 100.0

    def test_nonexistent_field(self):
        """Test with a field that doesn't exist on the model."""
        items = [
            Volume5mItem(avgHighPrice=100),
            Volume5mItem(avgHighPrice=200),
        ]
        result = get_average_field(items, "nonexistent_field")
        # Should return None as no items have this field
        assert result is None

    def test_large_numbers(self):
        """Test with large numbers."""
        items = [
            Volume5mItem(avgHighPrice=1_000_000_000),
            Volume5mItem(avgHighPrice=2_000_000_000),
            Volume5mItem(avgHighPrice=3_000_000_000),
        ]
        result = get_average_field(items, "avgHighPrice")
        assert result == 2_000_000_000.0

    def test_floating_point_precision(self):
        """Test that average handles floating point correctly."""
        items = [
            Volume5mItem(avgHighPrice=100),
            Volume5mItem(avgHighPrice=200),
            Volume5mItem(avgHighPrice=201),
        ]
        result = get_average_field(items, "avgHighPrice")
        # Average of 100, 200, 201 = 501 / 3 = 167.0
        assert result == pytest.approx(167.0)

    def test_single_none_in_list(self):
        """Test with a single None value in list."""
        items = [Volume5mItem(avgHighPrice=None)]
        result = get_average_field(items, "avgHighPrice")
        assert result is None

    def test_mix_with_default_zeros(self):
        """Test with items that have default zero values for volumes."""
        items = [
            Volume5mItem(highPriceVolume=0),  # Default value
            Volume5mItem(highPriceVolume=1000),
            Volume5mItem(highPriceVolume=2000),
        ]
        result = get_average_field(items, "highPriceVolume")
        # Average of 0, 1000, 2000 = 3000 / 3 = 1000
        assert result == 1000.0

    def test_all_same_values(self):
        """Test when all values are the same."""
        items = [
            Volume5mItem(avgHighPrice=500),
            Volume5mItem(avgHighPrice=500),
            Volume5mItem(avgHighPrice=500),
        ]
        result = get_average_field(items, "avgHighPrice")
        assert result == 500.0

    def test_two_items_average(self):
        """Test average of exactly two items."""
        items = [
            Volume5mItem(avgHighPrice=100),
            Volume5mItem(avgHighPrice=200),
        ]
        result = get_average_field(items, "avgHighPrice")
        assert result == 150.0

    def test_negative_values(self):
        """Test with negative values (edge case, unlikely in practice)."""
        items = [
            Volume5mItem(avgHighPrice=-100),
            Volume5mItem(avgHighPrice=-200),
            Volume5mItem(avgHighPrice=-300),
        ]
        result = get_average_field(items, "avgHighPrice")
        assert result == -200.0

    def test_very_large_list(self):
        """Test with a large number of items."""
        items = [Volume5mItem(avgHighPrice=100) for _ in range(1000)]
        result = get_average_field(items, "avgHighPrice")
        assert result == 100.0

    def test_odd_number_average(self):
        """Test average calculation with odd number of items."""
        items = [
            Volume5mItem(avgHighPrice=10),
            Volume5mItem(avgHighPrice=20),
            Volume5mItem(avgHighPrice=30),
            Volume5mItem(avgHighPrice=40),
            Volume5mItem(avgHighPrice=50),
        ]
        result = get_average_field(items, "avgHighPrice")
        # Average = 150 / 5 = 30
        assert result == 30.0

    def test_mostly_none_with_one_value(self):
        """Test with mostly None values and one valid value."""
        items = [
            Volume5mItem(avgHighPrice=None),
            Volume5mItem(avgHighPrice=None),
            Volume5mItem(avgHighPrice=None),
            Volume5mItem(avgHighPrice=100),
            Volume5mItem(avgHighPrice=None),
        ]
        result = get_average_field(items, "avgHighPrice")
        assert result == 100.0


class TestGetAverageFieldWithVolume5m:
    """Test get_average_field with Volume5m objects (as used in properties)."""

    def test_volume5m_avg_high_price(self):
        """Test average high price calculation with Volume5m object."""
        volume_data = Volume5m(
            data={
                "1": Volume5mItem(avgHighPrice=100),
                "2": Volume5mItem(avgHighPrice=200),
                "3": Volume5mItem(avgHighPrice=300),
            }
        )
        result = get_average_field(volume_data, "avgHighPrice")
        assert result == 200.0

    def test_volume5m_avg_high_volume(self):
        """Test average high volume calculation with Volume5m object."""
        volume_data = Volume5m(
            data={
                "1": Volume5mItem(highPriceVolume=1000),
                "2": Volume5mItem(highPriceVolume=2000),
                "3": Volume5mItem(highPriceVolume=3000),
            }
        )
        result = get_average_field(volume_data, "highPriceVolume")
        assert result == 2000.0

    def test_volume5m_avg_low_price(self):
        """Test average low price calculation with Volume5m object."""
        volume_data = Volume5m(
            data={
                "1": Volume5mItem(avgLowPrice=50),
                "2": Volume5mItem(avgLowPrice=100),
                "3": Volume5mItem(avgLowPrice=150),
            }
        )
        result = get_average_field(volume_data, "avgLowPrice")
        assert result == 100.0

    def test_volume5m_avg_low_volume(self):
        """Test average low volume calculation with Volume5m object."""
        volume_data = Volume5m(
            data={
                "1": Volume5mItem(lowPriceVolume=500),
                "2": Volume5mItem(lowPriceVolume=1000),
                "3": Volume5mItem(lowPriceVolume=1500),
            }
        )
        result = get_average_field(volume_data, "lowPriceVolume")
        assert result == 1000.0

    def test_volume5m_with_none_values(self):
        """Test Volume5m with some None values."""
        volume_data = Volume5m(
            data={
                "1": Volume5mItem(avgHighPrice=100),
                "2": Volume5mItem(avgHighPrice=None),
                "3": Volume5mItem(avgHighPrice=300),
            }
        )
        result = get_average_field(volume_data, "avgHighPrice")
        assert result == 200.0

    def test_volume5m_all_none_values(self):
        """Test Volume5m with all None values."""
        volume_data = Volume5m(
            data={
                "1": Volume5mItem(avgHighPrice=None),
                "2": Volume5mItem(avgHighPrice=None),
                "3": Volume5mItem(avgHighPrice=None),
            }
        )
        result = get_average_field(volume_data, "avgHighPrice")
        assert result is None

    def test_volume5m_empty_data(self):
        """Test Volume5m with empty data."""
        volume_data = Volume5m(data={})
        result = get_average_field(volume_data, "avgHighPrice")
        assert result is None

    def test_volume5m_single_item(self):
        """Test Volume5m with single item."""
        volume_data = Volume5m(
            data={"1": Volume5mItem(avgHighPrice=1000)}
        )
        result = get_average_field(volume_data, "avgHighPrice")
        assert result == 1000.0

    def test_volume5m_property_integration(self):
        """Test that Volume5m properties work correctly."""
        volume_data = Volume5m(
            data={
                "1": Volume5mItem(
                    avgHighPrice=100,
                    highPriceVolume=1000,
                    avgLowPrice=90,
                    lowPriceVolume=1200,
                ),
                "2": Volume5mItem(
                    avgHighPrice=200,
                    highPriceVolume=2000,
                    avgLowPrice=180,
                    lowPriceVolume=2400,
                ),
            }
        )
        assert volume_data.avg_high_price == 150.0
        assert volume_data.avg_high_volume == 1500.0
        assert volume_data.avg_low_price == 135.0
        assert volume_data.avg_low_volume == 1800.0
