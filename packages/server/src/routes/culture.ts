import { Router, Request, Response } from 'express';
import { getDb } from '../db/connection.js';
import { findRelationship } from '../services/relationship.js';

const router: Router = Router();

router.get('/zibei', (req: Request, res: Response) => {
  try {
    const q = (req.query.q as string)?.trim() ?? '';

    const db = getDb();
    const genealogies = db.prepare(`
      SELECT * FROM genealogy_main
      ORDER BY surname, region
    `).all() as Record<string, unknown>[];

    const results: Record<string, unknown>[] = [];

    for (const g of genealogies) {
      const gens = db.prepare(`
        SELECT * FROM genealogy_generation
        WHERE genealogy_id = ?
        ORDER BY sort_order ASC
      `).all(g.id) as { character: string; sort_order: number }[];

      if (gens.length === 0) continue;

      const charsStr = gens.map((gen) => gen.character).join('');
      const entry: Record<string, unknown> = {
        genealogy: g,
        generations: gens,
        chars_str: charsStr,
      };

      if (q && charsStr.includes(q)) {
        const matchedPositions: number[] = [];
        for (const gen of gens) {
          if (gen.character.includes(q)) {
            matchedPositions.push(gen.sort_order + 1);
          }
        }
        entry.matched_positions = matchedPositions;
        results.push(entry);
      } else if (!q) {
        results.push(entry);
      }
    }

    res.status(200).json(results);
  } catch (err) {
    console.error('Zibei search error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.post('/relationship', (req: Request, res: Response) => {
  try {
    const { genealogy_id, name_a, name_b, id_a, id_b } = req.body ?? {};

    if (!genealogy_id || !name_a || !name_b) {
      res.status(400).json({ error: 'genealogy_id, name_a, and name_b are required' });
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

    let memberA: Record<string, unknown> | null = null;
    let memberB: Record<string, unknown> | null = null;

    if (id_a) {
      memberA = db.prepare('SELECT * FROM family_member WHERE id = ? AND genealogy_id = ?').get(id_a, gid) as Record<string, unknown> | undefined ?? null;
    }
    if (!memberA) {
      memberA = db.prepare('SELECT * FROM family_member WHERE name = ? AND genealogy_id = ?').get(name_a, gid) as Record<string, unknown> | undefined ?? null;
    }

    if (id_b) {
      memberB = db.prepare('SELECT * FROM family_member WHERE id = ? AND genealogy_id = ?').get(id_b, gid) as Record<string, unknown> | undefined ?? null;
    }
    if (!memberB) {
      memberB = db.prepare('SELECT * FROM family_member WHERE name = ? AND genealogy_id = ?').get(name_b, gid) as Record<string, unknown> | undefined ?? null;
    }

    const membersA = db.prepare('SELECT * FROM family_member WHERE name = ? AND genealogy_id = ?').all(name_a, gid) as Record<string, unknown>[];
    const membersB = db.prepare('SELECT * FROM family_member WHERE name = ? AND genealogy_id = ?').all(name_b, gid) as Record<string, unknown>[];

    if (membersA.length === 0) {
      res.status(200).json({ error: `Member "${name_a}" not found` });
      return;
    }
    if (membersB.length === 0) {
      res.status(200).json({ error: `Member "${name_b}" not found` });
      return;
    }

    const needDisambiguateA = membersA.length > 1 && !id_a;
    const needDisambiguateB = membersB.length > 1 && !id_b;

    if (needDisambiguateA || needDisambiguateB) {
      res.status(200).json({
        disambiguate: true,
        members_a: needDisambiguateA ? membersA : null,
        members_b: needDisambiguateB ? membersB : null,
        selected_a: memberA,
        selected_b: memberB,
      });
      return;
    }

    const ma = memberA ?? membersA[0];
    const mb = memberB ?? membersB[0];
    const idA = ma.id as number;
    const idB = mb.id as number;

    const result = findRelationship(idA, idB);
    if (result) {
      res.status(200).json({
        relation: result.relation,
        lca: result.lca,
        up_a: result.upA,
        up_b: result.upB,
        chain_a: result.chainA,
        chain_b: result.chainB,
        member_a: ma,
        member_b: mb,
      });
    } else {
      res.status(200).json({
        error: `No relationship found between "${ma.name}" and "${mb.name}" in this genealogy`,
        member_a: ma,
        member_b: mb,
      });
    }
  } catch (err) {
    console.error('Relationship error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
