import Anthropic from '@anthropic-ai/sdk';
import { Config, DailyNote, KnowledgeItem } from './types';

export class AIProcessor {
  private client: Anthropic;

  constructor(private config: Config) {
    this.client = new Anthropic({
      apiKey: config.anthropicApiKey,
    });
  }

  /**
   * Extract knowledge items from daily notes using AI
   */
  async extractKnowledgeFromNotes(notes: DailyNote[]): Promise<KnowledgeItem[]> {
    if (notes.length === 0) {
      return [];
    }

    const knowledgeItems: KnowledgeItem[] = [];

    for (const note of notes) {
      console.log(`Processing note: ${note.fileName}`);

      const prompt = `You are analyzing a daily note from an Obsidian vault. Your task is to extract important knowledge, cool events, interesting insights, and valuable information that should be saved to a personal knowledge repository.

Please analyze the following daily note and extract important items:

${note.content}

For each important item you find, provide:
1. A clear title
2. The content/description
3. A category (choose from: Ideas, Events, Learnings, Projects, People, Resources, or Other)

Format your response as JSON array of objects with fields: title, content, category

Only extract items that are genuinely interesting or valuable. Skip mundane daily tasks or trivial entries.

If there are no important items to extract, return an empty array.`;

      try {
        const message = await this.client.messages.create({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 4096,
          messages: [
            {
              role: 'user',
              content: prompt,
            },
          ],
        });

        const responseText = message.content[0].type === 'text' ? message.content[0].text : '';

        // Extract JSON from response (handle both raw JSON and markdown code blocks)
        let jsonStr = responseText.trim();
        const codeBlockMatch = jsonStr.match(/```(?:json)?\n([\s\S]*?)\n```/);
        if (codeBlockMatch) {
          jsonStr = codeBlockMatch[1];
        }

        const extracted = JSON.parse(jsonStr);

        if (Array.isArray(extracted)) {
          for (const item of extracted) {
            knowledgeItems.push({
              title: item.title,
              content: item.content,
              category: item.category,
              date: note.date,
              sourceNote: note.fileName,
            });
          }
        }
      } catch (error) {
        console.error(`Error processing note ${note.fileName}:`, error);
      }
    }

    return knowledgeItems;
  }

  /**
   * Summarize a LessWrong post using AI
   */
  async summarizePost(title: string, url: string, content: string): Promise<string> {
    const prompt = `Please provide a concise 2-3 sentence summary of this LessWrong post:

Title: ${title}
URL: ${url}

Content:
${content.substring(0, 3000)} ${content.length > 3000 ? '...' : ''}

Focus on the key insights and main points. Keep it brief and informative.`;

    try {
      const message = await this.client.messages.create({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 500,
        messages: [
          {
            role: 'user',
            content: prompt,
          },
        ],
      });

      const summary = message.content[0].type === 'text' ? message.content[0].text : '';
      return summary.trim();
    } catch (error) {
      console.error(`Error summarizing post "${title}":`, error);
      return 'Summary unavailable.';
    }
  }
}
