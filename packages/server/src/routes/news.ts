import { Router, Request, Response } from 'express';
import { getDb } from '../db/connection.js';
import { authRequired, optionalAuth } from '../middleware/auth.js';
import { slugify } from '../utils/slugify.js';

const now = () => new Date().toISOString().replace('T', ' ').slice(0, 19);
const router: Router = Router();
const PER_PAGE = 12;

router.get('/', optionalAuth, (req: Request, res: Response) => {
  try {
    const cat = (req.query.cat as string) ?? '';
    const q = (req.query.q as string)?.trim() ?? '';
    const page = Math.max(1, parseInt(String(req.query.page ?? 1), 10));

    const db = getDb();

    const isAdmin = !!req.userId;
    let whereClause = isAdmin ? 'WHERE 1=1' : 'WHERE is_published = 1';
    const params: (string | number)[] = [];

    if (cat) {
      whereClause += ' AND category = ?';
      params.push(cat);
    }
    if (q) {
      whereClause += ' AND (title LIKE ? OR summary LIKE ?)';
      params.push(`%${q}%`, `%${q}%`);
    }

    const countRow = db.prepare(
      `SELECT COUNT(*) AS total FROM news_article ${whereClause}`
    ).get(...params) as { total: number };
    const total = Number(countRow.total);

    const items = db.prepare(`
      SELECT * FROM news_article ${whereClause}
      ORDER BY is_pinned DESC, create_time DESC
      LIMIT ? OFFSET ?
    `).all(...params, PER_PAGE, (page - 1) * PER_PAGE) as Record<string, unknown>[];

    const catCounts: Record<string, number> = {};
    const catWhere = isAdmin ? '' : 'WHERE is_published = 1';
    const catRows = db.prepare(`
      SELECT category, COUNT(*) AS cnt FROM news_article ${catWhere} GROUP BY category
    `).all() as { category: string; cnt: number }[];
    for (const r of catRows) {
      catCounts[r.category] = Number(r.cnt);
    }

    const hotWhere = isAdmin ? '' : 'WHERE is_published = 1';
    const hotArticles = db.prepare(`
      SELECT * FROM news_article ${hotWhere}
      ORDER BY view_count DESC LIMIT 5
    `).all() as Record<string, unknown>[];

    const totalViewsRow = db.prepare(
      `SELECT COALESCE(SUM(view_count), 0) AS total FROM news_article ${hotWhere}`
    ).get() as { total: number };
    const totalViews = Number(totalViewsRow.total);

    res.status(200).json({
      items,
      total,
      page,
      pages: Math.ceil(total / PER_PAGE) || 1,
      catCounts,
      hotArticles,
      totalViews,
    });
  } catch (err) {
    console.error('List news error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/id/:id', authRequired, (req: Request, res: Response) => {
  try {
    const id = parseInt(String(req.params.id ?? ''), 10);
    if (isNaN(id)) {
      res.status(400).json({ error: 'Invalid ID' });
      return;
    }
    const db = getDb();
    const article = db.prepare('SELECT * FROM news_article WHERE id = ?').get(id) as Record<string, unknown> | undefined;
    if (!article) {
      res.status(404).json({ error: 'Article not found' });
      return;
    }
    res.status(200).json(article);
  } catch (err) {
    console.error('Get news by id error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/:slug', (req: Request, res: Response) => {
  try {
    const slug = req.params.slug;
    const db = getDb();

    const article = db.prepare(
      'SELECT * FROM news_article WHERE slug = ? AND is_published = 1'
    ).get(slug) as Record<string, unknown> | undefined;

    if (!article) {
      res.status(404).json({ error: 'Article not found' });
      return;
    }

    db.prepare(`
      UPDATE news_article SET view_count = COALESCE(view_count, 0) + 1, update_time = ?
      WHERE id = ?
    `).run(now(), article.id);

    const updated = db.prepare('SELECT * FROM news_article WHERE id = ?').get(article.id) as Record<string, unknown>;
    const createTime = updated.create_time as string;

    const prev = db.prepare(`
      SELECT slug FROM news_article WHERE is_published = 1 AND create_time < ?
      ORDER BY create_time DESC LIMIT 1
    `).get(createTime) as { slug: string } | undefined;

    const next = db.prepare(`
      SELECT slug FROM news_article WHERE is_published = 1 AND create_time > ?
      ORDER BY create_time ASC LIMIT 1
    `).get(createTime) as { slug: string } | undefined;

    res.status(200).json({
      ...updated,
      prev_slug: prev?.slug ?? null,
      next_slug: next?.slug ?? null,
    });
  } catch (err) {
    console.error('Get news article error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.post('/', authRequired, (req: Request, res: Response) => {
  try {
    const body = req.body ?? {};
    const {
      title,
      slug: slugInput,
      category,
      summary,
      content,
      cover_image,
      source,
      event_date,
      is_published,
      is_pinned,
    } = body;

    if (!title) {
      res.status(400).json({ error: 'title is required' });
      return;
    }

    const db = getDb();
    let slug = (slugInput as string)?.trim() || slugify(title);
    const existing = db.prepare('SELECT id FROM news_article WHERE slug = ?').get(slug);
    if (existing) {
      slug = `${slug}-${Date.now()}`;
    }

    const result = db.prepare(`
      INSERT INTO news_article (
        title, slug, category, summary, content, cover_image, source, event_date,
        is_published, is_pinned, view_count, create_time, update_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
    `).run(
      title,
      slug,
      category ?? 'other',
      summary ?? null,
      content ?? '',
      cover_image ?? null,
      source ?? null,
      event_date ?? null,
      is_published ? 1 : 0,
      is_pinned ? 1 : 0,
      now(),
      now()
    );

    const inserted = db.prepare('SELECT * FROM news_article WHERE id = ?').get(result.lastInsertRowid) as Record<string, unknown>;
    res.status(201).json(inserted);
  } catch (err) {
    console.error('Create news article error:', err);
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
      title,
      slug: slugInput,
      category,
      summary,
      content,
      cover_image,
      source,
      event_date,
      is_published,
      is_pinned,
    } = body;

    const db = getDb();
    const existing = db.prepare('SELECT * FROM news_article WHERE id = ?').get(id) as Record<string, unknown> | undefined;
    if (!existing) {
      res.status(404).json({ error: 'Article not found' });
      return;
    }

    const newSlug = (slugInput as string)?.trim();
    if (newSlug && newSlug !== existing.slug) {
      const dup = db.prepare('SELECT id FROM news_article WHERE slug = ? AND id != ?').get(newSlug, id);
      if (!dup) {
        db.prepare('UPDATE news_article SET slug = ? WHERE id = ?').run(newSlug, id);
      }
    }

    db.prepare(`
      UPDATE news_article SET
        title = COALESCE(?, title),
        category = COALESCE(?, category),
        summary = ?,
        content = COALESCE(?, content),
        cover_image = ?,
        source = ?,
        event_date = ?,
        is_published = COALESCE(?, is_published),
        is_pinned = COALESCE(?, is_pinned),
        update_time = ?
      WHERE id = ?
    `).run(
      title ?? undefined,
      category ?? undefined,
      summary ?? null,
      content ?? undefined,
      cover_image ?? null,
      source ?? null,
      event_date ?? null,
      is_published !== undefined ? (is_published ? 1 : 0) : undefined,
      is_pinned !== undefined ? (is_pinned ? 1 : 0) : undefined,
      now(),
      id
    );

    const updated = db.prepare('SELECT * FROM news_article WHERE id = ?').get(id) as Record<string, unknown>;
    res.status(200).json(updated);
  } catch (err) {
    console.error('Update news article error:', err);
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
    const existing = db.prepare('SELECT id FROM news_article WHERE id = ?').get(id);
    if (!existing) {
      res.status(404).json({ error: 'Article not found' });
      return;
    }

    db.prepare('DELETE FROM news_article WHERE id = ?').run(id);
    res.status(200).json({ message: 'Article deleted' });
  } catch (err) {
    console.error('Delete news article error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
