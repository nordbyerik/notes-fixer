"""Type definitions for the notes fixer tool."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Config:
    """Configuration for the notes fixer tool."""
    ai_model: str
    ai_api_key: Optional[str]
    vault_path: str
    daily_notes_folder: str
    knowledge_repo_folder: str
    lookback_days: int
    lesswrong_post_count: int
    lesswrong_enabled: bool
    rss_feed_urls: List[str]
    rss_items_per_feed: int


@dataclass
class DailyNote:
    """Represents a daily note."""
    path: str
    file_name: str
    date: datetime
    content: str


@dataclass
class KnowledgeItem:
    """Represents an extracted knowledge item."""
    title: str
    content: str
    category: str
    date: datetime
    source_note: str


@dataclass
class LessWrongPost:
    """Represents a LessWrong post."""
    id: str
    title: str
    author: str
    url: str
    base_score: int
    posted_at: str
    content: str
    summary: Optional[str] = None
