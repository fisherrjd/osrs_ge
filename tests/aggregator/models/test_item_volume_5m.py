import pytest
from datetime import datetime, timezone
from aggregator.models.item_volume_5m import ItemSnapshot


class TestItemSnapshot:
    """Test the ItemSnapshot SQLModel."""

    def test_create_snapshot_with_all_fields(self):
        """Test creating ItemSnapshot with all fields specified."""
        timestamp = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        snapshot = ItemSnapshot(
            id=1,
            item_id=554,
            timestamp=timestamp,
            avg_high_price=5.5,
            high_price_volume=10000,
            avg_low_price=4.8,
            low_price_volume=12000,
            total_volume=22000,
        )
        assert snapshot.id == 1
        assert snapshot.item_id == 554
        assert snapshot.timestamp == timestamp
        assert snapshot.avg_high_price == 5.5
        assert snapshot.high_price_volume == 10000
        assert snapshot.avg_low_price == 4.8
        assert snapshot.low_price_volume == 12000
        assert snapshot.total_volume == 22000

    def test_create_snapshot_with_defaults(self):
        """Test creating ItemSnapshot with minimal required fields."""
        timestamp = datetime.now(timezone.utc)
        snapshot = ItemSnapshot(
            item_id=1234,
            timestamp=timestamp,
        )
        assert snapshot.id is None
        assert snapshot.item_id == 1234
        assert snapshot.timestamp == timestamp
        assert snapshot.avg_high_price is None
        assert snapshot.high_price_volume is None
        assert snapshot.avg_low_price is None
        assert snapshot.low_price_volume is None
        assert snapshot.total_volume is None

    def test_snapshot_without_id(self):
        """Test creating snapshot without ID (auto-generated)."""
        timestamp = datetime.now(timezone.utc)
        snapshot = ItemSnapshot(
            item_id=4151,
            timestamp=timestamp,
            avg_high_price=2000000.0,
            avg_low_price=1950000.0,
        )
        assert snapshot.id is None
        assert snapshot.item_id == 4151

    def test_snapshot_with_none_prices(self):
        """Test snapshot with None price values."""
        timestamp = datetime.now(timezone.utc)
        snapshot = ItemSnapshot(
            item_id=1,
            timestamp=timestamp,
            avg_high_price=None,
            avg_low_price=None,
        )
        assert snapshot.avg_high_price is None
        assert snapshot.avg_low_price is None

    def test_snapshot_with_zero_volumes(self):
        """Test snapshot with zero volume values."""
        timestamp = datetime.now(timezone.utc)
        snapshot = ItemSnapshot(
            item_id=1,
            timestamp=timestamp,
            high_price_volume=0,
            low_price_volume=0,
            total_volume=0,
        )
        assert snapshot.high_price_volume == 0
        assert snapshot.low_price_volume == 0
        assert snapshot.total_volume == 0

    def test_snapshot_with_float_prices(self):
        """Test snapshot with float price values."""
        timestamp = datetime.now(timezone.utc)
        snapshot = ItemSnapshot(
            item_id=1,
            timestamp=timestamp,
            avg_high_price=1234.56,
            avg_low_price=1200.99,
        )
        assert snapshot.avg_high_price == pytest.approx(1234.56)
        assert snapshot.avg_low_price == pytest.approx(1200.99)

    def test_snapshot_with_high_volumes(self):
        """Test snapshot with very high volume values."""
        timestamp = datetime.now(timezone.utc)
        snapshot = ItemSnapshot(
            item_id=1,
            timestamp=timestamp,
            high_price_volume=1_000_000,
            low_price_volume=2_000_000,
            total_volume=3_000_000,
        )
        assert snapshot.high_price_volume == 1_000_000
        assert snapshot.low_price_volume == 2_000_000
        assert snapshot.total_volume == 3_000_000

    def test_snapshot_total_volume_calculation(self):
        """Test that total_volume can represent sum of high and low volumes."""
        timestamp = datetime.now(timezone.utc)
        high_vol = 5000
        low_vol = 7000
        total_vol = high_vol + low_vol

        snapshot = ItemSnapshot(
            item_id=1,
            timestamp=timestamp,
            high_price_volume=high_vol,
            low_price_volume=low_vol,
            total_volume=total_vol,
        )
        assert snapshot.total_volume == high_vol + low_vol

    def test_snapshot_with_past_timestamp(self):
        """Test snapshot with past timestamp."""
        past_time = datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        snapshot = ItemSnapshot(
            item_id=1,
            timestamp=past_time,
        )
        assert snapshot.timestamp == past_time

    def test_snapshot_with_future_timestamp(self):
        """Test snapshot with future timestamp."""
        future_time = datetime(2030, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        snapshot = ItemSnapshot(
            item_id=1,
            timestamp=future_time,
        )
        assert snapshot.timestamp == future_time

    def test_realistic_fire_rune_snapshot(self):
        """Test realistic scenario: Fire rune snapshot."""
        timestamp = datetime(2024, 8, 25, 12, 30, 0, tzinfo=timezone.utc)
        snapshot = ItemSnapshot(
            item_id=554,  # Fire rune
            timestamp=timestamp,
            avg_high_price=5.2,
            high_price_volume=150000,
            avg_low_price=4.8,
            low_price_volume=180000,
            total_volume=330000,
        )
        assert snapshot.item_id == 554
        assert snapshot.avg_high_price == pytest.approx(5.2)
        assert snapshot.avg_low_price == pytest.approx(4.8)
        assert snapshot.total_volume == 330000

    def test_realistic_dragon_scimitar_snapshot(self):
        """Test realistic scenario: Dragon scimitar snapshot."""
        timestamp = datetime.now(timezone.utc)
        snapshot = ItemSnapshot(
            item_id=4587,  # Dragon scimitar
            timestamp=timestamp,
            avg_high_price=60000.0,
            high_price_volume=250,
            avg_low_price=59500.0,
            low_price_volume=300,
            total_volume=550,
        )
        assert snapshot.item_id == 4587
        assert snapshot.avg_high_price == 60000.0
        assert snapshot.avg_low_price == 59500.0
        assert snapshot.total_volume == 550

    def test_realistic_expensive_item_snapshot(self):
        """Test realistic scenario: Expensive item (Twisted bow)."""
        timestamp = datetime.now(timezone.utc)
        snapshot = ItemSnapshot(
            item_id=20997,  # Twisted bow
            timestamp=timestamp,
            avg_high_price=1200000000.0,
            high_price_volume=5,
            avg_low_price=1180000000.0,
            low_price_volume=3,
            total_volume=8,
        )
        assert snapshot.avg_high_price == 1200000000.0
        assert snapshot.avg_low_price == 1180000000.0
        assert snapshot.total_volume == 8

    def test_snapshot_with_no_trading_activity(self):
        """Test snapshot for item with no trading activity."""
        timestamp = datetime.now(timezone.utc)
        snapshot = ItemSnapshot(
            item_id=999,
            timestamp=timestamp,
            avg_high_price=None,
            high_price_volume=0,
            avg_low_price=None,
            low_price_volume=0,
            total_volume=0,
        )
        assert snapshot.avg_high_price is None
        assert snapshot.avg_low_price is None
        assert snapshot.total_volume == 0

    def test_snapshot_with_only_high_volume(self):
        """Test snapshot with only high volume trading."""
        timestamp = datetime.now(timezone.utc)
        snapshot = ItemSnapshot(
            item_id=1,
            timestamp=timestamp,
            avg_high_price=1000.0,
            high_price_volume=500,
            avg_low_price=None,
            low_price_volume=0,
            total_volume=500,
        )
        assert snapshot.high_price_volume == 500
        assert snapshot.low_price_volume == 0
        assert snapshot.total_volume == 500

    def test_snapshot_with_only_low_volume(self):
        """Test snapshot with only low volume trading."""
        timestamp = datetime.now(timezone.utc)
        snapshot = ItemSnapshot(
            item_id=1,
            timestamp=timestamp,
            avg_high_price=None,
            high_price_volume=0,
            avg_low_price=900.0,
            low_price_volume=600,
            total_volume=600,
        )
        assert snapshot.high_price_volume == 0
        assert snapshot.low_price_volume == 600
        assert snapshot.total_volume == 600

    def test_snapshot_tablename(self):
        """Test that table name is correctly set."""
        assert ItemSnapshot.__tablename__ == "itemsnapshot"

    def test_snapshot_item_id_field(self):
        """Test item_id field is properly set."""
        timestamp = datetime.now(timezone.utc)
        snapshot = ItemSnapshot(
            item_id=12345,
            timestamp=timestamp,
        )
        assert snapshot.item_id == 12345

    def test_snapshot_multiple_items_same_timestamp(self):
        """Test multiple snapshots for different items at same timestamp."""
        timestamp = datetime.now(timezone.utc)
        snapshot1 = ItemSnapshot(item_id=1, timestamp=timestamp)
        snapshot2 = ItemSnapshot(item_id=2, timestamp=timestamp)
        snapshot3 = ItemSnapshot(item_id=3, timestamp=timestamp)

        assert snapshot1.item_id == 1
        assert snapshot2.item_id == 2
        assert snapshot3.item_id == 3
        assert snapshot1.timestamp == snapshot2.timestamp == snapshot3.timestamp

    def test_snapshot_same_item_different_timestamps(self):
        """Test multiple snapshots for same item at different times."""
        item_id = 554
        time1 = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        time2 = datetime(2024, 1, 1, 12, 5, 0, tzinfo=timezone.utc)
        time3 = datetime(2024, 1, 1, 12, 10, 0, tzinfo=timezone.utc)

        snapshot1 = ItemSnapshot(item_id=item_id, timestamp=time1, avg_high_price=5.0)
        snapshot2 = ItemSnapshot(item_id=item_id, timestamp=time2, avg_high_price=5.2)
        snapshot3 = ItemSnapshot(item_id=item_id, timestamp=time3, avg_high_price=5.1)

        assert snapshot1.item_id == snapshot2.item_id == snapshot3.item_id
        assert snapshot1.avg_high_price == 5.0
        assert snapshot2.avg_high_price == 5.2
        assert snapshot3.avg_high_price == 5.1

    def test_snapshot_price_spread(self):
        """Test snapshot with high-low price spread."""
        timestamp = datetime.now(timezone.utc)
        snapshot = ItemSnapshot(
            item_id=1,
            timestamp=timestamp,
            avg_high_price=1000.0,
            avg_low_price=950.0,
        )
        spread = snapshot.avg_high_price - snapshot.avg_low_price
        assert spread == pytest.approx(50.0)

    def test_snapshot_large_price_values(self):
        """Test snapshot with very large price values."""
        timestamp = datetime.now(timezone.utc)
        snapshot = ItemSnapshot(
            item_id=1,
            timestamp=timestamp,
            avg_high_price=2_147_483_647.0,  # Max 32-bit int as float
            avg_low_price=2_000_000_000.0,
        )
        assert snapshot.avg_high_price == 2_147_483_647.0
        assert snapshot.avg_low_price == 2_000_000_000.0

    def test_snapshot_very_small_price_values(self):
        """Test snapshot with very small price values."""
        timestamp = datetime.now(timezone.utc)
        snapshot = ItemSnapshot(
            item_id=1,
            timestamp=timestamp,
            avg_high_price=0.1,
            avg_low_price=0.05,
        )
        assert snapshot.avg_high_price == pytest.approx(0.1)
        assert snapshot.avg_low_price == pytest.approx(0.05)

    def test_snapshot_negative_id(self):
        """Test snapshot with negative item_id (edge case)."""
        timestamp = datetime.now(timezone.utc)
        snapshot = ItemSnapshot(
            item_id=-1,
            timestamp=timestamp,
        )
        assert snapshot.item_id == -1

    def test_snapshot_timestamp_precision(self):
        """Test that timestamp maintains microsecond precision."""
        timestamp = datetime(2024, 1, 1, 12, 0, 0, 123456, tzinfo=timezone.utc)
        snapshot = ItemSnapshot(
            item_id=1,
            timestamp=timestamp,
        )
        assert snapshot.timestamp == timestamp
        assert snapshot.timestamp.microsecond == 123456
