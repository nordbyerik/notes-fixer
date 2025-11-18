"""AI processor for extracting knowledge and summarizing content."""

import json
import os
import re
from typing import List
from litellm import completion
from .types import Config, DailyNote, KnowledgeItem


class AIProcessor:
    """Handles AI-powered processing using any LLM provider."""

    def __init__(self, config: Config):
        self.config = config
        self.model = config.ai_model

        # Set API key as environment variable for LiteLLM
        if config.ai_api_key:
            # LiteLLM automatically detects the provider from the model name
            # and uses the appropriate env var (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.)
            if config.ai_model.startswith("claude"):
                os.environ["ANTHROPIC_API_KEY"] = config.ai_api_key
            elif config.ai_model.startswith("gpt"):
                os.environ["OPENAI_API_KEY"] = config.ai_api_key
            else:
                # For other providers, set a generic API key
                os.environ["LITELLM_API_KEY"] = config.ai_api_key

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
                response = completion(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4096,
                )

                response_text = response.choices[0].message.content

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
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
            )

            summary = response.choices[0].message.content.strip()
            return summary
        except Exception as e:
            print(f'Error summarizing post "{title}": {e}')
            return "Summary unavailable."
