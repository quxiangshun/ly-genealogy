import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const config = {
  PORT: parseInt(process.env.PORT ?? '5001', 10),
  JWT_SECRET: process.env.JWT_SECRET ?? 'genealogy_jwt_secret_change_in_production',
  DB_PATH: process.env.DB_PATH || path.resolve(__dirname, '../data/genealogy.db'),
  UPLOAD_DIR: process.env.UPLOAD_DIR || path.resolve(__dirname, '../data/uploads'),
  ADMIN_DIST: process.env.ADMIN_DIST || path.resolve(__dirname, '../../admin/dist'),
  ADMIN_USERNAME: process.env.ADMIN_USERNAME ?? 'ly-genealogy',
  ADMIN_PASSWORD: process.env.ADMIN_PASSWORD ?? '123456',
  SITE_NAME: process.env.SITE_NAME ?? '屈氏宗谱',
  BASE_URL: process.env.BASE_URL ?? '',
} as const;
