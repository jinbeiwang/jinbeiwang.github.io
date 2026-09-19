# jinbeiwang.github.io

The hub repository: a notes dashboard built with Astro, deployed to GitHub Pages by
GitHub Actions.

Two kinds of content live here:

- **Notes** — Markdown files in `src/content/notes/`. Adding one updates the
  dashboard, the category sections and the tag pages. No index file is ever
  edited by hand.
- **External projects** — the nine sibling repositories, each still its own Pages
  site under `jinbeiwang.github.io/<repo>/`. They are listed from
  `src/data/projects.json`; nothing about those repos changes.

## Adding a note

Three steps. The first one is a command.

```bash
npm run new hash-basics          # 1. make the file
npm run dev                      # 2. look at it while you write   (or: npm run build)
git add -A && git commit -m "..." && git push     # 3. publish
```

`npm run new <slug>` copies `templates/new-note.md` to
`src/content/notes/<slug>.md` and stamps today's date into the frontmatter. The
template is a working note — it demonstrates every piece of the house style and
says what each part is for. Replace the content, delete the comments, done.

Then, nothing else. **The dashboard entry, the category section, the tag pages,
the "read next" ordering and the contents drawer on the page itself are all
generated at build time.** There is no index to update and no CSS to write.

The slug is the URL: `hash-basics.md` is served at `/notes/hash-basics.html`.
**Pick it once and leave it alone** — renaming the file breaks every published
link to it. To change the heading, change `title`.

Useful flags:

```bash
npm run new hash-basics -- --title "The SAS hash object, from the start"
node scripts/new-note.mjs --help     # same script, without npm
```

`npm run new` refuses a slug that is not kebab-case, and refuses to overwrite an
existing note.

### What goes in the file

Frontmatter first — only `title` and `date` are required:

```yaml
---
title: The SAS hash object, from the start
summary: One line, shown under the title on the dashboard.
date: 2026-09-19
category: SAS patterns
tags: [SAS, Hash]
lang: zh
---
```

Valid categories are listed in `src/data/categories.json`. An unregistered value
does not break anything; it just adds a new section to the dashboard.

Then the body. Write plain Markdown if you like — but the notes have a small
vocabulary that carries this site's look: evidence tags (`[doc]` / `[lit]` /
`[实践]`), a conclusion box, tables bracketed in emerald, verdict pills. It is
all in `templates/new-note.md`, with comments, and it is documented in the note
**"这个站怎么组织"** at `/notes/site-workflow.html`.
Nothing about it lives in the note file itself: colours, spacing and the contents
drawer are decided by `src/styles/note.css`.

## Local development

```bash
npm ci           # exact versions from package-lock.json
npm install      # after editing package.json
npm run dev      # http://localhost:4321, reloads on save
npm run build    # writes dist/
npm run preview  # serve the built output
```

Run `npm run build` before pushing. The dev server is lenient; the build
validates frontmatter and will fail on a missing `title` or an unparseable `date`.

The lockfile resolves every package from `registry.npmjs.org`, not from a
mirror, so the versions installed here are the ones the build job gets.

## Layout

```
templates/new-note.md       the starting point `npm run new` copies
scripts/new-note.mjs        the scaffolding command
src/
  content/notes/            the notes, one Markdown file per note
  content.config.ts         the note collection's frontmatter schema
  data/
    site.json               site title, author, description
    categories.json         section order and hints
    projects.json           the nine external projects
  layouts/Note.astro        the note page shell (imports both stylesheets)
  components/Entry.astro    one dashboard row
  lib/notes.ts              slug helpers, shared by pages and components
  pages/
    index.astro             the dashboard
    notes/[...slug].astro   note pages
    tags/[tag].astro        tag pages
  styles/
    base.css                site skeleton, dashboard, tag pages
    note.css                the long-form reading layout — note pages only
astro.config.mjs
public/                     served as-is (favicon, .nojekyll)
```

`note.css` is imported by the note layout alone, so a change to the reading
layout cannot reach the dashboard. That separation is the point: the dashboard and
a long note are two different typographic jobs and used to fight over one sheet.

## Deployment

`.github/workflows/deploy.yml` builds the site and publishes `dist/` on every
push to `main`. A full run — checkout, install, build, deploy — takes about
thirty seconds. `dist/` is never committed.

**GitHub Pages is set to build with Actions** (`build_type: workflow`). This is
required: the other option, the legacy build, runs Jekyll on GitHub's side and
cannot execute an Astro build. It is already set; this is how it was done:

```bash
gh api -X PUT repos/jinbeiwang/jinbeiwang.github.io/pages -f build_type=workflow
```

Or in the web UI: Settings → Pages → Source → **GitHub Actions**.

Why it is worth keeping on `workflow`: while the setting is `legacy`, GitHub
runs its own `pages build and deployment` on every push, **in parallel with this
workflow**. Both publish a deployment and whichever finishes last wins, so the
site can silently flip back to the repository-root `index.html`.

### Pushing changes to `.github/workflows/`

The "Workflows permission" restriction applies to HTTPS pushes authenticated
with a personal access token. **Pushing over SSH is not subject to it** — the
deploy workflow was added with a plain `git push` over an SSH remote, with no
special token permission. If a push is ever rejected with `refusing to allow a
Personal Access Token to create or update workflow`, point the remote at SSH:

```bash
git remote set-url origin git@github.com:jinbeiwang/jinbeiwang.github.io.git
```

## Notes on the migration

This repository replaces two earlier approaches, both still present in the
working tree but out of the build:

- aggregating the nine sibling repos with a standalone Node script
  (`repo/site-dashboard/tools/build-index.mjs`, in the parent working directory).
  That script still works and its registry holds the titles and summaries now
  copied into `projects.json`;
- hand-written per-note HTML, each file carrying its own copy of the stylesheet.
  Those notes' tokens and type scale were carried into `src/styles/note.css`
  verbatim, and their contents drawer became a layout feature, so every note has
  one without shipping a script of its own.
