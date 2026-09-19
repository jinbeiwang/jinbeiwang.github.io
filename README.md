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

Create `src/content/notes/<kebab-case-slug>.md`:

```yaml
---
title: Title of the note
summary: One line, shown under the title on the dashboard.
date: 2026-09-19
category: Site notes
tags: [Astro, GitHub Pages]
lang: zh
---
```

Then `npm run build` and push. Only `title` and `date` are required.

**The file name is the URL** — `/notes/<slug>.html`. Renaming a file breaks a
published link; change `title` instead.

Valid categories are listed in `src/data/categories.json`. Using a value that
is not there does not break anything; it just adds a new section to the
dashboard.

## Local development

```bash
npm install
npm run dev      # http://localhost:4321, reloads on save
npm run build    # writes dist/
npm run preview  # serve the built output
```

Run `npm run build` before pushing. The dev server is lenient; the build
validates frontmatter and will fail on a missing `title` or an unparseable `date`.

## Layout

```
src/
  content/notes/      the notes, one Markdown file per note
  data/
    site.json         site title, author, description
    categories.json   section order and hints
    projects.json     the nine external projects
  layouts/Note.astro  the note page shell
  components/Entry.astro  one dashboard row
  pages/
    index.astro       the dashboard
    notes/[...slug].astro   note pages
    tags/[tag].astro  tag pages
  styles/base.css     every style on the site — the only place to change colours
astro.config.mjs
public/               served as-is (favicon, .nojekyll)
```

## Deployment

`.github/workflows/deploy.yml` builds the site and publishes `dist/` on every
push to `main`.

**GitHub Pages must be set to build with Actions, not from a branch.** The
repository started on the legacy build (GitHub running Jekyll server-side),
which cannot run an Astro build. Switch it once:

```bash
gh api -X PUT repos/jinbeiwang/jinbeiwang.github.io/pages \
  -f build_type=workflow
```

Or in the web UI: Settings → Pages → Source → **GitHub Actions**.

Once that is set, the repository-root `index.html` and `.nojekyll` are no longer
used — only the uploaded `dist/` is served. They can be deleted, though leaving
them costs nothing and acts as a fallback if the build type is ever reverted.

### If the workflow file cannot be pushed

Creating or updating anything under `.github/workflows/` requires the token to
carry the **Workflows** permission. A fine-grained PAT without it is rejected
with `refusing to allow a Personal Access Token to create or update workflow`.
Either grant that permission on the token, or add the file through the GitHub
web UI (Add file → Create new file → `.github/workflows/deploy.yml`).

## Notes on the migration

This repository replaces the earlier approach of aggregating the nine sibling
repos with a standalone Node script (`build-index.mjs`). That script still works
and its registry still holds the titles and summaries now copied into
`projects.json`, but it is no longer part of this site's build.

The per-note hand-written HTML style was not discarded: its tokens, type scale
and rules were carried into `src/styles/base.css` verbatim. What changed is that
the stylesheet is now shared — a note file contains no CSS at all.
