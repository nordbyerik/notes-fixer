# Obsidian Daily Notes CLI

A powerful CLI tool for managing your daily Obsidian notes with AI-powered knowledge extraction and LessWrong integration.

## Features

- **AI-Powered Knowledge Extraction**: Automatically extracts important insights, events, and learnings from your daily notes and organizes them into a knowledge repository
- **LessWrong Integration**: Fetches top posts from LessWrong and adds AI-generated summaries to your daily notes
- **Automated Daily Workflow**: Designed to run once per day (via cron) to keep your knowledge base up-to-date

## Prerequisites

- Node.js 18+ and npm
- An Obsidian vault with a daily notes folder
- Anthropic API key (for Claude AI)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd notes-fixer
```

2. Install dependencies:
```bash
npm install
```

3. Build the project:
```bash
npm run build
```

4. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

5. Configure your `.env` file with your settings:
```env
ANTHROPIC_API_KEY=your_api_key_here
OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
DAILY_NOTES_FOLDER=Daily Notes
KNOWLEDGE_REPO_FOLDER=Knowledge Base
LOOKBACK_DAYS=1
LESSWRONG_POST_COUNT=5
```

## Usage

### Run Everything (Recommended for Daily Use)

Process recent notes and add LessWrong posts in one command:

```bash
npm start run
```

Or using the compiled binary:

```bash
node dist/index.js run
```

### Extract Knowledge Only

Only extract knowledge from recent daily notes:

```bash
npm start extract-knowledge
```

### LessWrong Posts Only

Only fetch and add LessWrong posts to today's note:

```bash
npm start lesswrong
```

## Setting Up Daily Automation

To run this tool automatically once per day, set up a cron job:

1. Open your crontab:
```bash
crontab -e
```

2. Add a line to run the tool daily (example: every day at 9 AM):
```bash
0 9 * * * cd /path/to/notes-fixer && /usr/bin/node dist/index.js run >> /tmp/notes-fixer.log 2>&1
```

Make sure to:
- Replace `/path/to/notes-fixer` with the actual path
- Replace `/usr/bin/node` with your Node.js path (find it with `which node`)
- Ensure your `.env` file is properly configured

## How It Works

### Knowledge Extraction

1. Reads daily notes from the specified lookback period (default: 1 day)
2. Uses Claude AI to analyze each note and extract:
   - Important ideas
   - Notable events
   - Key learnings
   - Project updates
   - People mentions
   - Useful resources
3. Saves extracted items to categorized folders in your Knowledge Base:
   - `Knowledge Base/Ideas/`
   - `Knowledge Base/Events/`
   - `Knowledge Base/Learnings/`
   - `Knowledge Base/Projects/`
   - `Knowledge Base/People/`
   - `Knowledge Base/Resources/`

### LessWrong Integration

1. Fetches top recent posts from LessWrong using their GraphQL API
2. Generates concise summaries of each post using Claude AI
3. Adds summaries to a "Daily News" section in today's daily note
4. Includes links, authors, and scores for each post

## Folder Structure

```
notes-fixer/
├── src/
│   ├── index.ts           # Main CLI entry point
│   ├── config.ts          # Configuration loader
│   ├── types.ts           # TypeScript type definitions
│   ├── notesReader.ts     # Daily notes reader and file operations
│   ├── aiProcessor.ts     # AI-powered knowledge extraction
│   └── lesswrong.ts       # LessWrong API integration
├── dist/                  # Compiled JavaScript (generated)
├── .env                   # Your configuration (create from .env.example)
├── .env.example           # Configuration template
├── package.json
├── tsconfig.json
└── README.md
```

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | (required) |
| `OBSIDIAN_VAULT_PATH` | Absolute path to your Obsidian vault | (required) |
| `DAILY_NOTES_FOLDER` | Folder containing daily notes | `Daily Notes` |
| `KNOWLEDGE_REPO_FOLDER` | Folder for knowledge repository | `Knowledge Base` |
| `LOOKBACK_DAYS` | Number of days to look back for new notes | `1` |
| `LESSWRONG_POST_COUNT` | Number of LessWrong posts to fetch | `5` |

## Development

Run in development mode with auto-reload:

```bash
npm run dev
```

Build the project:

```bash
npm run build
```

Watch mode (auto-rebuild on changes):

```bash
npm run watch
```

## Troubleshooting

**Error: ANTHROPIC_API_KEY environment variable is required**
- Make sure you've created a `.env` file and added your API key

**Error: OBSIDIAN_VAULT_PATH environment variable is required**
- Set the correct path to your Obsidian vault in `.env`

**No notes found**
- Check that your daily notes folder path is correct
- Ensure your daily notes are `.md` files
- Verify the `LOOKBACK_DAYS` setting

**LessWrong posts not loading**
- Check your internet connection
- The LessWrong API may be temporarily unavailable

## License

MIT

## Contributing

Pull requests are welcome! Please feel free to submit issues for bugs or feature requests.
