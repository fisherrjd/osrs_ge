from typing import List, Optional
from aggregator.models.data_models import Volume5mItem


def get_average_field(items: List[Volume5mItem], field: str) -> Optional[float]:
    valid = [
        getattr(item, field, None)
        for item in items
        if getattr(item, field, None) is not None
    ]
    if not valid:
        return None
    return sum(valid) / len(valid)
