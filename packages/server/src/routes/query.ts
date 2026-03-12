import { Router, Request, Response } from 'express';
import { getDb } from '../db/connection.js';
import { authRequired } from '../middleware/auth.js';

const router: Router = Router();

router.get('/search', authRequired, (req: Request, res: Response) => {
  try {
    const { name, genealogy_id } = req.query;
    if (!name || typeof name !== 'string') {
      res.status(400).json({ error: 'name query param is required' });
      return;
    }

    const db = getDb();
    let sql = `
      SELECT m.*, g.genealogy_name
      FROM family_member m
      JOIN genealogy_main g ON g.id = m.genealogy_id
      WHERE m.name LIKE ?
    `;
    const params: (string | number)[] = [`%${name}%`];

    if (genealogy_id) {
      const gid = parseInt(String(genealogy_id), 10);
      if (!isNaN(gid)) {
        sql += ' AND m.genealogy_id = ?';
        params.push(gid);
      }
    }

    sql += ' ORDER BY m.generation_number ASC, m.id ASC LIMIT 100';

    const rows = db.prepare(sql).all(...params) as Record<string, unknown>[];
    res.status(200).json(rows);
  } catch (err) {
    console.error('Search members error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/tree/:genealogyId', authRequired, (req: Request, res: Response) => {
  try {
    const genealogyId = parseInt(String(req.params.genealogyId ?? ''), 10);
    if (isNaN(genealogyId)) {
      res.status(400).json({ error: 'Invalid genealogy ID' });
      return;
    }

    const db = getDb();
    const genealogy = db.prepare('SELECT id FROM genealogy_main WHERE id = ?').get(genealogyId);
    if (!genealogy) {
      res.status(404).json({ error: 'Genealogy not found' });
      return;
    }

    const rows = db.prepare(`
      SELECT * FROM family_member
      WHERE genealogy_id = ?
      ORDER BY generation_number ASC, id ASC
    `).all(genealogyId) as Record<string, unknown>[];

    res.status(200).json(rows);
  } catch (err) {
    console.error('Get tree error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/autocomplete', (req: Request, res: Response) => {
  try {
    const { genealogy_id, q } = req.query;
    if (!genealogy_id || !q || typeof q !== 'string') {
      res.status(400).json({ error: 'genealogy_id and q query params are required' });
      return;
    }

    const gid = parseInt(String(genealogy_id), 10);
    if (isNaN(gid)) {
      res.status(400).json({ error: 'Invalid genealogy_id' });
      return;
    }

    const db = getDb();
    const members = db.prepare(`
      SELECT m.id, m.name, m.generation_number, m.father_id
      FROM family_member m
      WHERE m.genealogy_id = ? AND m.name LIKE ?
      ORDER BY m.generation_number ASC, m.id ASC
      LIMIT 20
    `).all(gid, `%${q}%`) as { id: number; name: string; generation_number: number | null; father_id: number | null }[];

    const seen: Record<string, { id: number; name: string; generation: number | null; father: string; display?: string }[]> = {};
    for (const m of members) {
      const key = m.name;
      const fatherName = m.father_id
        ? (db.prepare('SELECT name FROM family_member WHERE id = ?').get(m.father_id) as { name: string } | undefined)?.name ?? ''
        : '';
      const item = {
        id: m.id,
        name: m.name,
        generation: m.generation_number,
        father: fatherName,
      };
      if (key in seen) {
        (item as Record<string, unknown>).display = `${m.name}（第${m.generation_number ?? '?'}世${fatherName ? `，父：${fatherName}` : ''}）`;
        seen[key].push(item);
      } else {
        seen[key] = [item];
      }
    }

    const results: { id: number; name: string; generation: number | null; father: string; display?: string }[] = [];
    for (const items of Object.values(seen)) {
      for (const item of items) {
        if (items.length > 1 && !item.display) {
          item.display = `${item.name}（第${item.generation ?? '?'}世${item.father ? `，父：${item.father}` : ''}）`;
        }
        results.push(item);
      }
    }

    res.status(200).json(results);
  } catch (err) {
    console.error('Autocomplete error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
