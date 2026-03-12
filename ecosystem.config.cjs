module.exports = {
  apps: [
    {
      name: 'ly-genealogy-api',
      script: 'packages/server/dist/index.js',
      cwd: __dirname,
      interpreter: 'none',
      env: {
        NODE_ENV: 'production',
        PORT: '5001',
        JWT_SECRET: '',
        BASE_URL: '',
      },
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: 'logs/api-error.log',
      out_file: 'logs/api-access.log',
      merge_logs: true,
      max_restarts: 10,
      restart_delay: 3000,
    },
  ],
}
