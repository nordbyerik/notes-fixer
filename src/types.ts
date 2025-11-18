export interface Config {
  anthropicApiKey: string;
  vaultPath: string;
  dailyNotesFolder: string;
  knowledgeRepoFolder: string;
  lookbackDays: number;
  lesswrongPostCount: number;
}

export interface DailyNote {
  path: string;
  fileName: string;
  date: Date;
  content: string;
}

export interface KnowledgeItem {
  title: string;
  content: string;
  category: string;
  date: Date;
  sourceNote: string;
}

export interface LessWrongPost {
  id: string;
  title: string;
  author: string;
  url: string;
  baseScore: number;
  postedAt: string;
  content: string;
  summary?: string;
}
