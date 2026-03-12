import { Router, Request, Response } from 'express';
import { getDb } from '../db/connection.js';

const router: Router = Router();

router.get('/', (_req: Request, res: Response) => {
  try {
    const db = getDb();

    const count = (sql: string) => Number((db.prepare(sql).get() as { cnt: number }).cnt);

    const genealogyCount = count('SELECT COUNT(*) AS cnt FROM genealogy_main');
    const memberCount = count('SELECT COUNT(*) AS cnt FROM family_member');
    const generationCount = count('SELECT COUNT(*) AS cnt FROM genealogy_generation');
    const wikiCount = count('SELECT COUNT(*) AS cnt FROM wiki_entry');
    const newsCount = count('SELECT COUNT(*) AS cnt FROM news_article');

    const regions = (db.prepare(`
      SELECT DISTINCT region FROM genealogy_main
      WHERE region IS NOT NULL AND region != ''
      ORDER BY region
    `).all() as { region: string }[]).map((r) => r.region);

    const surnames = (db.prepare(`
      SELECT DISTINCT surname FROM genealogy_main
      WHERE surname IS NOT NULL AND surname != ''
      ORDER BY surname
    `).all() as { surname: string }[]).map((s) => s.surname);

    const recentGenealogies = (db.prepare(`
      SELECT g.id, g.surname, g.genealogy_name, g.hall_name, g.region,
             g.period, g.description, g.scattered_region, g.create_time,
        (SELECT COUNT(*) FROM family_member m WHERE m.genealogy_id = g.id) AS member_count
      FROM genealogy_main g
      ORDER BY g.create_time DESC
      LIMIT 8
    `).all() as Record<string, unknown>[]).map((r) => ({
      id: r.id,
      surname: r.surname,
      name: r.genealogy_name,
      genealogy_name: r.genealogy_name,
      hall_name: r.hall_name,
      region: r.region,
      period: r.period,
      description: r.description,
      scattered_region: r.scattered_region,
      memberCount: Number(r.member_count ?? 0),
      createdAt: r.create_time,
    }));

    const recentNews = (db.prepare(`
      SELECT id, title, slug, category, is_pinned, event_date, create_time FROM news_article
      ORDER BY create_time DESC
      LIMIT 5
    `).all() as Record<string, unknown>[]).map((r) => ({
      id: r.id,
      title: r.title,
      slug: r.slug,
      category: r.category,
      is_pinned: r.is_pinned,
      event_date: r.event_date,
      create_time: r.create_time,
      createdAt: r.create_time,
    }));

    res.status(200).json({
      genealogyCount,
      memberCount,
      generationCount,
      wikiCount,
      newsCount,
      regions,
      surnames,
      recentGenealogies,
      recentNews,
    });
  } catch (err) {
    console.error('Stats error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
