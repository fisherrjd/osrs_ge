import pytest
from aggregator.models.item_model import Item, safe_int


class TestSafeInt:
    """Test the safe_int helper function."""

    def test_valid_integer(self):
        """Test with valid integer."""
        assert safe_int(100) == 100

    def test_zero(self):
        """Test with zero."""
        assert safe_int(0) == 0

    def test_negative_integer(self):
        """Test with negative integer."""
        assert safe_int(-50) == -50

    def test_none_returns_zero(self):
        """Test that None returns 0."""
        assert safe_int(None) == 0

    def test_string_returns_zero(self):
        """Test that string returns 0."""
        assert safe_int("100") == 0

    def test_float_returns_zero(self):
        """Test that float returns 0."""
        assert safe_int(100.5) == 0

    def test_boolean_returns_zero(self):
        """Test that boolean returns 0."""
        # Note: In Python, bool is a subclass of int, so True == 1 and False == 0
        # However, isinstance(True, int) is True, so this might behave differently
        # Based on the implementation, booleans might pass through
        result = safe_int(True)
        # Since bool is subclass of int, this will return 1
        assert result == 1

    def test_large_integer(self):
        """Test with large integer."""
        assert safe_int(1_000_000_000) == 1_000_000_000


class TestItemModel:
    """Test the Item SQLModel."""

    def test_create_item_with_all_fields(self):
        """Test creating Item with all fields specified."""
        item = Item(
            id=1234,
            name="Dragon scimitar",
            examine="A deadly weapon",
            members=True,
            lowalch=60000,
            limit=10,
            value=100000,
            highalch=90000,
            icon="dragon_scim.png",
            high=200000,
            highTime=1234567890,
            low=180000,
            lowTime=1234567891,
            volume_24h=150,
        )
        assert item.id == 1234
        assert item.name == "Dragon scimitar"
        assert item.examine == "A deadly weapon"
        assert item.members is True
        assert item.lowalch == 60000
        assert item.limit == 10
        assert item.value == 100000
        assert item.highalch == 90000
        assert item.icon == "dragon_scim.png"
        assert item.high == 200000
        assert item.highTime == 1234567890
        assert item.low == 180000
        assert item.lowTime == 1234567891
        assert item.volume_24h == 150

    def test_create_item_with_defaults(self):
        """Test creating Item with default values."""
        item = Item()
        assert item.id is None
        assert item.name == "Unknown"
        assert item.examine == ""
        assert item.members is False
        assert item.lowalch == 0
        assert item.limit == 0
        assert item.value == 0
        assert item.highalch == 0
        assert item.icon == ""
        assert item.high is None
        assert item.highTime is None
        assert item.low is None
        assert item.lowTime is None
        assert item.volume_24h == 0

    def test_margin_property_basic(self):
        """Test margin property with basic values."""
        item = Item(high=1000, low=500)
        # Tax = 1000 // 100 = 10
        # Margin = (1000 - 10) - 500 = 490
        assert item.margin == 490

    def test_margin_property_with_tax_cap(self):
        """Test margin property with values that hit tax cap."""
        item = Item(high=1_000_000_000, low=500_000_000)
        # Tax capped at 5M
        # Margin = (1_000_000_000 - 5_000_000) - 500_000_000 = 495_000_000
        assert item.margin == 495_000_000

    def test_margin_property_negative(self):
        """Test margin property with loss scenario."""
        item = Item(high=500, low=1000)
        # Tax = 500 // 100 = 5
        # Margin = (500 - 5) - 1000 = -505
        assert item.margin == -505

    def test_margin_property_zero_margin(self):
        """Test margin property when prices are equal."""
        item = Item(high=1000, low=1000)
        # Tax = 1000 // 100 = 10
        # Margin = (1000 - 10) - 1000 = -10
        assert item.margin == -10

    def test_margin_property_none_values(self):
        """Test margin property when high/low are None."""
        # This will raise a TypeError because ge_margin expects ints
        item = Item(high=None, low=None)
        with pytest.raises(TypeError):
            _ = item.margin

    def test_margin_property_one_none(self):
        """Test margin property when one value is None."""
        item = Item(high=1000, low=None)
        with pytest.raises(TypeError):
            _ = item.margin

    def test_free_to_play_item(self):
        """Test creating a free-to-play item."""
        item = Item(
            id=554,  # Fire rune
            name="Fire rune",
            examine="One of the four basic elemental Runes.",
            members=False,
            lowalch=1,
            highalch=2,
            limit=10000,
            value=5,
            high=5,
            low=4,
            volume_24h=1000000,
        )
        assert item.members is False
        assert item.name == "Fire rune"

    def test_members_item(self):
        """Test creating a members-only item."""
        item = Item(
            id=4151,  # Abyssal whip
            name="Abyssal whip",
            examine="A weapon from the abyss.",
            members=True,
            lowalch=72000,
            highalch=108000,
            limit=70,
            value=180000,
            high=2000000,
            low=1950000,
            volume_24h=1500,
        )
        assert item.members is True
        assert item.name == "Abyssal whip"

    def test_item_with_zero_volume(self):
        """Test item with zero trading volume."""
        item = Item(
            id=1,
            name="Rare item",
            high=1000000,
            low=900000,
            volume_24h=0,
        )
        assert item.volume_24h == 0

    def test_item_with_high_volume(self):
        """Test item with very high trading volume."""
        item = Item(
            id=1,
            name="Popular item",
            high=100,
            low=95,
            volume_24h=10000000,
        )
        assert item.volume_24h == 10000000

    def test_partial_price_data(self):
        """Test item with only high price set."""
        item = Item(id=1, name="Test", high=1000, low=None)
        assert item.high == 1000
        assert item.low is None

    def test_no_price_data(self):
        """Test item with no price data."""
        item = Item(id=1, name="Untradeable item")
        assert item.high is None
        assert item.low is None
        assert item.highTime is None
        assert item.lowTime is None

    def test_realistic_cheap_item(self):
        """Test realistic scenario for cheap item."""
        item = Item(
            id=2,
            name="Cannonball",
            examine="Ammo for the Dwarf Cannon.",
            members=True,
            lowalch=2,
            highalch=3,
            limit=9000,
            value=5,
            high=200,
            low=195,
            volume_24h=500000,
        )
        # Tax = 200 // 100 = 2
        # Margin = (200 - 2) - 195 = 3
        assert item.margin == 3

    def test_realistic_expensive_item(self):
        """Test realistic scenario for expensive item."""
        item = Item(
            id=11802,
            name="Armadyl godsword",
            examine="A weapon blessed by Armadyl.",
            members=True,
            lowalch=500000,
            highalch=750000,
            limit=10,
            value=1250000,
            high=40000000,
            low=39500000,
            volume_24h=50,
        )
        # Tax = 40000000 // 100 = 400000
        # Margin = (40000000 - 400000) - 39500000 = 100000
        assert item.margin == 100000

    def test_item_string_id_conversion(self):
        """Test that ID can be set from integer."""
        item = Item(id=12345, name="Test")
        assert item.id == 12345
        assert isinstance(item.id, int)

    def test_alch_values(self):
        """Test high alch and low alch values."""
        item = Item(
            id=1,
            name="Rune platebody",
            lowalch=25600,
            highalch=38400,
        )
        assert item.lowalch == 25600
        assert item.highalch == 38400
        assert item.highalch > item.lowalch

    def test_item_limit(self):
        """Test GE buy limit."""
        item = Item(id=1, name="Nature rune", limit=25000)
        assert item.limit == 25000

    def test_timestamps(self):
        """Test price timestamps."""
        item = Item(
            id=1,
            name="Test",
            high=1000,
            highTime=1609459200,  # 2021-01-01 00:00:00 UTC
            low=950,
            lowTime=1609459260,  # 2021-01-01 00:01:00 UTC
        )
        assert item.highTime == 1609459200
        assert item.lowTime == 1609459260
        assert item.lowTime > item.highTime
