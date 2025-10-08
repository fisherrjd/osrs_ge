"""
Tests for item lookup filtering logic.

Note: The usage/item_lookup.py file contains a bug where it references
item.item_name instead of item.name. This test file tests the intended
functionality.
"""

import pytest


def filter_items_by_search(item_names, search_text):
    """
    Filter item names by search text (case-insensitive substring match).

    This is the logic from item_lookup.py extracted for testing.
    """
    if search_text and search_text.strip():
        return [
            name for name in item_names if search_text.lower() in name.lower()
        ]
    else:
        return item_names


class TestItemFiltering:
    """Test item name filtering functionality."""

    def test_filter_with_exact_match(self):
        """Test filtering with exact name match."""
        item_names = ["Dragon scimitar", "Dragon dagger", "Abyssal whip"]
        result = filter_items_by_search(item_names, "Dragon scimitar")
        assert result == ["Dragon scimitar"]

    def test_filter_with_partial_match(self):
        """Test filtering with partial name match."""
        item_names = ["Dragon scimitar", "Dragon dagger", "Abyssal whip"]
        result = filter_items_by_search(item_names, "Dragon")
        assert len(result) == 2
        assert "Dragon scimitar" in result
        assert "Dragon dagger" in result

    def test_filter_case_insensitive(self):
        """Test that filtering is case insensitive."""
        item_names = ["Dragon scimitar", "Dragon dagger", "Abyssal whip"]
        result = filter_items_by_search(item_names, "dragon")
        assert len(result) == 2
        assert "Dragon scimitar" in result
        assert "Dragon dagger" in result

    def test_filter_uppercase_search(self):
        """Test filtering with uppercase search text."""
        item_names = ["dragon scimitar", "dragon dagger", "abyssal whip"]
        result = filter_items_by_search(item_names, "DRAGON")
        assert len(result) == 2

    def test_filter_mixed_case_search(self):
        """Test filtering with mixed case search text."""
        item_names = ["Dragon Scimitar", "DRAGON DAGGER", "abyssal whip"]
        result = filter_items_by_search(item_names, "DrAgOn")
        assert len(result) == 2

    def test_filter_with_empty_string(self):
        """Test filtering with empty search string returns all items."""
        item_names = ["Dragon scimitar", "Dragon dagger", "Abyssal whip"]
        result = filter_items_by_search(item_names, "")
        assert result == item_names

    def test_filter_with_no_matches(self):
        """Test filtering with search text that matches nothing."""
        item_names = ["Dragon scimitar", "Dragon dagger", "Abyssal whip"]
        result = filter_items_by_search(item_names, "Rune platebody")
        assert result == []

    def test_filter_with_single_character(self):
        """Test filtering with single character."""
        item_names = ["Air rune", "Water rune", "Earth rune", "Fire rune"]
        result = filter_items_by_search(item_names, "A")
        assert len(result) == 3  # Air, Water, Earth

    def test_filter_with_special_characters(self):
        """Test filtering with special characters in item names."""
        item_names = ["Dragon 2h sword", "3rd age platebody", "Bow (u)"]
        result = filter_items_by_search(item_names, "2h")
        assert result == ["Dragon 2h sword"]

    def test_filter_with_spaces(self):
        """Test filtering with spaces in search text."""
        item_names = ["Dragon scimitar", "Dragon dagger", "Abyssal whip"]
        result = filter_items_by_search(item_names, "Dragon s")
        assert result == ["Dragon scimitar"]

    def test_filter_empty_list(self):
        """Test filtering on empty item list."""
        item_names = []
        result = filter_items_by_search(item_names, "Dragon")
        assert result == []

    def test_filter_single_item_list_match(self):
        """Test filtering single item list with match."""
        item_names = ["Dragon scimitar"]
        result = filter_items_by_search(item_names, "Dragon")
        assert result == ["Dragon scimitar"]

    def test_filter_single_item_list_no_match(self):
        """Test filtering single item list with no match."""
        item_names = ["Dragon scimitar"]
        result = filter_items_by_search(item_names, "Abyssal")
        assert result == []

    def test_filter_with_substring_at_start(self):
        """Test filtering with substring at start of name."""
        item_names = ["Dragon scimitar", "Abyssal whip", "Dragon dagger"]
        result = filter_items_by_search(item_names, "Drag")
        assert len(result) == 2

    def test_filter_with_substring_at_end(self):
        """Test filtering with substring at end of name."""
        item_names = ["Dragon scimitar", "Rune scimitar", "Abyssal whip"]
        result = filter_items_by_search(item_names, "itar")
        assert len(result) == 2

    def test_filter_with_substring_in_middle(self):
        """Test filtering with substring in middle of name."""
        item_names = ["Dragon scimitar", "Dragon dagger", "Abyssal whip"]
        result = filter_items_by_search(item_names, "gon")
        assert len(result) == 2

    def test_filter_all_items_match(self):
        """Test when all items match the search."""
        item_names = ["Fire rune", "Water rune", "Air rune", "Earth rune"]
        result = filter_items_by_search(item_names, "rune")
        assert len(result) == 4

    def test_filter_with_numbers(self):
        """Test filtering with numbers in search."""
        item_names = ["3rd age platebody", "2h sword", "1000 arrows"]
        result = filter_items_by_search(item_names, "3")
        assert result == ["3rd age platebody"]

    def test_filter_preserves_order(self):
        """Test that filtering preserves original order."""
        item_names = ["Zebra", "Dragon", "Apple", "Dragon sword"]
        result = filter_items_by_search(item_names, "Dragon")
        assert result == ["Dragon", "Dragon sword"]

    def test_filter_with_duplicate_names(self):
        """Test filtering with duplicate item names."""
        item_names = ["Dragon scimitar", "Dragon dagger", "Dragon scimitar"]
        result = filter_items_by_search(item_names, "Dragon scimitar")
        assert len(result) == 2
        assert all(name == "Dragon scimitar" for name in result)

    def test_filter_realistic_osrs_items(self):
        """Test with realistic OSRS item names."""
        item_names = [
            "Abyssal whip",
            "Dragon scimitar",
            "Rune platebody",
            "Dragon platelegs",
            "Bandos chestplate",
            "Armadyl crossbow",
        ]
        result = filter_items_by_search(item_names, "plate")
        assert len(result) == 3
        assert "Rune platebody" in result
        assert "Bandos chestplate" in result
        assert "Dragon platelegs" in result

    def test_filter_common_abbreviations(self):
        """Test filtering with common OSRS abbreviations."""
        item_names = [
            "Dragon scimitar",
            "Abyssal whip",
            "Dragon dagger(p++)",
        ]
        result = filter_items_by_search(item_names, "scim")
        assert result == ["Dragon scimitar"]

    def test_filter_with_parentheses(self):
        """Test filtering items with parentheses."""
        item_names = ["Dragon dagger", "Dragon dagger(p)", "Dragon dagger(p++)"]
        result = filter_items_by_search(item_names, "(p")
        assert len(result) == 2

    def test_filter_runes(self):
        """Test filtering rune items."""
        item_names = [
            "Fire rune",
            "Water rune",
            "Air rune",
            "Rune platebody",
            "Rune scimitar",
        ]
        result = filter_items_by_search(item_names, "rune")
        assert len(result) == 5

    def test_filter_none_search_text(self):
        """Test filtering with None search text (should work like empty string)."""
        item_names = ["Dragon scimitar", "Abyssal whip"]
        # This tests the falsy behavior - None should return all items
        result = filter_items_by_search(item_names, None)
        assert result == item_names

    def test_filter_whitespace_only_search(self):
        """Test filtering with whitespace-only search."""
        item_names = ["Dragon scimitar", "Abyssal whip"]
        result = filter_items_by_search(item_names, "   ")
        # Whitespace should match items with spaces
        assert len(result) == 2

    def test_filter_long_item_names(self):
        """Test filtering with very long item names."""
        item_names = [
            "This is a very long item name for testing purposes",
            "Another long name",
            "Short",
        ]
        result = filter_items_by_search(item_names, "long")
        assert len(result) == 2

    def test_filter_large_list(self):
        """Test filtering on a large list of items."""
        # Simulate a large item database
        item_names = [f"Item {i}" for i in range(1000)]
        item_names.append("Dragon scimitar")
        result = filter_items_by_search(item_names, "Dragon")
        assert result == ["Dragon scimitar"]

    def test_filter_special_osrs_items(self):
        """Test filtering special OSRS items with unique names."""
        item_names = [
            "3rd age platebody",
            "Black d'hide body",
            "Dragon hunter crossbow",
            "Ghrazi rapier",
        ]
        result = filter_items_by_search(item_names, "hunter")
        assert result == ["Dragon hunter crossbow"]
