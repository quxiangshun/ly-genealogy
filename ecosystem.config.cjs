const DEPLOY_DIR = '/var/www/genealogy'

module.exports = {
  apps: [
    {
      name: 'ly-genealogy-api',
      script: `${DEPLOY_DIR}/server/dist/index.js`,
      env: {
        NODE_ENV: 'production',
        PORT: '5001',
        JWT_SECRET: '',
        BASE_URL: 'http://39.106.39.125:9997',
        DB_PATH: `${DEPLOY_DIR}/server/data/genealogy.db`,
        UPLOAD_DIR: `${DEPLOY_DIR}/server/data/uploads`,
        ADMIN_DIST: `${DEPLOY_DIR}/admin/dist`,
      },
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: `${DEPLOY_DIR}/logs/api-error.log`,
      out_file: `${DEPLOY_DIR}/logs/api-access.log`,
      merge_logs: true,
      max_restarts: 10,
      restart_delay: 3000,
    },
    {
      name: 'ly-genealogy-web',
      script: `${DEPLOY_DIR}/web/.output/server/index.mjs`,
      env: {
        NODE_ENV: 'production',
        PORT: '3000',
        NITRO_PORT: '3000',
      },
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: `${DEPLOY_DIR}/logs/web-error.log`,
      out_file: `${DEPLOY_DIR}/logs/web-access.log`,
      merge_logs: true,
      max_restarts: 10,
      restart_delay: 3000,
    },
  ],
}
