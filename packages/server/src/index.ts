import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import bcrypt from 'bcryptjs';
import { config } from './config.js';
import { getDb } from './db/connection.js';
import { initSchema } from './db/schema.js';
import authRouter from './routes/auth.js';
import genealogyRouter from './routes/genealogy.js';
import generationRouter from './routes/generation.js';
import memberRouter from './routes/member.js';
import queryRouter from './routes/query.js';
import cultureRouter from './routes/culture.js';
import wikiRouter from './routes/wiki.js';
import newsRouter from './routes/news.js';
import uploadRouter from './routes/upload.js';
import statsRouter from './routes/stats.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const app = express();

app.use(cors());
app.use(helmet({ contentSecurityPolicy: false }));
app.use(compression());
app.use(express.json());

app.use('/uploads', express.static(config.UPLOAD_DIR));

app.get('/api/health', (_req, res) => res.json({ ok: true }));
app.use('/api/auth', authRouter);
app.use('/api/genealogies', genealogyRouter);
app.use('/api/generations', generationRouter);
app.use('/api/members', memberRouter);
app.use('/api/query', queryRouter);
app.use('/api/culture', cultureRouter);
app.use('/api/wiki', wikiRouter);
app.use('/api/news', newsRouter);
app.use('/api/upload', uploadRouter);
app.use('/api/stats', statsRouter);

if (fs.existsSync(config.ADMIN_DIST)) {
  app.use('/admin', express.static(config.ADMIN_DIST));
  app.get('/admin/*', (_req, res) => {
    res.sendFile(path.join(config.ADMIN_DIST, 'index.html'));
  });
}

const dataDir = path.dirname(config.DB_PATH);
fs.mkdirSync(dataDir, { recursive: true });
fs.mkdirSync(config.UPLOAD_DIR, { recursive: true });

const db = getDb();
initSchema(db);

const adminCount = db.prepare('SELECT COUNT(*) as n FROM admin_user').get() as { n: number };
if (adminCount.n === 0) {
  const passwordHash = bcrypt.hashSync(config.ADMIN_PASSWORD, 10);
  db.prepare(
    'INSERT INTO admin_user (username, password_hash, must_change_password) VALUES (?, ?, 1)'
  ).run(config.ADMIN_USERNAME, passwordHash);
  console.log('Default admin user created:', config.ADMIN_USERNAME);
}

app.listen(config.PORT, () => {
  console.log(`Server running at http://localhost:${config.PORT}`);
});
