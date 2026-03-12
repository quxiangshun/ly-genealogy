import { Router, Request, Response } from 'express';
import { getDb } from '../db/connection.js';
import { authRequired } from '../middleware/auth.js';

const router: Router = Router();

router.get('/:genealogyId', (req: Request, res: Response) => {
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
      SELECT * FROM genealogy_generation
      WHERE genealogy_id = ?
      ORDER BY sort_order ASC
    `).all(genealogyId) as Record<string, unknown>[];

    res.status(200).json(rows);
  } catch (err) {
    console.error('Get generations error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.put('/:genealogyId', authRequired, (req: Request, res: Response) => {
  try {
    const genealogyId = parseInt(String(req.params.genealogyId ?? ''), 10);
    if (isNaN(genealogyId)) {
      res.status(400).json({ error: 'Invalid genealogy ID' });
      return;
    }

    const { generations } = req.body ?? {};
    if (!Array.isArray(generations)) {
      res.status(400).json({ error: 'generations array is required' });
      return;
    }

    const db = getDb();
    const genealogy = db.prepare('SELECT id FROM genealogy_main WHERE id = ?').get(genealogyId);
    if (!genealogy) {
      res.status(404).json({ error: 'Genealogy not found' });
      return;
    }

    db.prepare('DELETE FROM genealogy_generation WHERE genealogy_id = ?').run(genealogyId);

    const insertStmt = db.prepare(`
      INSERT INTO genealogy_generation (genealogy_id, sort_order, character, note)
      VALUES (?, ?, ?, ?)
    `);

    for (let i = 0; i < generations.length; i++) {
      const g = generations[i] ?? {};
      const character = g.character ?? '';
      const note = g.note ?? null;
      insertStmt.run(genealogyId, i, character, note);
    }

    const rows = db.prepare(`
      SELECT * FROM genealogy_generation
      WHERE genealogy_id = ?
      ORDER BY sort_order ASC
    `).all(genealogyId) as Record<string, unknown>[];

    res.status(200).json(rows);
  } catch (err) {
    console.error('Update generations error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
