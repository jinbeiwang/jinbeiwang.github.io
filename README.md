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

Because of that, the root `index.html` and `.nojekyll` are now dead weight: the
served site comes entirely from `dist/`. The `index.html` is the previous
landing page and no longer reflects what is published, which makes it a trap for
the next person reading the repository. It is recoverable from history
(`git show bff280d:index.html`) if the build type is ever reverted to legacy.

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

This repository replaces the earlier approach of aggregating the nine sibling
repos with a standalone Node script (`build-index.mjs`). That script still works
and its registry still holds the titles and summaries now copied into
`projects.json`, but it is no longer part of this site's build.

The per-note hand-written HTML style was not discarded: its tokens, type scale
and rules were carried into `src/styles/base.css` verbatim. What changed is that
the stylesheet is now shared — a note file contains no CSS at all.
