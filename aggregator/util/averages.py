from typing import List, Optional, Union


def get_average_field(items, field: str) -> Optional[float]:
    """
    Calculate average of a field across items.

    Args:
        items: Either a list of Volume5mItem objects or a Volume5m object with a .data dict
        field: The field name to average

    Returns:
        Average value or None if no valid values
    """
    # Handle Volume5m object (has .data attribute which is a dict)
    if hasattr(items, 'data') and isinstance(items.data, dict):
        items_list = list(items.data.values())
    else:
        items_list = items

    valid = [
        getattr(item, field, None)
        for item in items_list
        if getattr(item, field, None) is not None
    ]
    if not valid:
        return None
    return sum(valid) / len(valid)
