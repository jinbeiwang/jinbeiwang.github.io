import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://jinbeiwang.github.io',

  // keep the .html URL shape the existing notes already use
  // (/notes/some-slug.html rather than /notes/some-slug/)
  build: { format: 'file' },
  trailingSlash: 'ignore',

  devToolbar: { enabled: false },

  // Astro ships Shiki's github-dark by default, which paints code blocks dark
  // inline (and inline styles win over base.css). The house style is light, so
  // pick the light counterpart.
  markdown: {
    shikiConfig: { theme: 'github-light' },
  },
});
