import { Router, Request, Response } from 'express';
import { getDb } from '../db/connection.js';
import { authRequired } from '../middleware/auth.js';

const now = () => new Date().toISOString().replace('T', ' ').slice(0, 19);
const router: Router = Router();

router.get('/', (req: Request, res: Response) => {
  try {
    const { surname, region, period } = req.query;
    const db = getDb();

    let sql = `
      SELECT g.*,
        (SELECT COUNT(*) FROM family_member m WHERE m.genealogy_id = g.id) AS member_count
      FROM genealogy_main g
      WHERE 1=1
    `;
    const params: (string | number)[] = [];

    if (surname && typeof surname === 'string') {
      sql += ' AND g.surname LIKE ?';
      params.push(`%${surname}%`);
    }
    if (region && typeof region === 'string') {
      sql += ' AND g.region LIKE ?';
      params.push(`%${region}%`);
    }
    if (period && typeof period === 'string') {
      sql += ' AND g.period LIKE ?';
      params.push(`%${period}%`);
    }

    sql += ' ORDER BY g.surname, g.genealogy_name';

    const rows = db.prepare(sql).all(...params) as Record<string, unknown>[];
    const items = rows.map((r) => ({
      ...r,
      member_count: Number(r.member_count ?? 0),
    }));

    res.status(200).json(items);
  } catch (err) {
    console.error('List genealogies error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/:id', (req: Request, res: Response) => {
  try {
    const id = parseInt(String(req.params.id ?? ''), 10);
    if (isNaN(id)) {
      res.status(400).json({ error: 'Invalid ID' });
      return;
    }

    const db = getDb();
    const row = db.prepare(`
      SELECT g.*,
        (SELECT COUNT(*) FROM family_member m WHERE m.genealogy_id = g.id) AS member_count,
        (SELECT COUNT(*) FROM genealogy_generation gg WHERE gg.genealogy_id = g.id) AS generation_count
      FROM genealogy_main g
      WHERE g.id = ?
    `).get(id) as Record<string, unknown> | undefined;

    if (!row) {
      res.status(404).json({ error: 'Genealogy not found' });
      return;
    }

    res.status(200).json({
      ...row,
      member_count: Number(row.member_count ?? 0),
      generation_count: Number(row.generation_count ?? 0),
    });
  } catch (err) {
    console.error('Get genealogy error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.post('/', authRequired, (req: Request, res: Response) => {
  try {
    const body = req.body ?? {};
    const {
      surname,
      genealogy_name,
      region,
      period,
      volumes,
      hall_name,
      source_url,
      founder_info,
      collection_info,
      scattered_region,
      description,
    } = body;

    if (!surname || !genealogy_name) {
      res.status(400).json({ error: 'surname and genealogy_name are required' });
      return;
    }

    const db = getDb();
    const stmt = db.prepare(`
      INSERT INTO genealogy_main (
        surname, genealogy_name, region, period, volumes, hall_name,
        source_url, founder_info, collection_info, scattered_region,
        description, create_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const result = stmt.run(
      surname,
      genealogy_name ?? null,
      region ?? null,
      period ?? null,
      volumes ?? null,
      hall_name ?? null,
      source_url ?? null,
      founder_info ?? null,
      collection_info ?? null,
      scattered_region ?? null,
      description ?? null,
      now()
    );

    const inserted = db.prepare('SELECT * FROM genealogy_main WHERE id = ?').get(result.lastInsertRowid) as Record<string, unknown>;
    res.status(201).json(inserted);
  } catch (err) {
    console.error('Create genealogy error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.put('/:id', authRequired, (req: Request, res: Response) => {
  try {
    const id = parseInt(String(req.params.id ?? ''), 10);
    if (isNaN(id)) {
      res.status(400).json({ error: 'Invalid ID' });
      return;
    }

    const body = req.body ?? {};
    const {
      surname,
      genealogy_name,
      region,
      period,
      volumes,
      hall_name,
      source_url,
      founder_info,
      collection_info,
      scattered_region,
      description,
    } = body;

    const db = getDb();
    const existing = db.prepare('SELECT id FROM genealogy_main WHERE id = ?').get(id);
    if (!existing) {
      res.status(404).json({ error: 'Genealogy not found' });
      return;
    }

    db.prepare(`
      UPDATE genealogy_main SET
        surname = COALESCE(?, surname),
        genealogy_name = COALESCE(?, genealogy_name),
        region = ?,
        period = ?,
        volumes = ?,
        hall_name = ?,
        source_url = ?,
        founder_info = ?,
        collection_info = ?,
        scattered_region = ?,
        description = ?
      WHERE id = ?
    `).run(
      surname ?? undefined,
      genealogy_name ?? undefined,
      region ?? null,
      period ?? null,
      volumes ?? null,
      hall_name ?? null,
      source_url ?? null,
      founder_info ?? null,
      collection_info ?? null,
      scattered_region ?? null,
      description ?? null,
      id
    );

    const updated = db.prepare('SELECT * FROM genealogy_main WHERE id = ?').get(id) as Record<string, unknown>;
    res.status(200).json(updated);
  } catch (err) {
    console.error('Update genealogy error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.delete('/:id', authRequired, (req: Request, res: Response) => {
  try {
    const id = parseInt(String(req.params.id ?? ''), 10);
    if (isNaN(id)) {
      res.status(400).json({ error: 'Invalid ID' });
      return;
    }

    const db = getDb();
    const existing = db.prepare('SELECT id FROM genealogy_main WHERE id = ?').get(id);
    if (!existing) {
      res.status(404).json({ error: 'Genealogy not found' });
      return;
    }

    db.prepare('DELETE FROM genealogy_main WHERE id = ?').run(id);
    res.status(200).json({ message: 'Genealogy deleted' });
  } catch (err) {
    console.error('Delete genealogy error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
