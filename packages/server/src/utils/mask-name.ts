/**
 * Mask name for privacy display:
 * - 1 char -> *
 * - 2 chars -> first + *
 * - 3 chars -> first + * + last
 * - 4 chars -> first + ** + last
 * - 5+ chars -> first 2 + * padding + last 2
 */
export function maskName(name: string): string {
  const s = (name ?? '').trim();
  const len = s.length;
  if (len === 0) return '';
  if (len === 1) return '*';
  if (len === 2) return s[0] + '*';
  if (len === 3) return s[0] + '*' + s[2];
  if (len === 4) return s[0] + '**' + s[3];
  return s.slice(0, 2) + '*'.repeat(len - 4) + s.slice(-2);
}
