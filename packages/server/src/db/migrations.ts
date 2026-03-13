import type Database from 'better-sqlite3';

export interface Migration {
  version: number;
  description: string;
  up: (db: Database.Database) => void;
}

function ensureVersionTable(db: Database.Database): void {
  db.exec(`
    CREATE TABLE IF NOT EXISTS schema_version (
      version INTEGER PRIMARY KEY,
      description TEXT NOT NULL,
      applied_at TEXT DEFAULT (datetime('now','localtime'))
    )
  `);
}

function getCurrentVersion(db: Database.Database): number {
  const row = db.prepare(
    'SELECT MAX(version) AS v FROM schema_version'
  ).get() as { v: number | null } | undefined;
  return row?.v ?? 0;
}

function hasColumn(db: Database.Database, table: string, column: string): boolean {
  const cols = db.prepare(`PRAGMA table_info(${table})`).all() as { name: string }[];
  return cols.some(c => c.name === column);
}

// ─── 迁移定义 ───────────────────────────────────────
// 每次数据库结构变更，在此数组末尾追加一条即可。
// version 必须递增，up() 中只写增量 DDL，不要删除旧迁移。

const migrations: Migration[] = [
  {
    version: 1,
    description: 'family_member 添加 former_name 字段',
    up(db) {
      if (!hasColumn(db, 'family_member', 'former_name')) {
        db.exec('ALTER TABLE family_member ADD COLUMN former_name TEXT');
      }
    },
  },
  // ── 后续新增迁移示例 ──
  // {
  //   version: 2,
  //   description: '新增 xxx 表',
  //   up(db) {
  //     db.exec(`CREATE TABLE IF NOT EXISTS xxx (...)`);
  //   },
  // },
];

// ─── 迁移执行器 ─────────────────────────────────────

export function runMigrations(db: Database.Database): void {
  ensureVersionTable(db);
  const current = getCurrentVersion(db);

  const pending = migrations.filter(m => m.version > current);
  if (pending.length === 0) return;

  const insert = db.prepare(
    'INSERT INTO schema_version (version, description) VALUES (?, ?)'
  );

  for (const m of pending) {
    db.transaction(() => {
      m.up(db);
      insert.run(m.version, m.description);
    })();
    console.log(`  migration v${m.version}: ${m.description}`);
  }

  console.log(`Database migrated: v${current} → v${pending[pending.length - 1].version}`);
}
