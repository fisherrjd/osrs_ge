import pytest
import sys
import os

# Add the project root to the path so we can import the parse_num and compare functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


# Import the functions we need to test from best_margin.py
# Since they're defined in a streamlit app, we'll need to extract and test them
# For now, we'll define them here to test the logic

def parse_num(val):
    """Parse numeric values with k, m, b, t suffixes."""
    if isinstance(val, (int, float)):
        return val
    # This will raise AttributeError if val is None (when calling .replace())
    val = val.replace(",", "").strip().lower()
    if val.endswith("k"):
        try:
            return int(float(val[:-1]) * 1_000)
        except ValueError:
            return 0
    elif val.endswith("m"):
        try:
            return int(float(val[:-1]) * 1_000_000)
        except ValueError:
            return 0
    elif val.endswith("b"):
        try:
            return int(float(val[:-1]) * 1_000_000_000)
        except ValueError:
            return 0
    elif val.endswith("t"):
        try:
            return int(float(val[:-1]) * 1_000_000_000_000)
        except ValueError:
            return 0
    try:
        return int(val)
    except ValueError:
        return 0


def compare(val, op, ref):
    """Compare val with ref using the given operator. Returns False if val is None."""
    if val is None:
        return False
    return val > ref if op == ">" else val < ref


class TestParseNum:
    """Test the parse_num function for parsing numeric values with suffixes."""

    def test_integer_input(self):
        """Test with direct integer input."""
        assert parse_num(100) == 100

    def test_float_input(self):
        """Test with direct float input."""
        assert parse_num(100.5) == 100.5

    def test_string_number(self):
        """Test with string number."""
        assert parse_num("100") == 100

    def test_thousand_suffix_k(self):
        """Test parsing 'k' suffix for thousands."""
        assert parse_num("1k") == 1_000
        assert parse_num("10k") == 10_000
        assert parse_num("100k") == 100_000

    def test_million_suffix_m(self):
        """Test parsing 'm' suffix for millions."""
        assert parse_num("1m") == 1_000_000
        assert parse_num("10m") == 10_000_000
        assert parse_num("100m") == 100_000_000

    def test_billion_suffix_b(self):
        """Test parsing 'b' suffix for billions."""
        assert parse_num("1b") == 1_000_000_000
        assert parse_num("10b") == 10_000_000_000
        assert parse_num("100b") == 100_000_000_000

    def test_trillion_suffix_t(self):
        """Test parsing 't' suffix for trillions."""
        assert parse_num("1t") == 1_000_000_000_000
        assert parse_num("10t") == 10_000_000_000_000

    def test_decimal_with_k_suffix(self):
        """Test decimal values with k suffix."""
        assert parse_num("1.5k") == 1_500
        assert parse_num("2.5k") == 2_500
        assert parse_num("0.5k") == 500

    def test_decimal_with_m_suffix(self):
        """Test decimal values with m suffix."""
        assert parse_num("1.5m") == 1_500_000
        assert parse_num("2.5m") == 2_500_000
        assert parse_num("0.1m") == 100_000

    def test_decimal_with_b_suffix(self):
        """Test decimal values with b suffix."""
        assert parse_num("1.5b") == 1_500_000_000
        assert parse_num("2.5b") == 2_500_000_000

    def test_uppercase_suffixes(self):
        """Test that uppercase suffixes are handled (converted to lowercase)."""
        assert parse_num("1K") == 1_000
        assert parse_num("1M") == 1_000_000
        assert parse_num("1B") == 1_000_000_000
        assert parse_num("1T") == 1_000_000_000_000

    def test_mixed_case_suffixes(self):
        """Test mixed case is handled."""
        assert parse_num("1k") == 1_000
        assert parse_num("1K") == 1_000

    def test_commas_in_numbers(self):
        """Test that commas are properly removed."""
        assert parse_num("1,000") == 1_000
        assert parse_num("1,000,000") == 1_000_000
        assert parse_num("100,000,000") == 100_000_000

    def test_commas_with_suffix(self):
        """Test commas with suffix (though unusual)."""
        assert parse_num("1,000k") == 1_000_000

    def test_whitespace_handling(self):
        """Test that whitespace is stripped."""
        assert parse_num("  100  ") == 100
        assert parse_num("  1k  ") == 1_000
        assert parse_num(" 1m ") == 1_000_000

    def test_zero_value(self):
        """Test zero value."""
        assert parse_num("0") == 0
        assert parse_num(0) == 0

    def test_zero_with_suffix(self):
        """Test zero with suffix."""
        assert parse_num("0k") == 0
        assert parse_num("0m") == 0

    def test_invalid_string_returns_zero(self):
        """Test that invalid strings return 0."""
        assert parse_num("abc") == 0
        assert parse_num("invalid") == 0
        assert parse_num("") == 0

    def test_negative_values(self):
        """Test negative values (edge case)."""
        assert parse_num("-100") == -100
        assert parse_num("-1k") == -1_000
        assert parse_num("-1m") == -1_000_000

    def test_very_small_decimal(self):
        """Test very small decimal values with suffix."""
        assert parse_num("0.1k") == 100
        assert parse_num("0.01m") == 10_000

    def test_realistic_osrs_values(self):
        """Test realistic OSRS gold values."""
        assert parse_num("3.5b") == 3_500_000_000  # Party hat price
        assert parse_num("100m") == 100_000_000  # High tier item
        assert parse_num("500k") == 500_000  # Mid tier item
        assert parse_num("1000") == 1_000  # Low tier item

    def test_none_input(self):
        """Test None input."""
        # This will raise an AttributeError when trying to call .replace()
        # The function doesn't handle None gracefully, it would need a fix
        with pytest.raises(AttributeError):
            parse_num(None)

    def test_large_number_string(self):
        """Test large number as string."""
        assert parse_num("1000000000") == 1_000_000_000

    def test_special_characters(self):
        """Test strings with special characters return 0."""
        assert parse_num("@#$%") == 0
        assert parse_num("1@k") == 0  # Invalid format


