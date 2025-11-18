"""AI processor for extracting knowledge and summarizing content."""

import json
import re
from typing import List
from anthropic import Anthropic
from .types import Config, DailyNote, KnowledgeItem


class AIProcessor:
    """Handles AI-powered processing using Claude."""

    def __init__(self, config: Config):
        self.config = config
        self.client = Anthropic(api_key=config.anthropic_api_key)

    def extract_knowledge_from_notes(self, notes: List[DailyNote]) -> List[KnowledgeItem]:
        """Extract knowledge items from daily notes using AI."""
        if not notes:
            return []

        knowledge_items: List[KnowledgeItem] = []

        for note in notes:
            print(f"Processing note: {note.file_name}")

            prompt = f"""You are analyzing a daily note from an Obsidian vault. Your task is to extract important knowledge, cool events, interesting insights, and valuable information that should be saved to a personal knowledge repository.

Please analyze the following daily note and extract important items:

{note.content}

For each important item you find, provide:
1. A clear title
2. The content/description
3. A category (choose from: Ideas, Events, Learnings, Projects, People, Resources, or Other)

Format your response as JSON array of objects with fields: title, content, category

Only extract items that are genuinely interesting or valuable. Skip mundane daily tasks or trivial entries.

If there are no important items to extract, return an empty array."""

            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}],
                )

                response_text = message.content[0].text

                # Extract JSON from response (handle both raw JSON and markdown code blocks)
                json_str = response_text.strip()
                code_block_match = re.search(r"```(?:json)?\n([\s\S]*?)\n```", json_str)
                if code_block_match:
                    json_str = code_block_match.group(1)

                extracted = json.loads(json_str)

                if isinstance(extracted, list):
                    for item in extracted:
                        knowledge_items.append(
                            KnowledgeItem(
                                title=item["title"],
                                content=item["content"],
                                category=item["category"],
                                date=note.date,
                                source_note=note.file_name,
                            )
                        )
            except Exception as e:
                print(f"Error processing note {note.file_name}: {e}")

        return knowledge_items

    def summarize_post(self, title: str, url: str, content: str) -> str:
        """Summarize a LessWrong post using AI."""
        # Truncate content to avoid token limits
        truncated_content = content[:3000]
        if len(content) > 3000:
            truncated_content += "..."

        prompt = f"""Please provide a concise 2-3 sentence summary of this LessWrong post:

Title: {title}
URL: {url}

Content:
{truncated_content}

Focus on the key insights and main points. Keep it brief and informative."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )

            summary = message.content[0].text.strip()
            return summary
        except Exception as e:
            print(f'Error summarizing post "{title}": {e}')
            return "Summary unavailable."
