import * as fs from 'fs';
import * as path from 'path';
import { Config, DailyNote } from './types';

export class NotesReader {
  constructor(private config: Config) {}

  /**
   * Get all daily notes from the specified lookback period
   */
  async getRecentDailyNotes(): Promise<DailyNote[]> {
    const dailyNotesPath = path.join(this.config.vaultPath, this.config.dailyNotesFolder);

    if (!fs.existsSync(dailyNotesPath)) {
      console.log(`Daily notes folder not found: ${dailyNotesPath}`);
      return [];
    }

    const files = fs.readdirSync(dailyNotesPath);
    const markdownFiles = files.filter(f => f.endsWith('.md'));

    const notes: DailyNote[] = [];
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - this.config.lookbackDays);

    for (const fileName of markdownFiles) {
      const filePath = path.join(dailyNotesPath, fileName);
      const stats = fs.statSync(filePath);

      // Check if file was modified within lookback period
      if (stats.mtime >= cutoffDate) {
        const content = fs.readFileSync(filePath, 'utf-8');
        notes.push({
          path: filePath,
          fileName,
          date: stats.mtime,
          content,
        });
      }
    }

    return notes.sort((a, b) => b.date.getTime() - a.date.getTime());
  }

  /**
   * Get the current day's daily note, or create it if it doesn't exist
   */
  getTodayNote(): { path: string; content: string; exists: boolean } {
    const today = new Date();
    const dateStr = today.toISOString().split('T')[0]; // YYYY-MM-DD
    const fileName = `${dateStr}.md`;
    const dailyNotesPath = path.join(this.config.vaultPath, this.config.dailyNotesFolder);
    const notePath = path.join(dailyNotesPath, fileName);

    // Ensure daily notes folder exists
    if (!fs.existsSync(dailyNotesPath)) {
      fs.mkdirSync(dailyNotesPath, { recursive: true });
    }

    const exists = fs.existsSync(notePath);
    let content = '';

    if (exists) {
      content = fs.readFileSync(notePath, 'utf-8');
    } else {
      // Create a new note with basic structure
      content = `# ${dateStr}\n\n## Daily News\n\n## Notes\n\n`;
      fs.writeFileSync(notePath, content);
    }

    return { path: notePath, content, exists };
  }

  /**
   * Update today's note with LessWrong posts
   */
  updateTodayNoteWithNews(newsSection: string): void {
    const { path: notePath, content } = this.getTodayNote();

    // Find or create the Daily News section
    const newsSectionRegex = /## Daily News\n([\s\S]*?)(?=\n## |\n#|$)/;
    const match = content.match(newsSectionRegex);

    let updatedContent: string;
    if (match) {
      // Replace existing Daily News section
      updatedContent = content.replace(
        newsSectionRegex,
        `## Daily News\n\n${newsSection}\n`
      );
    } else {
      // Add Daily News section after the title
      const lines = content.split('\n');
      const titleIndex = lines.findIndex(line => line.startsWith('# '));
      if (titleIndex !== -1) {
        lines.splice(titleIndex + 1, 0, '', '## Daily News', '', newsSection, '');
        updatedContent = lines.join('\n');
      } else {
        updatedContent = content + '\n\n## Daily News\n\n' + newsSection;
      }
    }

    fs.writeFileSync(notePath, updatedContent);
  }

  /**
   * Ensure knowledge repo folder exists
   */
  ensureKnowledgeRepoExists(): string {
    const knowledgeRepoPath = path.join(this.config.vaultPath, this.config.knowledgeRepoFolder);

    if (!fs.existsSync(knowledgeRepoPath)) {
      fs.mkdirSync(knowledgeRepoPath, { recursive: true });
    }

    return knowledgeRepoPath;
  }

  /**
   * Save a knowledge item to the knowledge repo
   */
  saveKnowledgeItem(category: string, title: string, content: string): void {
    const knowledgeRepoPath = this.ensureKnowledgeRepoExists();
    const categoryPath = path.join(knowledgeRepoPath, category);

    if (!fs.existsSync(categoryPath)) {
      fs.mkdirSync(categoryPath, { recursive: true });
    }

    // Sanitize title for filename
    const sanitizedTitle = title
      .replace(/[^a-zA-Z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .toLowerCase();

    const fileName = `${sanitizedTitle}.md`;
    const filePath = path.join(categoryPath, fileName);

    // Check if file already exists
    if (fs.existsSync(filePath)) {
      // Append to existing file
      const existingContent = fs.readFileSync(filePath, 'utf-8');
      const separator = '\n\n---\n\n';
      const updatedContent = existingContent + separator + content;
      fs.writeFileSync(filePath, updatedContent);
    } else {
      // Create new file
      const fullContent = `# ${title}\n\n${content}`;
      fs.writeFileSync(filePath, fullContent);
    }
  }
}