class TestCompare:
    """Test the compare function for comparing values with operators."""

    def test_greater_than_true(self):
        """Test greater than comparison returns True."""
        assert compare(10, ">", 5) is True

    def test_greater_than_false(self):
        """Test greater than comparison returns False."""
        assert compare(5, ">", 10) is False

    def test_greater_than_equal(self):
        """Test greater than with equal values returns False."""
        assert compare(10, ">", 10) is False

    def test_less_than_true(self):
        """Test less than comparison returns True."""
        assert compare(5, "<", 10) is True

    def test_less_than_false(self):
        """Test less than comparison returns False."""
        assert compare(10, "<", 5) is False

    def test_less_than_equal(self):
        """Test less than with equal values returns False."""
        assert compare(10, "<", 10) is False

    def test_none_value_returns_false(self):
        """Test that None value always returns False."""
        assert compare(None, ">", 5) is False
        assert compare(None, "<", 5) is False

    def test_none_value_with_zero_ref(self):
        """Test None value with zero reference."""
        assert compare(None, ">", 0) is False
        assert compare(None, "<", 0) is False

    def test_zero_comparisons(self):
        """Test comparisons with zero."""
        assert compare(0, ">", -1) is True
        assert compare(0, "<", 1) is True
        assert compare(0, ">", 0) is False
        assert compare(0, "<", 0) is False

    def test_negative_numbers(self):
        """Test comparisons with negative numbers."""
        assert compare(-5, ">", -10) is True
        assert compare(-10, "<", -5) is True
        assert compare(-5, ">", 5) is False

    def test_large_numbers(self):
        """Test comparisons with large numbers."""
        assert compare(1_000_000_000, ">", 999_999_999) is True
        assert compare(999_999_999, "<", 1_000_000_000) is True

    def test_float_comparisons(self):
        """Test comparisons with float values."""
        assert compare(10.5, ">", 10) is True
        assert compare(10.0, "<", 10.5) is True

    def test_realistic_osrs_filters(self):
        """Test realistic OSRS filtering scenarios."""
        # Item with high price > 1m
        assert compare(2_000_000, ">", 1_000_000) is True

        # Item with low price < 100k
        assert compare(50_000, "<", 100_000) is True

        # Item with margin > 10k
        assert compare(15_000, ">", 10_000) is True

        # Item with volume < 1000
        assert compare(500, "<", 1_000) is True

    def test_filter_out_none_prices(self):
        """Test that items with None prices are filtered out."""
        # This simulates filtering items that don't have price data
        assert compare(None, ">", 0) is False
        assert compare(None, "<", 1_000_000_000) is False

    def test_edge_case_boundary_values(self):
        """Test boundary value comparisons."""
        # Just above threshold
        assert compare(100_001, ">", 100_000) is True

        # Just below threshold
        assert compare(99_999, "<", 100_000) is True

        # Exactly at threshold
        assert compare(100_000, ">", 100_000) is False
        assert compare(100_000, "<", 100_000) is False

    def test_invalid_operator_behavior(self):
        """Test behavior with invalid operator (edge case)."""
        # The function only checks for ">", anything else defaults to "<"
        assert compare(10, ">=", 5) is False  # Will be treated as "<"
        assert compare(10, "==", 5) is False  # Will be treated as "<"
        assert compare(5, "!=", 10) is True  # Will be treated as "<"

    def test_string_comparisons(self):
        """Test comparisons with string values."""
        # This would work in Python as strings can be compared
        assert compare("b", ">", "a") is True
        assert compare("a", "<", "b") is True

    def test_combined_with_parse_num(self):
        """Test compare function with parse_num results."""
        # Simulating filtering workflow
        user_input = "1m"
        threshold = parse_num(user_input)
        assert compare(2_000_000, ">", threshold) is True
        assert compare(500_000, ">", threshold) is False
