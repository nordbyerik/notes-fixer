"""LessWrong integration for fetching and summarizing posts."""

from typing import List
import requests
from .types import Config
from .ai_processor import AIProcessor
from .base_scraper import BaseScraper, ScrapedItem


class LessWrongScraper(BaseScraper):
    """Scraper for LessWrong posts."""

    GRAPHQL_ENDPOINT = "https://www.lesswrong.com/graphql"

    def __init__(self, post_count: int, ai_processor: AIProcessor):
        self.post_count = post_count
        self.ai_processor = ai_processor

    @property
    def name(self) -> str:
        return "LessWrong"

    def fetch_items(self) -> List[ScrapedItem]:
        """Fetch top recent posts from LessWrong."""
        query = f"""
            query RecentPosts {{
                posts(input: {{
                    terms: {{
                        view: "magic"
                        limit: {self.post_count}
                        filter: "frontpage"
                    }}
                }}) {{
                    results {{
                        _id
                        title
                        slug
                        baseScore
                        postedAt
                        user {{
                            displayName
                        }}
                        contents {{
                            plaintextDescription
                        }}
                    }}
                }}
            }}
        """

        try:
            response = requests.post(
                self.GRAPHQL_ENDPOINT,
                json={"query": query},
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                print(f"GraphQL errors: {data['errors']}")
                return []

            posts = data["data"]["posts"]["results"]

            return [
                ScrapedItem(
                    title=post["title"],
                    author=post.get("user", {}).get("displayName", "Unknown"),
                    url=f"https://www.lesswrong.com/posts/{post['_id']}/{post['slug']}",
                    published_at=post["postedAt"],
                    content=post.get("contents", {}).get("plaintextDescription", ""),
                    score=post["baseScore"],
                )
                for post in posts
            ]
        except Exception as e:
            print(f"Error fetching LessWrong posts: {e}")
            return []

    def format_for_daily_note(self, items: List[ScrapedItem]) -> str:
        """Format LessWrong posts for daily note with AI summaries."""
        if not items:
            return "No posts available."

        print(f"Generating summaries for {len(items)} LessWrong posts...")

        formatted_items: List[str] = []

        for item in items:
            summary = self.ai_processor.summarize_post(
                item.title, item.url, item.content
            )

            formatted = f"""### [{item.title}]({item.url})
**Author:** {item.author} | **Score:** {item.score}

{summary}"""

            formatted_items.append(formatted)

        return "\n\n".join(formatted_items)
