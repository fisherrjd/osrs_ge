from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class SourceType(str, Enum):
    OFFICIAL = "official"
    REDDIT = "reddit"


class CategoryType(str, Enum):
    UPDATE = "update"
    PATCH = "patch"
    COMMUNITY = "community"
    EVENT = "event"


class NewsItem(SQLModel, table=True):
    __tablename__ = "news_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = Field(default=None)
    source: SourceType = Field(index=True)
    source_identifier: Optional[str] = Field(default=None)
    category: CategoryType = Field(index=True)
    date: datetime = Field(index=True)
    url: str = Field(unique=True)
    upvotes: Optional[int] = Field(default=None)
    comments: Optional[int] = Field(default=None)

    # Backend-only fields for ranking/management
    score: float = Field(default=0.0, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def calculate_score(self) -> float:
        """Calculate ranking score - called by backend cronjob"""
        base_score = 0

        source_weights = {SourceType.OFFICIAL: 100, SourceType.REDDIT: 50}
        base_score += source_weights.get(self.source, 0)

        # Ensure date is timezone-aware for comparison
        item_date = self.date
        if item_date.tzinfo is None:
            item_date = item_date.replace(tzinfo=timezone.utc)

        age_hours = (datetime.now(timezone.utc) - item_date).total_seconds() / 3600
        time_score = max(0, 100 - (age_hours / 24) * 10)
        base_score += time_score

        if self.source == SourceType.REDDIT:
            engagement = (self.upvotes or 0) * 0.1 + (self.comments or 0) * 0.5
            base_score += min(engagement, 50)

        category_weights = {
            CategoryType.UPDATE: 20,
            CategoryType.PATCH: 15,
            CategoryType.EVENT: 10,
            CategoryType.COMMUNITY: 0,
        }
        base_score += category_weights.get(self.category, 0)

        return base_score

    @property
    def time_ago(self) -> str:
        """Generate human-readable time ago string"""
        # Ensure date is timezone-aware for comparison
        item_date = self.date
        if item_date.tzinfo is None:
            item_date = item_date.replace(tzinfo=timezone.utc)

        delta = datetime.now(timezone.utc) - item_date

        if delta.days > 365:
            years = delta.days // 365
            return f"{years} year{'s' if years != 1 else ''} ago"
        elif delta.days > 30:
            months = delta.days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"
        elif delta.days > 0:
            return f"{delta.days} day{'s' if delta.days != 1 else ''} ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "just now"

    def to_frontend(self) -> dict:
        """Serialize for frontend - only fields matching TypeScript interface"""
        result = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "category": self.category,
            "date": self.date.isoformat(),
            "timeAgo": self.time_ago,
            "url": self.url,
        }

        # Only include Reddit-specific fields if present
        if self.upvotes is not None:
            result["upvotes"] = self.upvotes
        if self.comments is not None:
            result["comments"] = self.comments

        return result
