/** Shared helpers for the note collection. */

/** YYYY-MM-DD, the one date format used everywhere on the site. */
export const fmtDate = (d: Date | string): string =>
  new Date(d).toISOString().slice(0, 10);

/**
 * A tag's URL segment. Lowercased, spaces to hyphens, punctuation dropped.
 * CJK is kept as-is — it survives percent-encoding and stays readable in the
 * address bar, which a transliteration or a hash would not.
 */
export const tagSlug = (t: string): string =>
  t
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9\u4e00-\u9fff-]/g, '');

/** Notes are served as real .html files (build.format = 'file'). */
export const noteHref = (id: string): string => `/notes/${id}.html`;

/** The on-site path shown in an entry's meta row. */
export const notePath = (id: string): string => `/notes/${id}.html`;
