from datetime import datetime, timezone

from sqlmodel import Session, col, select

from api.schemas.dump_event import DumpEvent
from api.schemas.item_model import Item
from api.schemas.item_volume_5m import ItemSnapshot

# Detection thresholds
PRICE_CHANGE_THRESHOLD = 0.05  # 5% price change
VOLUME_SPIKE_THRESHOLD = 2.0  # 2x average volume
BASELINE_SNAPSHOTS = 12  # 1 hour of 5-minute snapshots


def get_baseline_stats(
    session: Session, item_id: int, before_timestamp: datetime
) -> tuple[float | None, float | None]:
    """
    Calculate baseline price and volume averages from recent snapshots.

    Returns (avg_price, avg_volume) or (None, None) if insufficient data.
    """
    query = (
        select(ItemSnapshot)
        .where(ItemSnapshot.item_id == item_id)
        .where(ItemSnapshot.timestamp < before_timestamp)
        .order_by(col(ItemSnapshot.timestamp).desc())
        .limit(BASELINE_SNAPSHOTS)
    )
    snapshots = session.exec(query).all()

    if len(snapshots) < 3:
        # Need at least 3 snapshots for meaningful baseline
        return None, None

    # Calculate average price (use avg_high_price as primary indicator)
    prices = [s.avg_high_price for s in snapshots if s.avg_high_price is not None]
    volumes = [s.total_volume for s in snapshots if s.total_volume is not None]

    if not prices or not volumes:
        return None, None

    avg_price = sum(prices) / len(prices)
    avg_volume = sum(volumes) / len(volumes)

    return avg_price, avg_volume


def detect_event(
    session: Session,
    item_id: int,
    item_name: str,
    current_snapshot: ItemSnapshot,
) -> DumpEvent | None:
    """
    Analyze a snapshot for dump/spike events.

    Returns a DumpEvent if thresholds are exceeded, None otherwise.
    """
    # Get current values
    current_price = current_snapshot.avg_high_price
    current_volume = current_snapshot.total_volume

    if current_price is None or current_volume is None:
        return None

    # Get baseline
    baseline_price, baseline_volume = get_baseline_stats(
        session, item_id, current_snapshot.timestamp
    )

    if baseline_price is None or baseline_volume is None:
        return None

    if baseline_price == 0 or baseline_volume == 0:
        return None

    # Calculate changes
    price_change = (current_price - baseline_price) / baseline_price
    volume_change = current_volume / baseline_volume

    # Check for dump (price drop + volume spike)
    if (
        price_change <= -PRICE_CHANGE_THRESHOLD
        and volume_change >= VOLUME_SPIKE_THRESHOLD
    ):
        return DumpEvent(
            item_id=item_id,
            item_name=item_name,
            event_type="dump",
            detected_at=datetime.now(timezone.utc),
            trigger_price=current_price,
            baseline_price=baseline_price,
            price_change_percent=price_change * 100,
            trigger_volume=current_volume,
            baseline_volume=baseline_volume,
            volume_change_percent=(volume_change - 1) * 100,
        )

    # Check for spike (price rise + volume spike)
    if (
        price_change >= PRICE_CHANGE_THRESHOLD
        and volume_change >= VOLUME_SPIKE_THRESHOLD
    ):
        return DumpEvent(
            item_id=item_id,
            item_name=item_name,
            event_type="spike",
            detected_at=datetime.now(timezone.utc),
            trigger_price=current_price,
            baseline_price=baseline_price,
            price_change_percent=price_change * 100,
            trigger_volume=current_volume,
            baseline_volume=baseline_volume,
            volume_change_percent=(volume_change - 1) * 100,
        )

    return None


def run_detection_for_snapshots(
    session: Session, snapshots: list[ItemSnapshot]
) -> list[DumpEvent]:
    """
    Run detection on a batch of snapshots.

    Returns list of detected events.
    """
    events = []

    # Build item_id -> name mapping
    item_ids = list({s.item_id for s in snapshots})
    items_query = select(Item).where(col(Item.id).in_(item_ids))
    items = session.exec(items_query).all()
    item_names = {item.id: item.name for item in items}

    for snapshot in snapshots:
        item_name = item_names.get(snapshot.item_id, f"Item {snapshot.item_id}")
        event = detect_event(session, snapshot.item_id, item_name, snapshot)
        if event:
            events.append(event)

    return events
