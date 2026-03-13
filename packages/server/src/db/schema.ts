import type Database from 'better-sqlite3';
import { runMigrations } from './migrations.js';

export function initSchema(db: Database.Database): void {
  db.exec(`
    CREATE TABLE IF NOT EXISTS admin_user (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT NOT NULL UNIQUE,
      password_hash TEXT NOT NULL,
      must_change_password INTEGER DEFAULT 1,
      create_time TEXT DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS genealogy_main (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      surname TEXT NOT NULL,
      genealogy_name TEXT NOT NULL,
      region TEXT,
      period TEXT,
      volumes TEXT,
      hall_name TEXT,
      source_url TEXT,
      founder_info TEXT,
      collection_info TEXT,
      scattered_region TEXT,
      description TEXT,
      create_time TEXT DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS genealogy_generation (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      genealogy_id INTEGER NOT NULL REFERENCES genealogy_main(id) ON DELETE CASCADE,
      sort_order INTEGER NOT NULL DEFAULT 0,
      character TEXT NOT NULL,
      note TEXT
    );

    CREATE TABLE IF NOT EXISTS family_member (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      genealogy_id INTEGER NOT NULL REFERENCES genealogy_main(id) ON DELETE CASCADE,
      name TEXT NOT NULL,
      former_name TEXT,
      gender TEXT NOT NULL DEFAULT 'M',
      generation_number INTEGER,
      courtesy_name TEXT,
      birth_date TEXT,
      death_date TEXT,
      birth_place TEXT,
      father_id INTEGER REFERENCES family_member(id) ON DELETE SET NULL,
      mother_id INTEGER REFERENCES family_member(id) ON DELETE SET NULL,
      spouse_name TEXT,
      photo TEXT,
      notes TEXT,
      path TEXT
    );

    CREATE TABLE IF NOT EXISTS wiki_entry (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      slug TEXT NOT NULL UNIQUE,
      category TEXT NOT NULL DEFAULT 'other',
      summary TEXT,
      content TEXT NOT NULL,
      cover_image TEXT,
      era TEXT,
      is_published INTEGER DEFAULT 1,
      sort_order INTEGER DEFAULT 0,
      view_count INTEGER DEFAULT 0,
      create_time TEXT DEFAULT (datetime('now','localtime')),
      update_time TEXT DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS news_article (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      slug TEXT NOT NULL UNIQUE,
      category TEXT NOT NULL DEFAULT 'other',
      summary TEXT,
      content TEXT NOT NULL,
      cover_image TEXT,
      source TEXT,
      event_date TEXT,
      is_published INTEGER DEFAULT 1,
      is_pinned INTEGER DEFAULT 0,
      view_count INTEGER DEFAULT 0,
      create_time TEXT DEFAULT (datetime('now','localtime')),
      update_time TEXT DEFAULT (datetime('now','localtime'))
    );
  `);

  runMigrations(db);
}
