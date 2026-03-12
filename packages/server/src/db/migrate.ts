/**
 * Migrate data from old SQLite database to the server database.
 * Run: pnpm migrate -- /path/to/old/genealogy.db
 */
import Database from 'better-sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';
import { getDb } from './connection.js';
import { initSchema } from './schema.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const defaultOldDbPath = path.resolve(__dirname, '../../../../genealogy.db');

const OLD_DB_PATH = process.argv[2] ?? defaultOldDbPath;

const TABLES = [
  'admin_user',
  'genealogy_main',
  'genealogy_generation',
  'family_member',
  'wiki_entry',
  'news_article',
] as const;

function migrate(): void {
  console.log(`Migrating from: ${OLD_DB_PATH}`);
  console.log(`Target: server database (from config)\n`);

  const oldDb = new Database(OLD_DB_PATH, { readonly: true });
  const newDb = getDb();

  initSchema(newDb);

  const counts: Record<string, number> = {};

  for (const table of TABLES) {
    try {
      const rows = oldDb.prepare(`SELECT * FROM ${table}`).all() as Record<
        string,
        unknown
      >[];

      if (rows.length === 0) {
        counts[table] = 0;
        console.log(`  ${table}: 0 rows (empty or table missing)`);
        continue;
      }

      const columns = Object.keys(rows[0]);
      const placeholders = columns.map(() => '?').join(', ');
      const colList = columns.join(', ');

      const insertSql = `INSERT OR IGNORE INTO ${table} (${colList}) VALUES (${placeholders})`;
      const insert = newDb.prepare(insertSql);

      const insertMany = newDb.transaction(() => {
        let inserted = 0;
        for (const row of rows) {
          const values = columns.map((c) => row[c] ?? null);
          const result = insert.run(...values);
          if (result.changes > 0) inserted++;
        }
        return inserted;
      });

      const inserted = insertMany();
      counts[table] = inserted;
      console.log(`  ${table}: ${inserted} rows inserted (${rows.length} total in source)`);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.log(`  ${table}: error - ${msg}`);
      counts[table] = 0;
    }
  }

  oldDb.close();

  console.log('\nMigration complete. Counts:');
  for (const [table, count] of Object.entries(counts)) {
    console.log(`  ${table}: ${count}`);
  }
}

migrate();
process.exit(0);
