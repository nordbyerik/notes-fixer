#!/usr/bin/env python3
"""Main CLI entry point for the notes fixer tool."""

import argparse
import sys
from .config import load_config
from .notes_reader import NotesReader
from .ai_processor import AIProcessor
from .lesswrong import LessWrongIntegration


def cmd_run(args):
    """Run the daily notes processing (extract knowledge + add LessWrong posts)."""
    try:
        print("Starting daily notes processing...\n")

        config = load_config()
        notes_reader = NotesReader(config)
        ai_processor = AIProcessor(config)
        lesswrong = LessWrongIntegration(config, ai_processor)

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

        # Step 2: Fetch and add LessWrong posts to today's note
        print("Step 2: Fetching LessWrong posts...")
        news_section = lesswrong.fetch_and_summarize_posts()

        notes_reader.update_today_note_with_news(news_section)
        print("\nLessWrong posts added to today's note!\n")

        print("✓ Daily notes processing complete!")
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


def cmd_lesswrong(args):
    """Fetch LessWrong posts and add to today's note only."""
    try:
        config = load_config()
        notes_reader = NotesReader(config)
        ai_processor = AIProcessor(config)
        lesswrong = LessWrongIntegration(config, ai_processor)

        print("Fetching LessWrong posts...")
        news_section = lesswrong.fetch_and_summarize_posts()

        notes_reader.update_today_note_with_news(news_section)
        print("\n✓ LessWrong posts added to today's note!")
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
        "run", help="Run the daily notes processing (extract knowledge + add LessWrong posts)"
    )
    parser_run.set_defaults(func=cmd_run)

    # Extract knowledge command
    parser_extract = subparsers.add_parser(
        "extract-knowledge", help="Extract knowledge from recent daily notes only"
    )
    parser_extract.set_defaults(func=cmd_extract_knowledge)

    # LessWrong command
    parser_lesswrong = subparsers.add_parser(
        "lesswrong", help="Fetch LessWrong posts and add to today's note only"
    )
    parser_lesswrong.set_defaults(func=cmd_lesswrong)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
