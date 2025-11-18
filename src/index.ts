#!/usr/bin/env node

import { Command } from 'commander';
import { loadConfig } from './config';
import { NotesReader } from './notesReader';
import { AIProcessor } from './aiProcessor';
import { LessWrongIntegration } from './lesswrong';

const program = new Command();

program
  .name('notes-fixer')
  .description('CLI tool for managing daily Obsidian notes with AI-powered knowledge extraction')
  .version('1.0.0');

program
  .command('run')
  .description('Run the daily notes processing (extract knowledge + add LessWrong posts)')
  .action(async () => {
    try {
      console.log('Starting daily notes processing...\n');

      const config = loadConfig();
      const notesReader = new NotesReader(config);
      const aiProcessor = new AIProcessor(config);
      const lesswrong = new LessWrongIntegration(config, aiProcessor);

      // Step 1: Extract knowledge from recent daily notes
      console.log('Step 1: Extracting knowledge from recent notes...');
      const recentNotes = await notesReader.getRecentDailyNotes();
      console.log(`Found ${recentNotes.length} recent notes to process.\n`);

      if (recentNotes.length > 0) {
        const knowledgeItems = await aiProcessor.extractKnowledgeFromNotes(recentNotes);
        console.log(`Extracted ${knowledgeItems.length} knowledge items.\n`);

        // Save knowledge items to knowledge repository
        for (const item of knowledgeItems) {
          console.log(`Saving: ${item.title} -> ${item.category}`);
          notesReader.saveKnowledgeItem(item.category, item.title, item.content);
        }

        if (knowledgeItems.length > 0) {
          console.log('\nKnowledge items saved to repository!\n');
        }
      }

      // Step 2: Fetch and add LessWrong posts to today's note
      console.log('Step 2: Fetching LessWrong posts...');
      const newsSection = await lesswrong.fetchAndSummarizePosts();

      notesReader.updateTodayNoteWithNews(newsSection);
      console.log('\nLessWrong posts added to today\'s note!\n');

      console.log('✓ Daily notes processing complete!');
    } catch (error) {
      console.error('Error:', error instanceof Error ? error.message : error);
      process.exit(1);
    }
  });

program
  .command('extract-knowledge')
  .description('Extract knowledge from recent daily notes only')
  .action(async () => {
    try {
      const config = loadConfig();
      const notesReader = new NotesReader(config);
      const aiProcessor = new AIProcessor(config);

      console.log('Extracting knowledge from recent notes...');
      const recentNotes = await notesReader.getRecentDailyNotes();
      console.log(`Found ${recentNotes.length} recent notes to process.\n`);

      if (recentNotes.length === 0) {
        console.log('No recent notes found.');
        return;
      }

      const knowledgeItems = await aiProcessor.extractKnowledgeFromNotes(recentNotes);
      console.log(`Extracted ${knowledgeItems.length} knowledge items.\n`);

      for (const item of knowledgeItems) {
        console.log(`Saving: ${item.title} -> ${item.category}`);
        notesReader.saveKnowledgeItem(item.category, item.title, item.content);
      }

      console.log('\n✓ Knowledge extraction complete!');
    } catch (error) {
      console.error('Error:', error instanceof Error ? error.message : error);
      process.exit(1);
    }
  });

program
  .command('lesswrong')
  .description('Fetch LessWrong posts and add to today\'s note only')
  .action(async () => {
    try {
      const config = loadConfig();
      const notesReader = new NotesReader(config);
      const aiProcessor = new AIProcessor(config);
      const lesswrong = new LessWrongIntegration(config, aiProcessor);

      console.log('Fetching LessWrong posts...');
      const newsSection = await lesswrong.fetchAndSummarizePosts();

      notesReader.updateTodayNoteWithNews(newsSection);
      console.log('\n✓ LessWrong posts added to today\'s note!');
    } catch (error) {
      console.error('Error:', error instanceof Error ? error.message : error);
      process.exit(1);
    }
  });

program.parse();
