"""Notes reader for managing Obsidian daily notes."""

import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
from .types import Config, DailyNote


class NotesReader:
    """Handles reading and writing Obsidian notes."""

    def __init__(self, config: Config):
        self.config = config

    def get_recent_daily_notes(self) -> List[DailyNote]:
        """Get all daily notes from the specified lookback period."""
        daily_notes_path = Path(self.config.vault_path) / self.config.daily_notes_folder

        if not daily_notes_path.exists():
            print(f"Daily notes folder not found: {daily_notes_path}")
            return []

        notes: List[DailyNote] = []
        cutoff_date = datetime.now() - timedelta(days=self.config.lookback_days)

        for file_path in daily_notes_path.glob("*.md"):
            stats = file_path.stat()
            mtime = datetime.fromtimestamp(stats.st_mtime)

            # Check if file was modified within lookback period
            if mtime >= cutoff_date:
                content = file_path.read_text(encoding="utf-8")
                notes.append(
                    DailyNote(
                        path=str(file_path),
                        file_name=file_path.name,
                        date=mtime,
                        content=content,
                    )
                )

        # Sort by date, newest first
        notes.sort(key=lambda n: n.date, reverse=True)
        return notes

    def get_today_note(self) -> Dict[str, any]:
        """Get the current day's daily note, or create it if it doesn't exist."""
        today = datetime.now()
        date_str = today.strftime("%Y-%m-%d")
        file_name = f"{date_str}.md"
        daily_notes_path = Path(self.config.vault_path) / self.config.daily_notes_folder
        note_path = daily_notes_path / file_name

        # Ensure daily notes folder exists
        daily_notes_path.mkdir(parents=True, exist_ok=True)

        exists = note_path.exists()
        content = ""

        if exists:
            content = note_path.read_text(encoding="utf-8")
        else:
            # Create a new note with basic structure
            content = f"# {date_str}\n\n## Daily News\n\n## Notes\n\n"
            note_path.write_text(content, encoding="utf-8")

        return {"path": str(note_path), "content": content, "exists": exists}

    def update_today_note_with_news(self, news_section: str) -> None:
        """Update today's note with LessWrong posts."""
        note_info = self.get_today_note()
        note_path = Path(note_info["path"])
        content = note_info["content"]

        # Find or create the Daily News section
        news_section_regex = r"## Daily News\n([\s\S]*?)(?=\n## |\n#|$)"
        match = re.search(news_section_regex, content)

        if match:
            # Replace existing Daily News section
            updated_content = re.sub(
                news_section_regex,
                f"## Daily News\n\n{news_section}\n",
                content,
            )
        else:
            # Add Daily News section after the title
            lines = content.split("\n")
            title_index = next(
                (i for i, line in enumerate(lines) if line.startswith("# ")), None
            )
            if title_index is not None:
                lines.insert(title_index + 1, "")
                lines.insert(title_index + 2, "## Daily News")
                lines.insert(title_index + 3, "")
                lines.insert(title_index + 4, news_section)
                lines.insert(title_index + 5, "")
                updated_content = "\n".join(lines)
            else:
                updated_content = content + "\n\n## Daily News\n\n" + news_section

        note_path.write_text(updated_content, encoding="utf-8")

    def ensure_knowledge_repo_exists(self) -> Path:
        """Ensure knowledge repo folder exists."""
        knowledge_repo_path = Path(self.config.vault_path) / self.config.knowledge_repo_folder
        knowledge_repo_path.mkdir(parents=True, exist_ok=True)
        return knowledge_repo_path

    def save_knowledge_item(self, category: str, title: str, content: str) -> None:
        """Save a knowledge item to the knowledge repo."""
        knowledge_repo_path = self.ensure_knowledge_repo_exists()
        category_path = knowledge_repo_path / category
        category_path.mkdir(parents=True, exist_ok=True)

        # Sanitize title for filename
        sanitized_title = re.sub(r"[^a-zA-Z0-9\s-]", "", title)
        sanitized_title = re.sub(r"\s+", "-", sanitized_title).lower()

        file_name = f"{sanitized_title}.md"
        file_path = category_path / file_name

        # Check if file already exists
        if file_path.exists():
            # Append to existing file
            existing_content = file_path.read_text(encoding="utf-8")
            separator = "\n\n---\n\n"
            updated_content = existing_content + separator + content
            file_path.write_text(updated_content, encoding="utf-8")
        else:
            # Create new file
            full_content = f"# {title}\n\n{content}"
            file_path.write_text(full_content, encoding="utf-8")
