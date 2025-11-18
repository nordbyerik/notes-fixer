"""Configuration loader for the notes fixer tool."""

import os
from pathlib import Path
from dotenv import load_dotenv
from .types import Config


def load_config() -> Config:
    """Load configuration from environment variables."""
    load_dotenv()

    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")

    vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
    if not vault_path:
        raise ValueError("OBSIDIAN_VAULT_PATH environment variable is required")

    return Config(
        anthropic_api_key=anthropic_api_key,
        vault_path=str(Path(vault_path).resolve()),
        daily_notes_folder=os.getenv("DAILY_NOTES_FOLDER", "Daily Notes"),
        knowledge_repo_folder=os.getenv("KNOWLEDGE_REPO_FOLDER", "Knowledge Base"),
        lookback_days=int(os.getenv("LOOKBACK_DAYS", "1")),
        lesswrong_post_count=int(os.getenv("LESSWRONG_POST_COUNT", "5")),
    )
