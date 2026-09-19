import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * One collection: the notes that live in this repository.
 *
 * The file name becomes the entry id, which becomes the URL
 * (src/content/notes/site-workflow.md -> /notes/site-workflow.html).
 * Renaming a file therefore breaks a published link — change `title` instead.
 */
const notes = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/notes' }),
  schema: z.object({
    title: z.string(),
    summary: z.string().optional(),
    date: z.coerce.date(),
    category: z.string().default('Site notes'),
    tags: z.array(z.string()).default([]),
    lang: z.string().default('zh'),
    draft: z.boolean().default(false),
  }),
});

export const collections = { notes };
