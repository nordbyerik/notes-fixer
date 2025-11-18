"""Configuration loader for the notes fixer tool."""

import os
from pathlib import Path
from dotenv import load_dotenv
from .types import Config


def load_config() -> Config:
    """Load configuration from environment variables."""
    load_dotenv()

    # Model configuration - defaults to Claude
    ai_model = os.getenv("AI_MODEL", "claude-sonnet-4-20250514")

    # API key - try AI_API_KEY first, then fall back to ANTHROPIC_API_KEY for backward compatibility
    ai_api_key = os.getenv("AI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

    # API key is optional for local models (e.g., ollama/llama3)
    if not ai_api_key and not ai_model.startswith("ollama/"):
        raise ValueError("AI_API_KEY or ANTHROPIC_API_KEY environment variable is required for cloud models")

    vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
    if not vault_path:
        raise ValueError("OBSIDIAN_VAULT_PATH environment variable is required")

    return Config(
        ai_model=ai_model,
        ai_api_key=ai_api_key,
        vault_path=str(Path(vault_path).resolve()),
        daily_notes_folder=os.getenv("DAILY_NOTES_FOLDER", "Daily Notes"),
        knowledge_repo_folder=os.getenv("KNOWLEDGE_REPO_FOLDER", "Knowledge Base"),
        lookback_days=int(os.getenv("LOOKBACK_DAYS", "1")),
        lesswrong_post_count=int(os.getenv("LESSWRONG_POST_COUNT", "5")),
    )
