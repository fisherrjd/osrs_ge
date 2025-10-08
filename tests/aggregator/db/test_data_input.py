import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from aggregator.db.data_input import (
    fetch_data,
    mapping_wrapper,
    latest_wrapper,
    volume_wrapper,
    volume5m_wrapper,
    fetch_all_data,
    update_database,
    save_volume5m_to_db,
)
from aggregator.models.data_models import (
    MappingData,
    MappingList,
    LatestData,
    Volume24h,
    Volume5m,
    Volume5mItem,
    ItemData,
)
from aggregator.models.item_model import Item
from aggregator.models.item_volume_5m import ItemSnapshot


class TestFetchData:
    """Test the fetch_data function."""

    @patch("aggregator.db.data_input.requests.get")
    def test_successful_fetch(self, mock_get):
        """Test successful data fetch."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        result = fetch_data("http://test.com/api")

        assert result == {"data": "test"}
        mock_get.assert_called_once()

    @patch("aggregator.db.data_input.requests.get")
    def test_fetch_with_headers(self, mock_get):
        """Test that headers are sent with the request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        fetch_data("http://test.com/api")

        # Verify headers were passed
        call_args = mock_get.call_args
        assert "headers" in call_args.kwargs

    @patch("aggregator.db.data_input.requests.get")
    def test_fetch_failure_404(self, mock_get):
        """Test fetch with 404 error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="Failed to fetch data: 404"):
            fetch_data("http://test.com/api")

    @patch("aggregator.db.data_input.requests.get")
    def test_fetch_failure_500(self, mock_get):
        """Test fetch with 500 error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="Failed to fetch data: 500"):
            fetch_data("http://test.com/api")

    @patch("aggregator.db.data_input.requests.get")
    def test_fetch_with_empty_response(self, mock_get):
        """Test fetch with empty JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        result = fetch_data("http://test.com/api")
        assert result == {}

    @patch("aggregator.db.data_input.requests.get")
    def test_fetch_with_complex_data(self, mock_get):
        """Test fetch with complex nested JSON data."""
        complex_data = {
            "items": [{"id": 1, "name": "test"}],
            "meta": {"count": 1},
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = complex_data
        mock_get.return_value = mock_response

        result = fetch_data("http://test.com/api")
        assert result == complex_data


class TestMappingWrapper:
    """Test the mapping_wrapper function."""

    @patch("aggregator.db.data_input.fetch_data")
    def test_mapping_wrapper_success(self, mock_fetch):
        """Test successful mapping data retrieval."""
        mock_fetch.return_value = [
            {
                "examine": "A shiny sword",
                "id": 1,
                "members": True,
                "lowalch": 100,
                "highalch": 150,
                "limit": 10,
                "value": 200,
                "icon": "sword.png",
                "name": "Sword",
            }
        ]

        result = mapping_wrapper()

        assert isinstance(result, MappingList)
        assert len(result.items) == 1
        assert result.items[0].id == 1
        assert result.items[0].name == "Sword"

    @patch("aggregator.db.data_input.fetch_data")
    def test_mapping_wrapper_multiple_items(self, mock_fetch):
        """Test mapping wrapper with multiple items."""
        mock_fetch.return_value = [
            {"examine": "Item 1", "id": 1, "members": False, "name": "Item1"},
            {"examine": "Item 2", "id": 2, "members": True, "name": "Item2"},
            {"examine": "Item 3", "id": 3, "members": False, "name": "Item3"},
        ]

        result = mapping_wrapper()

        assert len(result.items) == 3
        assert result.items[0].id == 1
        assert result.items[1].id == 2
        assert result.items[2].id == 3

    @patch("aggregator.db.data_input.fetch_data")
    def test_mapping_wrapper_empty_list(self, mock_fetch):
        """Test mapping wrapper with empty data."""
        mock_fetch.return_value = []

        result = mapping_wrapper()

        assert isinstance(result, MappingList)
        assert len(result.items) == 0


class TestLatestWrapper:
    """Test the latest_wrapper function."""

    @patch("aggregator.db.data_input.fetch_data")
    def test_latest_wrapper_success(self, mock_fetch):
        """Test successful latest price data retrieval."""
        mock_fetch.return_value = {
            "data": {
                1: {"high": 1000, "highTime": 123, "low": 900, "lowTime": 124}
            }
        }

        result = latest_wrapper()

        assert isinstance(result, LatestData)
        assert 1 in result.data
        assert result.data[1].high == 1000
        assert result.data[1].low == 900

    @patch("aggregator.db.data_input.fetch_data")
    def test_latest_wrapper_multiple_items(self, mock_fetch):
        """Test latest wrapper with multiple items."""
        mock_fetch.return_value = {
            "data": {
                1: {"high": 100, "low": 90},
                2: {"high": 200, "low": 180},
                3: {"high": 300, "low": 270},
            }
        }

        result = latest_wrapper()

        assert len(result.data) == 3
        assert result.data[1].high == 100
        assert result.data[2].high == 200

    @patch("aggregator.db.data_input.fetch_data")
    def test_latest_wrapper_empty_data(self, mock_fetch):
        """Test latest wrapper with empty data."""
        mock_fetch.return_value = {"data": {}}

        result = latest_wrapper()

        assert isinstance(result, LatestData)
        assert len(result.data) == 0


class TestVolumeWrapper:
    """Test the volume_wrapper function."""

    @patch("aggregator.db.data_input.fetch_data")
    def test_volume_wrapper_success(self, mock_fetch):
        """Test successful volume data retrieval."""
        mock_fetch.return_value = {
            "timestamp": 1234567890,
            "data": {"1": 100, "2": 200},
        }

        result = volume_wrapper()

        assert isinstance(result, Volume24h)
        assert result.timestamp == 1234567890
        assert result.data["1"] == 100
        assert result.data["2"] == 200

    @patch("aggregator.db.data_input.fetch_data")
    def test_volume_wrapper_with_none_values(self, mock_fetch):
        """Test volume wrapper with None values."""
        mock_fetch.return_value = {
            "timestamp": 123,
            "data": {"1": 100, "2": None, "3": 300},
        }

        result = volume_wrapper()

        assert result.data["1"] == 100
        assert result.data["2"] is None
        assert result.data["3"] == 300


class TestVolume5mWrapper:
    """Test the volume5m_wrapper function."""

    @patch("aggregator.db.data_input.fetch_data")
    def test_volume5m_wrapper_success(self, mock_fetch):
        """Test successful 5m volume data retrieval."""
        mock_fetch.return_value = {
            "data": {
                "1": {
                    "avgHighPrice": 100,
                    "highPriceVolume": 1000,
                    "avgLowPrice": 90,
                    "lowPriceVolume": 1200,
                }
            }
        }

        result = volume5m_wrapper()

        assert isinstance(result, Volume5m)
        assert "1" in result.data
        assert result.data["1"].avgHighPrice == 100
        assert result.data["1"].avgLowPrice == 90

    @patch("aggregator.db.data_input.fetch_data")
    def test_volume5m_wrapper_multiple_items(self, mock_fetch):
        """Test volume5m wrapper with multiple items."""
        mock_fetch.return_value = {
            "data": {
                "1": {"avgHighPrice": 100, "avgLowPrice": 90},
                "2": {"avgHighPrice": 200, "avgLowPrice": 180},
                "3": {"avgHighPrice": 300, "avgLowPrice": 270},
            }
        }

        result = volume5m_wrapper()

        assert len(result.data) == 3
        assert result.data["1"].avgHighPrice == 100
        assert result.data["2"].avgHighPrice == 200


class TestFetchAllData:
    """Test the fetch_all_data function."""

    @patch("aggregator.db.data_input.volume5m_wrapper")
    @patch("aggregator.db.data_input.volume_wrapper")
    @patch("aggregator.db.data_input.latest_wrapper")
    @patch("aggregator.db.data_input.mapping_wrapper")
    def test_fetch_all_data_success(
        self, mock_mapping, mock_latest, mock_volume, mock_volume5m
    ):
        """Test successful fetching of all data."""
        mock_mapping.return_value = MappingList(items=[])
        mock_latest.return_value = LatestData(data={})
        mock_volume.return_value = Volume24h(data={})
        mock_volume5m.return_value = Volume5m(data={})

        mapping, latest, volume, volume5m = fetch_all_data()

        assert isinstance(mapping, MappingList)
        assert isinstance(latest, LatestData)
        assert isinstance(volume, Volume24h)
        assert isinstance(volume5m, Volume5m)
        mock_mapping.assert_called_once()
        mock_latest.assert_called_once()
        mock_volume.assert_called_once()
        mock_volume5m.assert_called_once()

    @patch("aggregator.db.data_input.volume5m_wrapper")
    @patch("aggregator.db.data_input.volume_wrapper")
    @patch("aggregator.db.data_input.latest_wrapper")
    @patch("aggregator.db.data_input.mapping_wrapper")
    def test_fetch_all_data_returns_tuple(
        self, mock_mapping, mock_latest, mock_volume, mock_volume5m
    ):
        """Test that fetch_all_data returns a tuple of 4 elements."""
        mock_mapping.return_value = MappingList(items=[])
        mock_latest.return_value = LatestData(data={})
        mock_volume.return_value = Volume24h(data={})
        mock_volume5m.return_value = Volume5m(data={})

        result = fetch_all_data()

        assert isinstance(result, tuple)
        assert len(result) == 4


class TestUpdateDatabase:
    """Test the update_database function."""

    def test_update_database_returns_function(self):
        """Test that update_database returns a function."""
        latest_data = LatestData(data={})
        mapping_data = MappingList(items=[])
        volume_data = Volume24h(data={})

        result = update_database(latest_data, mapping_data, volume_data)

        assert callable(result)

    @patch("aggregator.db.data_input.session")
    def test_update_database_inner_function(self, mock_session):
        """Test the inner function returned by update_database."""
        # Create test data
        mapping_data = MappingList(
            items=[
                MappingData(
                    examine="Test item",
                    id=1,
                    members=True,
                    lowalch=100,
                    highalch=150,
                    limit=10,
                    value=200,
                    icon="icon.png",
                    name="Test Item",
                )
            ]
        )
        latest_data = LatestData(
            data={
                1: ItemData(high=1000, highTime=123, low=900, lowTime=124)
            }
        )
        volume_data = Volume24h(data={"1": 50})

        # Get the inner function
        update_func = update_database(latest_data, mapping_data, volume_data)

        # Mock session methods
        mock_session.merge = MagicMock()
        mock_session.commit = MagicMock()

        # Call the inner function
        update_func(latest_data, mapping_data, volume_data)

        # Verify session methods were called
        mock_session.merge.assert_called()
        mock_session.commit.assert_called_once()

    @patch("aggregator.db.data_input.session")
    def test_update_database_skips_unmapped_items(self, mock_session):
        """Test that items not in mapping are skipped."""
        mapping_data = MappingList(
            items=[
                MappingData(
                    examine="Test", id=1, members=True, name="Item1"
                )
            ]
        )
        # Latest data has item 2 which is not in mapping
        latest_data = LatestData(
            data={
                2: ItemData(high=1000, low=900)
            }
        )
        volume_data = Volume24h(data={})

        update_func = update_database(latest_data, mapping_data, volume_data)

        mock_session.merge = MagicMock()
        mock_session.commit = MagicMock()

        update_func(latest_data, mapping_data, volume_data)

        # merge should not be called since item 2 is not in mapping
        mock_session.merge.assert_not_called()
        mock_session.commit.assert_called_once()

    @patch("aggregator.db.data_input.session")
    def test_update_database_with_missing_volume(self, mock_session):
        """Test update with missing volume data for an item."""
        mapping_data = MappingList(
            items=[
                MappingData(
                    examine="Test", id=1, members=True, name="Item1"
                )
            ]
        )
        latest_data = LatestData(
            data={1: ItemData(high=1000, low=900)}
        )
        # Volume data doesn't have item 1
        volume_data = Volume24h(data={"2": 50})

        update_func = update_database(latest_data, mapping_data, volume_data)

        mock_session.merge = MagicMock()
        mock_session.commit = MagicMock()

        update_func(latest_data, mapping_data, volume_data)

        # Should still merge the item with volume defaulting to 0
        mock_session.merge.assert_called()
        mock_session.commit.assert_called_once()


class TestSaveVolume5mToDb:
    """Test the save_volume5m_to_db function."""

    @patch("aggregator.db.data_input.Session")
    def test_save_volume5m_single_item(self, mock_session_class):
        """Test saving single item's 5m volume data."""
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        volume_data = Volume5m(
            data={
                "1": Volume5mItem(
                    avgHighPrice=100,
                    highPriceVolume=1000,
                    avgLowPrice=90,
                    lowPriceVolume=1200,
                )
            }
        )
        mock_engine = Mock()

        save_volume5m_to_db(volume_data, mock_engine)

        # Verify session was created with engine
        mock_session_class.assert_called_once_with(mock_engine)
        # Verify add and commit were called
        mock_session.add.assert_called()
        mock_session.commit.assert_called_once()

    @patch("aggregator.db.data_input.Session")
    def test_save_volume5m_multiple_items(self, mock_session_class):
        """Test saving multiple items' 5m volume data."""
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        volume_data = Volume5m(
            data={
                "1": Volume5mItem(avgHighPrice=100, highPriceVolume=1000),
                "2": Volume5mItem(avgHighPrice=200, highPriceVolume=2000),
                "3": Volume5mItem(avgHighPrice=300, highPriceVolume=3000),
            }
        )
        mock_engine = Mock()

        save_volume5m_to_db(volume_data, mock_engine)

        # add should be called 3 times (once per item)
        assert mock_session.add.call_count == 3
        mock_session.commit.assert_called_once()

    @patch("aggregator.db.data_input.Session")
    def test_save_volume5m_calculates_total_volume(self, mock_session_class):
        """Test that total volume is calculated correctly."""
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        volume_data = Volume5m(
            data={
                "1": Volume5mItem(
                    highPriceVolume=5000,
                    lowPriceVolume=7000,
                )
            }
        )
        mock_engine = Mock()

        save_volume5m_to_db(volume_data, mock_engine)

        # Get the ItemSnapshot that was added
        call_args = mock_session.add.call_args
        snapshot = call_args[0][0]

        assert isinstance(snapshot, ItemSnapshot)
        assert snapshot.total_volume == 12000  # 5000 + 7000

    @patch("aggregator.db.data_input.Session")
    def test_save_volume5m_handles_none_volumes(self, mock_session_class):
        """Test handling of None volume values."""
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        volume_data = Volume5m(
            data={
                "1": Volume5mItem(
                    avgHighPrice=100,
                    highPriceVolume=None,
                    avgLowPrice=90,
                    lowPriceVolume=None,
                )
            }
        )
        mock_engine = Mock()

        save_volume5m_to_db(volume_data, mock_engine)

        # Get the ItemSnapshot that was added
        call_args = mock_session.add.call_args
        snapshot = call_args[0][0]

        # None volumes should default to 0
        assert snapshot.total_volume == 0

    @patch("aggregator.db.data_input.Session")
    def test_save_volume5m_sets_timestamp(self, mock_session_class):
        """Test that timestamp is set for snapshots."""
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        volume_data = Volume5m(
            data={"1": Volume5mItem(avgHighPrice=100)}
        )
        mock_engine = Mock()

        before_time = datetime.now(timezone.utc)
        save_volume5m_to_db(volume_data, mock_engine)
        after_time = datetime.now(timezone.utc)

        # Get the ItemSnapshot that was added
        call_args = mock_session.add.call_args
        snapshot = call_args[0][0]

        # Timestamp should be between before and after
        assert before_time <= snapshot.timestamp <= after_time

    @patch("aggregator.db.data_input.Session")
    def test_save_volume5m_converts_item_id_to_int(self, mock_session_class):
        """Test that item_id is converted from string to int."""
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        volume_data = Volume5m(
            data={"12345": Volume5mItem(avgHighPrice=100)}
        )
        mock_engine = Mock()

        save_volume5m_to_db(volume_data, mock_engine)

        # Get the ItemSnapshot that was added
        call_args = mock_session.add.call_args
        snapshot = call_args[0][0]

        assert snapshot.item_id == 12345
        assert isinstance(snapshot.item_id, int)

    @patch("aggregator.db.data_input.Session")
    def test_save_volume5m_empty_data(self, mock_session_class):
        """Test saving with empty volume data."""
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        volume_data = Volume5m(data={})
        mock_engine = Mock()

        save_volume5m_to_db(volume_data, mock_engine)

        # add should not be called
        mock_session.add.assert_not_called()
        # commit should still be called
        mock_session.commit.assert_called_once()

    @patch("aggregator.db.data_input.Session")
    def test_save_volume5m_preserves_all_fields(self, mock_session_class):
        """Test that all fields are preserved when saving."""
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        volume_data = Volume5m(
            data={
                "554": Volume5mItem(
                    avgHighPrice=5,
                    highPriceVolume=150000,
                    avgLowPrice=4,
                    lowPriceVolume=180000,
                )
            }
        )
        mock_engine = Mock()

        save_volume5m_to_db(volume_data, mock_engine)

        call_args = mock_session.add.call_args
        snapshot = call_args[0][0]

        assert snapshot.item_id == 554
        assert snapshot.avg_high_price == 5
        assert snapshot.high_price_volume == 150000
        assert snapshot.avg_low_price == 4
        assert snapshot.low_price_volume == 180000
        assert snapshot.total_volume == 330000
