import { getDb } from '../db/connection.js';

/**
 * Rebuild materialized paths for all family members in a genealogy.
 * Path format: /root_id/.../self_id/
 */
export function rebuildPaths(genealogyId: number): void {
  const db = getDb();
  const members = db
    .prepare(
      'SELECT id, father_id FROM family_member WHERE genealogy_id = ?'
    )
    .all(genealogyId) as Array<{ id: number; father_id: number | null }>;

  const memberMap = new Map<number, { id: number; father_id: number | null }>();
  for (const m of members) {
    memberMap.set(m.id, m);
  }

  const computed = new Map<number, string>();

  function compute(mid: number): string {
    const cached = computed.get(mid);
    if (cached !== undefined) return cached;

    const m = memberMap.get(mid);
    if (!m) return '';

    let result: string;
    if (m.father_id && memberMap.has(m.father_id)) {
      const parentPath = compute(m.father_id);
      result = `${parentPath}${mid}/`;
    } else {
      result = `/${mid}/`;
    }
    computed.set(mid, result);
    return result;
  }

  const updateStmt = db.prepare(
    'UPDATE family_member SET path = ? WHERE id = ?'
  );
  const updateMany = db.transaction(() => {
    for (const m of members) {
      const path = compute(m.id);
      updateStmt.run(path, m.id);
    }
  });

  updateMany();
}
