import fetch from 'node-fetch';
import { Config, LessWrongPost } from './types';
import { AIProcessor } from './aiProcessor';

export class LessWrongIntegration {
  private readonly GRAPHQL_ENDPOINT = 'https://www.lesswrong.com/graphql';

  constructor(
    private config: Config,
    private aiProcessor: AIProcessor
  ) {}

  /**
   * Fetch top recent posts from LessWrong
   */
  async fetchTopPosts(): Promise<LessWrongPost[]> {
    const query = `
      query RecentPosts {
        posts(input: {
          terms: {
            view: "magic"
            limit: ${this.config.lesswrongPostCount}
            filter: "frontpage"
          }
        }) {
          results {
            _id
            title
            slug
            baseScore
            postedAt
            user {
              displayName
            }
            contents {
              plaintextDescription
            }
          }
        }
      }
    `;

    try {
      const response = await fetch(this.GRAPHQL_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      const data: any = await response.json();

      if (data.errors) {
        console.error('GraphQL errors:', data.errors);
        return [];
      }

      const posts = data.data.posts.results;

      return posts.map((post: any) => ({
        id: post._id,
        title: post.title,
        author: post.user?.displayName || 'Unknown',
        url: `https://www.lesswrong.com/posts/${post._id}/${post.slug}`,
        baseScore: post.baseScore,
        postedAt: post.postedAt,
        content: post.contents?.plaintextDescription || '',
      }));
    } catch (error) {
      console.error('Error fetching LessWrong posts:', error);
      return [];
    }
  }

  /**
   * Fetch and summarize top posts
   */
  async fetchAndSummarizePosts(): Promise<string> {
    console.log('Fetching top LessWrong posts...');
    const posts = await this.fetchTopPosts();

    if (posts.length === 0) {
      return 'No posts available.';
    }

    console.log(`Found ${posts.length} posts. Generating summaries...`);

    const summaries: string[] = [];

    for (const post of posts) {
      const summary = await this.aiProcessor.summarizePost(
        post.title,
        post.url,
        post.content
      );

      const formattedPost = `### [${post.title}](${post.url})
**Author:** ${post.author} | **Score:** ${post.baseScore}

${summary}`;

      summaries.push(formattedPost);
    }

    return summaries.join('\n\n');
  }
}
