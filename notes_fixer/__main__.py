#!/usr/bin/env python3
"""Main CLI entry point for the notes fixer tool."""

import argparse
import sys
from typing import List
from .config import load_config
from .notes_reader import NotesReader
from .ai_processor import AIProcessor
from .lesswrong import LessWrongScraper
from .rss_scraper import RSSFeedScraper
from .base_scraper import BaseScraper


def cmd_run(args):
    """Run the daily notes processing (extract knowledge + fetch from all scrapers)."""
    try:
        print("Starting daily notes processing...\n")

        config = load_config()
        notes_reader = NotesReader(config)
        ai_processor = AIProcessor(config)

        # Step 1: Extract knowledge from recent daily notes
        print("Step 1: Extracting knowledge from recent notes...")
        recent_notes = notes_reader.get_recent_daily_notes()
        print(f"Found {len(recent_notes)} recent notes to process.\n")

        if recent_notes:
            knowledge_items = ai_processor.extract_knowledge_from_notes(recent_notes)
            print(f"Extracted {len(knowledge_items)} knowledge items.\n")

            # Save knowledge items to knowledge repository
            for item in knowledge_items:
                print(f"Saving: {item.title} -> {item.category}")
                notes_reader.save_knowledge_item(item.category, item.title, item.content)

            if knowledge_items:
                print("\nKnowledge items saved to repository!\n")

        # Step 2: Fetch content from all enabled scrapers
        print("Step 2: Fetching content from scrapers...")
        scrapers: List[BaseScraper] = []

        # Add LessWrong scraper if enabled
        if config.lesswrong_enabled:
            scrapers.append(LessWrongScraper(config.lesswrong_post_count, ai_processor))

        # Add RSS scrapers if configured
        if config.rss_feed_urls:
            scrapers.append(RSSFeedScraper(config.rss_feed_urls, ai_processor, config.rss_items_per_feed))

        if not scrapers:
            print("No scrapers enabled. Set LESSWRONG_ENABLED=true or configure RSS_FEEDS to fetch content.")
            return

        # Fetch and format content from all scrapers
        news_sections: List[str] = []
        for scraper in scrapers:
            print(f"\nFetching from {scraper.name}...")
            items = scraper.fetch_items()
            if items:
                formatted = scraper.format_for_daily_note(items)
                news_sections.append(f"## {scraper.name}\n\n{formatted}")
            else:
                print(f"No items found from {scraper.name}")

        if news_sections:
            combined_news = "\n\n".join(news_sections)
            notes_reader.update_today_note_with_news(combined_news)
            print("\n✓ Content added to today's note!")

        print("\n✓ Daily notes processing complete!")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_extract_knowledge(args):
    """Extract knowledge from recent daily notes only."""
    try:
        config = load_config()
        notes_reader = NotesReader(config)
        ai_processor = AIProcessor(config)

        print("Extracting knowledge from recent notes...")
        recent_notes = notes_reader.get_recent_daily_notes()
        print(f"Found {len(recent_notes)} recent notes to process.\n")

        if not recent_notes:
            print("No recent notes found.")
            return

        knowledge_items = ai_processor.extract_knowledge_from_notes(recent_notes)
        print(f"Extracted {len(knowledge_items)} knowledge items.\n")

        for item in knowledge_items:
            print(f"Saving: {item.title} -> {item.category}")
            notes_reader.save_knowledge_item(item.category, item.title, item.content)

        print("\n✓ Knowledge extraction complete!")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_fetch_content(args):
    """Fetch content from all scrapers and add to today's note."""
    try:
        config = load_config()
        notes_reader = NotesReader(config)
        ai_processor = AIProcessor(config)

        scrapers: List[BaseScraper] = []

        # Add LessWrong scraper if enabled
        if config.lesswrong_enabled:
            scrapers.append(LessWrongScraper(config.lesswrong_post_count, ai_processor))

        # Add RSS scrapers if configured
        if config.rss_feed_urls:
            scrapers.append(RSSFeedScraper(config.rss_feed_urls, ai_processor, config.rss_items_per_feed))

        if not scrapers:
            print("No scrapers enabled. Set LESSWRONG_ENABLED=true or configure RSS_FEEDS to fetch content.")
            return

        # Fetch and format content from all scrapers
        news_sections: List[str] = []
        for scraper in scrapers:
            print(f"Fetching from {scraper.name}...")
            items = scraper.fetch_items()
            if items:
                formatted = scraper.format_for_daily_note(items)
                news_sections.append(f"## {scraper.name}\n\n{formatted}")
            else:
                print(f"No items found from {scraper.name}")

        if news_sections:
            combined_news = "\n\n".join(news_sections)
            notes_reader.update_today_note_with_news(combined_news)
            print("\n✓ Content added to today's note!")
        else:
            print("No content fetched from any scraper.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CLI tool for managing daily Obsidian notes with AI-powered knowledge extraction"
    )
    parser.add_argument(
        "--version", action="version", version="notes-fixer 1.0.0"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run command
    parser_run = subparsers.add_parser(
        "run", help="Run the full workflow (extract knowledge + fetch from all scrapers)"
    )
    parser_run.set_defaults(func=cmd_run)

    # Extract knowledge command
    parser_extract = subparsers.add_parser(
        "extract-knowledge", help="Extract knowledge from recent daily notes only"
    )
    parser_extract.set_defaults(func=cmd_extract_knowledge)

    # Fetch content command
    parser_fetch = subparsers.add_parser(
        "fetch-content", help="Fetch content from all enabled scrapers (LessWrong, RSS feeds, etc.)"
    )
    parser_fetch.set_defaults(func=cmd_fetch_content)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
