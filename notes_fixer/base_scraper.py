"""Base scraper interface for content sources."""

from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ScrapedItem:
    """Represents a scraped content item."""
    title: str
    url: str
    author: str
    published_at: str
    content: str
    score: int = 0  # Optional score/rating
    summary: str = ""


class BaseScraper(ABC):
    """Base class for all content scrapers."""

    @abstractmethod
    def fetch_items(self) -> List[ScrapedItem]:
        """Fetch items from the source."""
        pass

    @abstractmethod
    def format_for_daily_note(self, items: List[ScrapedItem]) -> str:
        """Format scraped items for inclusion in daily note."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the scraper source."""
        pass
