import pytest
from aggregator.models.data_models import (
    MappingData,
    MappingList,
    ItemData,
    LatestData,
    Volume24h,
    Volume5mItem,
    Volume5m,
)


class TestMappingData:
    """Test MappingData model."""

    def test_create_with_all_fields(self):
        """Test creating MappingData with all fields."""
        data = MappingData(
            examine="A shiny sword",
            id=1234,
            members=True,
            lowalch=100,
            highalch=150,
            limit=10,
            value=200,
            icon="icon.png",
            name="Shiny Sword",
        )
        assert data.examine == "A shiny sword"
        assert data.id == 1234
        assert data.members is True
        assert data.lowalch == 100
        assert data.highalch == 150
        assert data.limit == 10
        assert data.value == 200
        assert data.icon == "icon.png"
        assert data.name == "Shiny Sword"

    def test_create_with_defaults(self):
        """Test creating MappingData with default values."""
        data = MappingData(examine="Test item", id=1, members=False, name="Test")
        assert data.lowalch == 0
        assert data.highalch == 0
        assert data.limit == 0
        assert data.value == 0
        assert data.icon == ""

    def test_free_to_play_item(self):
        """Test free-to-play item."""
        data = MappingData(
            examine="A basic item", id=1, members=False, name="Bronze sword"
        )
        assert data.members is False

    def test_members_item(self):
        """Test members-only item."""
        data = MappingData(
            examine="A rare item", id=1, members=True, name="Dragon scimitar"
        )
        assert data.members is True


class TestMappingList:
    """Test MappingList model."""

    def test_empty_list(self):
        """Test creating empty MappingList."""
        mapping_list = MappingList(items=[])
        assert len(mapping_list.items) == 0

    def test_single_item(self):
        """Test MappingList with single item."""
        item = MappingData(examine="Test", id=1, members=False, name="Test Item")
        mapping_list = MappingList(items=[item])
        assert len(mapping_list.items) == 1
        assert mapping_list.items[0].name == "Test Item"

    def test_multiple_items(self):
        """Test MappingList with multiple items."""
        items = [
            MappingData(examine="Item 1", id=1, members=False, name="Item 1"),
            MappingData(examine="Item 2", id=2, members=True, name="Item 2"),
            MappingData(examine="Item 3", id=3, members=False, name="Item 3"),
        ]
        mapping_list = MappingList(items=items)
        assert len(mapping_list.items) == 3


class TestItemData:
    """Test ItemData model."""

    def test_all_fields_present(self):
        """Test ItemData with all fields."""
        data = ItemData(high=1000, highTime=1234567890, low=900, lowTime=1234567891)
        assert data.high == 1000
        assert data.highTime == 1234567890
        assert data.low == 900
        assert data.lowTime == 1234567891

    def test_all_fields_none(self):
        """Test ItemData with all None values."""
        data = ItemData()
        assert data.high is None
        assert data.highTime is None
        assert data.low is None
        assert data.lowTime is None

    def test_partial_data(self):
        """Test ItemData with some fields set."""
        data = ItemData(high=1000, low=900)
        assert data.high == 1000
        assert data.low == 900
        assert data.highTime is None
        assert data.lowTime is None


class TestLatestData:
    """Test LatestData model."""

    def test_empty_data(self):
        """Test LatestData with empty dictionary."""
        data = LatestData(data={})
        assert len(data.data) == 0

    def test_single_item(self):
        """Test LatestData with single item."""
        item_data = ItemData(high=1000, low=900)
        data = LatestData(data={1234: item_data})
        assert 1234 in data.data
        assert data.data[1234].high == 1000

    def test_multiple_items(self):
        """Test LatestData with multiple items."""
        data = LatestData(
            data={
                1: ItemData(high=100, low=90),
                2: ItemData(high=200, low=180),
                3: ItemData(high=300, low=270),
            }
        )
        assert len(data.data) == 3
        assert data.data[1].high == 100
        assert data.data[2].high == 200
        assert data.data[3].high == 300


class TestVolume24h:
    """Test Volume24h model."""

    def test_with_timestamp_and_data(self):
        """Test Volume24h with timestamp and data."""
        data = Volume24h(timestamp=1234567890, data={"1": 100, "2": 200, "3": 300})
        assert data.timestamp == 1234567890
        assert data.data["1"] == 100
        assert data.data["2"] == 200

    def test_default_timestamp(self):
        """Test Volume24h with default timestamp."""
        data = Volume24h(data={"1": 100})
        assert data.timestamp == 0

    def test_none_values_in_data(self):
        """Test Volume24h with None values."""
        data = Volume24h(data={"1": 100, "2": None, "3": 300})
        assert data.data["1"] == 100
        assert data.data["2"] is None
        assert data.data["3"] == 300

    def test_empty_data_dict(self):
        """Test Volume24h with empty data."""
        data = Volume24h(timestamp=123456, data={})
        assert data.timestamp == 123456
        assert len(data.data) == 0


