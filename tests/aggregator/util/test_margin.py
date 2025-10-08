import pytest
from aggregator.util.margin import ge_margin


class TestGEMargin:
    """Test the GE margin calculation function."""

    def test_basic_profit_calculation(self):
        """Test basic profit calculation with simple values."""
        # High price 1000, Low price 500
        # Tax = 1000 // 100 = 10
        # Profit = (1000 - 10) - 500 = 490
        result = ge_margin(1000, 500)
        assert result == 490

    def test_zero_margin(self):
        """Test when buy and sell price are equal."""
        # High price 1000, Low price 1000
        # Tax = 1000 // 100 = 10
        # Profit = (1000 - 10) - 1000 = -10
        result = ge_margin(1000, 1000)
        assert result == -10

    def test_negative_margin(self):
        """Test when sell price is lower than buy price (loss scenario)."""
        # High price 500, Low price 1000
        # Tax = 500 // 100 = 5
        # Profit = (500 - 5) - 1000 = -505
        result = ge_margin(500, 1000)
        assert result == -505

    def test_tax_cap_at_5m(self):
        """Test that tax is capped at 5 million coins."""
        # High price 1 billion (1_000_000_000)
        # Tax should be capped at 5_000_000, not 10_000_000
        # Profit = (1_000_000_000 - 5_000_000) - 500_000_000 = 495_000_000
        result = ge_margin(1_000_000_000, 500_000_000)
        assert result == 495_000_000

    def test_tax_exactly_at_cap(self):
        """Test when calculated tax equals the cap."""
        # High price 500_000_000 (500M)
        # Tax = 500_000_000 // 100 = 5_000_000 (exactly at cap)
        # Profit = (500_000_000 - 5_000_000) - 250_000_000 = 245_000_000
        result = ge_margin(500_000_000, 250_000_000)
        assert result == 245_000_000

    def test_tax_below_cap(self):
        """Test when calculated tax is below the cap."""
        # High price 100_000_000 (100M)
        # Tax = 100_000_000 // 100 = 1_000_000 (below 5M cap)
        # Profit = (100_000_000 - 1_000_000) - 50_000_000 = 49_000_000
        result = ge_margin(100_000_000, 50_000_000)
        assert result == 49_000_000

    def test_very_small_values(self):
        """Test with very small values (under 100 coins)."""
        # High price 50, Low price 25
        # Tax = 50 // 100 = 0
        # Profit = (50 - 0) - 25 = 25
        result = ge_margin(50, 25)
        assert result == 25

    def test_zero_prices(self):
        """Test edge case with zero prices."""
        # High price 0, Low price 0
        # Tax = 0 // 100 = 0
        # Profit = (0 - 0) - 0 = 0
        result = ge_margin(0, 0)
        assert result == 0

    def test_realistic_item_scenario_1(self):
        """Test realistic scenario: Dragon bones."""
        # Example: Dragon bones selling for 2500, buying for 2400
        # Tax = 2500 // 100 = 25
        # Profit = (2500 - 25) - 2400 = 75
        result = ge_margin(2500, 2400)
        assert result == 75

    def test_realistic_item_scenario_2(self):
        """Test realistic scenario: Expensive item."""
        # Example: Blue partyhat selling for 3.5B, buying for 3.4B
        # Tax = capped at 5M
        # Profit = (3_500_000_000 - 5_000_000) - 3_400_000_000 = 95_000_000
        result = ge_margin(3_500_000_000, 3_400_000_000)
        assert result == 95_000_000

    def test_realistic_item_scenario_3(self):
        """Test realistic scenario: Mid-tier item."""
        # Example: Abyssal whip selling for 2M, buying for 1.8M
        # Tax = 2_000_000 // 100 = 20_000
        # Profit = (2_000_000 - 20_000) - 1_800_000 = 180_000
        result = ge_margin(2_000_000, 1_800_000)
        assert result == 180_000

    def test_high_price_one(self):
        """Test edge case with high price of 1."""
        # High price 1, Low price 0
        # Tax = 1 // 100 = 0
        # Profit = (1 - 0) - 0 = 1
        result = ge_margin(1, 0)
        assert result == 1

    def test_large_spread(self):
        """Test with large spread between buy and sell prices."""
        # High price 1B, Low price 100M
        # Tax = capped at 5M
        # Profit = (1_000_000_000 - 5_000_000) - 100_000_000 = 895_000_000
        result = ge_margin(1_000_000_000, 100_000_000)
        assert result == 895_000_000

    def test_minimal_profit(self):
        """Test scenario with minimal profit margin."""
        # High price 1001, Low price 1000
        # Tax = 1001 // 100 = 10
        # Profit = (1001 - 10) - 1000 = -9
        result = ge_margin(1001, 1000)
        assert result == -9

    def test_99gp_tax_threshold(self):
        """Test values just below 100gp where tax becomes 0."""
        # High price 99, Low price 50
        # Tax = 99 // 100 = 0
        # Profit = (99 - 0) - 50 = 49
        result = ge_margin(99, 50)
        assert result == 49

    def test_100gp_tax_threshold(self):
        """Test values at exactly 100gp where tax becomes 1."""
        # High price 100, Low price 50
        # Tax = 100 // 100 = 1
        # Profit = (100 - 1) - 50 = 49
        result = ge_margin(100, 50)
        assert result == 49

    def test_maximum_int_values(self):
        """Test with very large integer values."""
        # High price max int-like, Low price also large
        # Tax should be capped at 5M
        high = 2_147_483_647  # Max 32-bit int
        low = 2_000_000_000
        result = ge_margin(high, low)
        # Profit = (2_147_483_647 - 5_000_000) - 2_000_000_000 = 142_483_647
        assert result == 142_483_647
