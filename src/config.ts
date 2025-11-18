import * as dotenv from 'dotenv';
import * as path from 'path';
import { Config } from './types';

dotenv.config();

export function loadConfig(): Config {
  const anthropicApiKey = process.env.ANTHROPIC_API_KEY;
  if (!anthropicApiKey) {
    throw new Error('ANTHROPIC_API_KEY environment variable is required');
  }

  const vaultPath = process.env.OBSIDIAN_VAULT_PATH;
  if (!vaultPath) {
    throw new Error('OBSIDIAN_VAULT_PATH environment variable is required');
  }

  return {
    anthropicApiKey,
    vaultPath: path.resolve(vaultPath),
    dailyNotesFolder: process.env.DAILY_NOTES_FOLDER || 'Daily Notes',
    knowledgeRepoFolder: process.env.KNOWLEDGE_REPO_FOLDER || 'Knowledge Base',
    lookbackDays: parseInt(process.env.LOOKBACK_DAYS || '1', 10),
    lesswrongPostCount: parseInt(process.env.LESSWRONG_POST_COUNT || '5', 10),
  };
}
