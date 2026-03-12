/**
 * Slugify: keep Chinese chars and alphanumeric, replace other chars with hyphens.
 * Lowercase, trim hyphens. If empty, return timestamp.
 */
export function slugify(text: string): string {
  const s = (text ?? '')
    .trim()
    .replace(/[^\w\u4e00-\u9fff]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .toLowerCase();
  return s || String(Math.floor(Date.now() / 1000));
}
