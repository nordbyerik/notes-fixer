"""LessWrong integration for fetching and summarizing posts."""

from typing import List
import requests
from .types import Config, LessWrongPost
from .ai_processor import AIProcessor


class LessWrongIntegration:
    """Handles fetching and processing LessWrong posts."""

    GRAPHQL_ENDPOINT = "https://www.lesswrong.com/graphql"

    def __init__(self, config: Config, ai_processor: AIProcessor):
        self.config = config
        self.ai_processor = ai_processor

    def fetch_top_posts(self) -> List[LessWrongPost]:
        """Fetch top recent posts from LessWrong."""
        query = f"""
            query RecentPosts {{
                posts(input: {{
                    terms: {{
                        view: "magic"
                        limit: {self.config.lesswrong_post_count}
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
                LessWrongPost(
                    id=post["_id"],
                    title=post["title"],
                    author=post.get("user", {}).get("displayName", "Unknown"),
                    url=f"https://www.lesswrong.com/posts/{post['_id']}/{post['slug']}",
                    base_score=post["baseScore"],
                    posted_at=post["postedAt"],
                    content=post.get("contents", {}).get("plaintextDescription", ""),
                )
                for post in posts
            ]
        except Exception as e:
            print(f"Error fetching LessWrong posts: {e}")
            return []

    def fetch_and_summarize_posts(self) -> str:
        """Fetch and summarize top posts."""
        print("Fetching top LessWrong posts...")
        posts = self.fetch_top_posts()

        if not posts:
            return "No posts available."

        print(f"Found {len(posts)} posts. Generating summaries...")

        summaries: List[str] = []

        for post in posts:
            summary = self.ai_processor.summarize_post(
                post.title, post.url, post.content
            )

            formatted_post = f"""### [{post.title}]({post.url})
**Author:** {post.author} | **Score:** {post.base_score}

{summary}"""

            summaries.append(formatted_post)

        return "\n\n".join(summaries)
