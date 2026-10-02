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

/**
 * The guide: a series of textbook-style chapters on the core of computer
 * science, written in dependency order.
 *
 * This lives in its own collection rather than in `notes` because the two are
 * read differently. A note is a finished, standalone piece; a chapter is one
 * instalment of a numbered series with an ordering, a prerequisite list, and a
 * next/previous neighbour. Keeping them apart means /notes/ and the dashboard
 * keep working exactly as before, and a chapter's URL never collides with a
 * note's.
 *
 * `index.md` is the series landing page: it is the only entry with
 * `kind: index`, and it is where the outline and the progress list live.
 */
const guide = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/guide' }),
  schema: z.object({
    kind: z.enum(['index', 'chapter']).default('chapter'),
    title: z.string(),
    short: z.string().optional(),
    summary: z.string().optional(),
    date: z.coerce.date(),
    order: z.number().default(0),
    part: z.string().default(''),
    prereq: z.string().optional(),
    ready: z.boolean().default(false),
    reading: z.string().optional(),
    tags: z.array(z.string()).default([]),
    lang: z.string().default('zh'),
    draft: z.boolean().default(false),
    steps: z
      .array(
        z.object({
          part: z.string(),
          items: z.array(
            z.object({
              title: z.string(),
              href: z.string().optional(),
              note: z.string().optional(),
              state: z.enum(['done', 'current', 'next', 'planned']).default('planned'),
            })
          ),
        })
      )
      .default([]),
  }),
});

export const collections = { notes, guide };