class TestVolume5mItem:
    """Test Volume5mItem model."""

    def test_all_fields_set(self):
        """Test Volume5mItem with all fields."""
        item = Volume5mItem(
            avgHighPrice=1000, highPriceVolume=50, avgLowPrice=900, lowPriceVolume=60
        )
        assert item.avgHighPrice == 1000
        assert item.highPriceVolume == 50
        assert item.avgLowPrice == 900
        assert item.lowPriceVolume == 60

    def test_default_values(self):
        """Test Volume5mItem default values."""
        item = Volume5mItem()
        assert item.avgHighPrice is None
        assert item.highPriceVolume == 0
        assert item.avgLowPrice is None
        assert item.lowPriceVolume == 0

    def test_partial_data(self):
        """Test Volume5mItem with partial data."""
        item = Volume5mItem(avgHighPrice=1000, highPriceVolume=50)
        assert item.avgHighPrice == 1000
        assert item.highPriceVolume == 50
        assert item.avgLowPrice is None
        assert item.lowPriceVolume == 0

    def test_zero_volumes(self):
        """Test Volume5mItem with zero volumes."""
        item = Volume5mItem(
            avgHighPrice=1000, highPriceVolume=0, avgLowPrice=900, lowPriceVolume=0
        )
        assert item.highPriceVolume == 0
        assert item.lowPriceVolume == 0


class TestVolume5m:
    """Test Volume5m model and its properties."""

    def test_avg_high_price_property(self):
        """Test avg_high_price property calculation."""
        data = Volume5m(
            data={
                "1": Volume5mItem(avgHighPrice=100),
                "2": Volume5mItem(avgHighPrice=200),
                "3": Volume5mItem(avgHighPrice=300),
            }
        )
        assert data.avg_high_price == 200.0

    def test_avg_high_volume_property(self):
        """Test avg_high_volume property calculation."""
        data = Volume5m(
            data={
                "1": Volume5mItem(highPriceVolume=1000),
                "2": Volume5mItem(highPriceVolume=2000),
                "3": Volume5mItem(highPriceVolume=3000),
            }
        )
        assert data.avg_high_volume == 2000.0

    def test_avg_low_price_property(self):
        """Test avg_low_price property calculation."""
        data = Volume5m(
            data={
                "1": Volume5mItem(avgLowPrice=50),
                "2": Volume5mItem(avgLowPrice=100),
                "3": Volume5mItem(avgLowPrice=150),
            }
        )
        assert data.avg_low_price == 100.0

    def test_avg_low_volume_property(self):
        """Test avg_low_volume property calculation."""
        data = Volume5m(
            data={
                "1": Volume5mItem(lowPriceVolume=500),
                "2": Volume5mItem(lowPriceVolume=1000),
                "3": Volume5mItem(lowPriceVolume=1500),
            }
        )
        assert data.avg_low_volume == 1000.0

    def test_empty_data(self):
        """Test Volume5m with empty data."""
        data = Volume5m(data={})
        assert data.avg_high_price is None
        assert data.avg_high_volume is None
        assert data.avg_low_price is None
        assert data.avg_low_volume is None

    def test_single_item(self):
        """Test Volume5m with single item."""
        data = Volume5m(
            data={
                "1": Volume5mItem(
                    avgHighPrice=1000,
                    highPriceVolume=100,
                    avgLowPrice=900,
                    lowPriceVolume=120,
                )
            }
        )
        assert data.avg_high_price == 1000.0
        assert data.avg_high_volume == 100.0
        assert data.avg_low_price == 900.0
        assert data.avg_low_volume == 120.0

    def test_mixed_none_values(self):
        """Test Volume5m properties with some None values."""
        data = Volume5m(
            data={
                "1": Volume5mItem(avgHighPrice=100),
                "2": Volume5mItem(avgHighPrice=None),
                "3": Volume5mItem(avgHighPrice=300),
            }
        )
        # Should average only the non-None values
        assert data.avg_high_price == 200.0

    def test_all_none_values(self):
        """Test Volume5m properties when all values are None."""
        data = Volume5m(
            data={
                "1": Volume5mItem(avgHighPrice=None),
                "2": Volume5mItem(avgHighPrice=None),
                "3": Volume5mItem(avgHighPrice=None),
            }
        )
        assert data.avg_high_price is None

    def test_realistic_scenario(self):
        """Test with realistic OSRS data scenario."""
        data = Volume5m(
            data={
                "554": Volume5mItem(  # Fire rune
                    avgHighPrice=5, highPriceVolume=10000, avgLowPrice=4, lowPriceVolume=12000
                ),
                "1215": Volume5mItem(  # Dragon dagger
                    avgHighPrice=17000,
                    highPriceVolume=50,
                    avgLowPrice=16500,
                    lowPriceVolume=60,
                ),
                "4151": Volume5mItem(  # Abyssal whip
                    avgHighPrice=2000000,
                    highPriceVolume=20,
                    avgLowPrice=1950000,
                    lowPriceVolume=25,
                ),
            }
        )
        # Average of 5, 17000, 2000000
        expected_avg_high = (5 + 17000 + 2000000) / 3
        assert data.avg_high_price == pytest.approx(expected_avg_high)

    def test_zero_volumes_included_in_average(self):
        """Test that zero volumes are included in average calculation."""
        data = Volume5m(
            data={
                "1": Volume5mItem(highPriceVolume=0),
                "2": Volume5mItem(highPriceVolume=1000),
                "3": Volume5mItem(highPriceVolume=2000),
            }
        )
        # Average should be (0 + 1000 + 2000) / 3 = 1000
        assert data.avg_high_volume == 1000.0
