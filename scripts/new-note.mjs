#!/usr/bin/env node
/**
 * Scaffold a new note.
 *
 *   npm run new <slug>
 *   npm run new <slug> -- --title "The title you want"
 *
 * Copies templates/new-note.md to src/content/notes/<slug>.md and stamps
 * today's date into the frontmatter. Everything else — the dashboard entry,
 * the category section, the tag pages, the contents drawer on the page — is
 * generated at build time, so there is nothing else to touch.
 *
 * The slug is the URL: src/content/notes/hash-basics.md is served at
 * /notes/hash-basics.html. Pick it once and leave it alone.
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const TEMPLATE = resolve(ROOT, 'templates/new-note.md');
const NOTES_DIR = resolve(ROOT, 'src/content/notes');

const args = process.argv.slice(2);
let title = null;
const positional = [];
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === '--title' || a === '-t') { title = args[++i] ?? null; continue; }
  if (a.startsWith('-')) continue;
  positional.push(a);
}
const slug = positional[0];

function usage(problem) {
  if (problem) console.error(`error: ${problem}\n`);
  console.error('usage: npm run new <slug> [-- --title "The title"]\n');
  console.error('  <slug>   kebab-case, becomes the file name and the URL');
  console.error('           e.g. hash-basics  ->  /notes/hash-basics.html\n');
  console.error('  The file is created from templates/new-note.md and opens with');
  console.error('  today\'s date. Edit it, then npm run build && git push.');
  process.exit(1);
}

if (!slug) usage('no slug given');
if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) {
  usage(`"${slug}" is not kebab-case (lowercase letters, digits, single hyphens)`);
}
if (!existsSync(TEMPLATE)) usage(`missing template: ${TEMPLATE}`);

// local date, not UTC — a note written at 1am should not be stamped yesterday
const now = new Date();
const pad = (n) => String(n).padStart(2, '0');
const today = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;

mkdirSync(NOTES_DIR, { recursive: true });
const target = resolve(NOTES_DIR, `${slug}.md`);

if (existsSync(target)) {
  console.error(`error: ${target.replace(ROOT + '\\', '').replace(ROOT + '/', '')} already exists`);
  console.error('       the file name is the URL — pick another slug, or edit the existing note');
  process.exit(1);
}

let body = readFileSync(TEMPLATE, 'utf8').replace(/^date: __DATE__$/m, `date: ${today}`);
if (title) body = body.replace(/^title: .*$/m, `title: ${title}`);
writeFileSync(target, body, 'utf8');

const rel = `src/content/notes/${slug}.md`;
console.log(`created  ${rel}`);
console.log(`url      /notes/${slug}.html       (after the next deploy)`);
console.log('');
console.log('next:');
console.log(`  1. edit ${rel} — the template explains every part`);
console.log('  2. npm run dev     to look at it locally  (or: npm run build)');
console.log('  3. git add -A && git commit -m "..." && git push');
