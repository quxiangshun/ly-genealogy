import { Router, Request, Response } from 'express';
import { getDb } from '../db/connection.js';
import { authRequired } from '../middleware/auth.js';
import { rebuildPaths } from '../services/path-rebuild.js';

const now = () => new Date().toISOString().replace('T', ' ').slice(0, 19);
const router: Router = Router();

router.get('/', authRequired, (req: Request, res: Response) => {
  try {
    const genealogyId = req.query.genealogy_id;
    if (!genealogyId) {
      res.status(200).json([]);
      return;
    }

    const gid = parseInt(String(genealogyId), 10);
    if (isNaN(gid)) {
      res.status(400).json({ error: 'Invalid genealogy_id' });
      return;
    }

    const db = getDb();
    const genealogy = db.prepare('SELECT id FROM genealogy_main WHERE id = ?').get(gid);
    if (!genealogy) {
      res.status(404).json({ error: 'Genealogy not found' });
      return;
    }

    const rows = db.prepare(`
      SELECT * FROM family_member
      WHERE genealogy_id = ?
      ORDER BY generation_number ASC, id ASC
    `).all(gid) as Record<string, unknown>[];

    res.status(200).json(rows);
  } catch (err) {
    console.error('List members error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/:id', authRequired, (req: Request, res: Response) => {
  try {
    const id = parseInt(String(req.params.id ?? ''), 10);
    if (isNaN(id)) {
      res.status(400).json({ error: 'Invalid ID' });
      return;
    }

    const db = getDb();
    const member = db.prepare('SELECT * FROM family_member WHERE id = ?').get(id) as Record<string, unknown> | undefined;
    if (!member) {
      res.status(404).json({ error: 'Member not found' });
      return;
    }

    const fatherId = member.father_id as number | null;
    const motherId = member.mother_id as number | null;
    const genealogyId = member.genealogy_id as number;

    let fatherName: string | null = null;
    let motherName: string | null = null;
    if (fatherId) {
      const f = db.prepare('SELECT name FROM family_member WHERE id = ?').get(fatherId) as { name: string } | undefined;
      fatherName = f?.name ?? null;
    }
    if (motherId) {
      const m = db.prepare('SELECT name FROM family_member WHERE id = ?').get(motherId) as { name: string } | undefined;
      motherName = m?.name ?? null;
    }

    const children = db.prepare(`
      SELECT * FROM family_member
      WHERE genealogy_id = ? AND (father_id = ? OR mother_id = ?)
      ORDER BY generation_number ASC, id ASC
    `).all(genealogyId, id, id) as Record<string, unknown>[];

    const parentIds = [fatherId, motherId].filter(Boolean) as number[];
    let siblings: Record<string, unknown>[] = [];
    if (parentIds.length > 0) {
      const placeholders = parentIds.map(() => '?').join(', ');
      siblings = db.prepare(`
        SELECT * FROM family_member
        WHERE genealogy_id = ? AND id != ? AND (father_id IN (${placeholders}) OR mother_id IN (${placeholders}))
        ORDER BY generation_number ASC, id ASC
      `).all(genealogyId, id, ...parentIds, ...parentIds) as Record<string, unknown>[];
    }

    res.status(200).json({
      ...member,
      father_name: fatherName,
      mother_name: motherName,
      children,
      siblings,
    });
  } catch (err) {
    console.error('Get member error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.post('/', authRequired, (req: Request, res: Response) => {
  try {
    const body = req.body ?? {};
    const {
      genealogy_id,
      name,
      former_name,
      gender,
      generation_number,
      courtesy_name,
      birth_date,
      death_date,
      birth_place,
      father_id,
      mother_id,
      spouse_name,
      photo,
      notes,
    } = body;

    if (!genealogy_id || !name) {
      res.status(400).json({ error: 'genealogy_id and name are required' });
      return;
    }

    const gid = parseInt(String(genealogy_id), 10);
    if (isNaN(gid)) {
      res.status(400).json({ error: 'Invalid genealogy_id' });
      return;
    }

    const db = getDb();
    const genealogy = db.prepare('SELECT id FROM genealogy_main WHERE id = ?').get(gid);
    if (!genealogy) {
      res.status(404).json({ error: 'Genealogy not found' });
      return;
    }

    const stmt = db.prepare(`
      INSERT INTO family_member (
        genealogy_id, name, former_name, gender, generation_number, courtesy_name,
        birth_date, death_date, birth_place, father_id, mother_id,
        spouse_name, photo, notes
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const result = stmt.run(
      gid,
      name,
      former_name ?? null,
      gender ?? 'M',
      generation_number ?? null,
      courtesy_name ?? null,
      birth_date ?? null,
      death_date ?? null,
      birth_place ?? null,
      father_id ?? null,
      mother_id ?? null,
      spouse_name ?? null,
      photo ?? null,
      notes ?? null
    );

    rebuildPaths(gid);

    const inserted = db.prepare('SELECT * FROM family_member WHERE id = ?').get(result.lastInsertRowid) as Record<string, unknown>;
    res.status(201).json(inserted);
  } catch (err) {
    console.error('Create member error:', err);
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
      name,
      former_name,
      gender,
      generation_number,
      courtesy_name,
      birth_date,
      death_date,
      birth_place,
      father_id,
      mother_id,
      spouse_name,
      photo,
      notes,
    } = body;

    const db = getDb();
    const existing = db.prepare('SELECT id, genealogy_id FROM family_member WHERE id = ?').get(id) as { id: number; genealogy_id: number } | undefined;
    if (!existing) {
      res.status(404).json({ error: 'Member not found' });
      return;
    }

    db.prepare(`
      UPDATE family_member SET
        name = COALESCE(?, name),
        former_name = ?,
        gender = COALESCE(?, gender),
        generation_number = ?,
        courtesy_name = ?,
        birth_date = ?,
        death_date = ?,
        birth_place = ?,
        father_id = ?,
        mother_id = ?,
        spouse_name = ?,
        photo = ?,
        notes = ?
      WHERE id = ?
    `).run(
      name ?? undefined,
      former_name ?? null,
      gender ?? undefined,
      generation_number ?? null,
      courtesy_name ?? null,
      birth_date ?? null,
      death_date ?? null,
      birth_place ?? null,
      father_id ?? null,
      mother_id ?? null,
      spouse_name ?? null,
      photo ?? null,
      notes ?? null,
      id
    );

    rebuildPaths(existing.genealogy_id);

    const updated = db.prepare('SELECT * FROM family_member WHERE id = ?').get(id) as Record<string, unknown>;
    res.status(200).json(updated);
  } catch (err) {
    console.error('Update member error:', err);
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
    const existing = db.prepare('SELECT id, genealogy_id FROM family_member WHERE id = ?').get(id) as { id: number; genealogy_id: number } | undefined;
    if (!existing) {
      res.status(404).json({ error: 'Member not found' });
      return;
    }

    db.prepare('UPDATE family_member SET father_id = NULL WHERE father_id = ?').run(id);
    db.prepare('UPDATE family_member SET mother_id = NULL WHERE mother_id = ?').run(id);
    db.prepare('DELETE FROM family_member WHERE id = ?').run(id);

    rebuildPaths(existing.genealogy_id);

    res.status(200).json({ message: 'Member deleted' });
  } catch (err) {
    console.error('Delete member error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
