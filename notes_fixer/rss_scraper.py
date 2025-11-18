"""RSS feed scraper for fetching content from RSS/Atom feeds."""

from typing import List
import requests
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from .base_scraper import BaseScraper, ScrapedItem
from .ai_processor import AIProcessor


class RSSFeedScraper(BaseScraper):
    """Scraper for RSS/Atom feeds."""

    def __init__(self, feed_urls: List[str], ai_processor: AIProcessor, max_items_per_feed: int = 5):
        """
        Initialize RSS feed scraper.

        Args:
            feed_urls: List of RSS/Atom feed URLs to scrape
            ai_processor: AI processor for generating summaries
            max_items_per_feed: Maximum number of items to fetch per feed
        """
        self.feed_urls = feed_urls
        self.ai_processor = ai_processor
        self.max_items_per_feed = max_items_per_feed

    @property
    def name(self) -> str:
        return "RSS Feeds"

    def fetch_items(self) -> List[ScrapedItem]:
        """Fetch items from all configured RSS feeds."""
        all_items: List[ScrapedItem] = []

        for feed_url in self.feed_urls:
            print(f"Fetching RSS feed: {feed_url}")
            try:
                # Fetch the feed
                response = requests.get(feed_url, timeout=10)
                response.raise_for_status()

                # Parse XML
                root = ET.fromstring(response.content)

                # Handle both RSS and Atom feeds
                items = self._parse_feed(root)

                # Limit to max items per feed
                for item in items[:self.max_items_per_feed]:
                    all_items.append(item)

            except Exception as e:
                print(f"Error fetching RSS feed {feed_url}: {e}")
                continue

        return all_items

    def _parse_feed(self, root: ET.Element) -> List[ScrapedItem]:
        """Parse RSS or Atom feed from XML root."""
        items: List[ScrapedItem] = []

        # Check if it's RSS or Atom
        if root.tag == 'rss' or root.tag == '{http://www.w3.org/2005/Atom}feed':
            # RSS feed
            if root.tag == 'rss':
                for item in root.findall('.//item'):
                    scraped_item = self._parse_rss_item(item)
                    if scraped_item:
                        items.append(scraped_item)
            # Atom feed
            else:
                for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                    scraped_item = self._parse_atom_entry(entry)
                    if scraped_item:
                        items.append(scraped_item)

        return items

    def _parse_rss_item(self, item: ET.Element) -> ScrapedItem:
        """Parse an RSS item."""
        title = self._get_text(item, 'title', 'No Title')
        link = self._get_text(item, 'link', '')
        author = self._get_text(item, 'author') or self._get_text(item, '{http://purl.org/dc/elements/1.1/}creator', 'Unknown')
        published = self._get_text(item, 'pubDate', '')

        # Get description/content
        description = self._get_text(item, 'description', '')
        content = self._get_text(item, '{http://purl.org/rss/1.0/modules/content/}encoded', description)

        # Strip HTML
        content = self._strip_html(content)[:1000]

        return ScrapedItem(
            title=title,
            url=link,
            author=author,
            published_at=published,
            content=content,
        )

    def _parse_atom_entry(self, entry: ET.Element) -> ScrapedItem:
        """Parse an Atom entry."""
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        title_elem = entry.find('atom:title', ns)
        title = title_elem.text if title_elem is not None else 'No Title'

        link_elem = entry.find('atom:link[@rel="alternate"]', ns) or entry.find('atom:link', ns)
        link = link_elem.get('href', '') if link_elem is not None else ''

        author_elem = entry.find('atom:author/atom:name', ns)
        author = author_elem.text if author_elem is not None else 'Unknown'

        published_elem = entry.find('atom:published', ns) or entry.find('atom:updated', ns)
        published = published_elem.text if published_elem is not None else ''

        # Get content or summary
        content_elem = entry.find('atom:content', ns) or entry.find('atom:summary', ns)
        content = content_elem.text if content_elem is not None else ''

        # Strip HTML
        content = self._strip_html(content)[:1000]

        return ScrapedItem(
            title=title,
            url=link,
            author=author,
            published_at=published,
            content=content,
        )

    def _get_text(self, element: ET.Element, tag: str, default: str = '') -> str:
        """Safely get text from an XML element."""
        child = element.find(tag)
        return child.text if child is not None and child.text else default

    def format_for_daily_note(self, items: List[ScrapedItem]) -> str:
        """Format RSS items for daily note with AI summaries."""
        if not items:
            return "No new items from RSS feeds."

        print(f"Generating summaries for {len(items)} RSS items...")

        formatted_items: List[str] = []

        for item in items:
            # Generate AI summary
            summary = self.ai_processor.summarize_post(
                item.title,
                item.url,
                item.content
            )

            formatted = f"""### [{item.title}]({item.url})
**Author:** {item.author} | **Published:** {item.published_at[:10] if item.published_at else 'Unknown'}

{summary}"""

            formatted_items.append(formatted)

        return "\n\n".join(formatted_items)

    def _strip_html(self, html_text: str) -> str:
        """Remove HTML tags from text."""
        import re
        # Remove HTML tags
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', html_text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
