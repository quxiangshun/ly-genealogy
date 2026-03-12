module.exports = {
  apps: [
    {
      name: "ly-genealogy",
      script: "/var/www/genealogy/.venv/bin/gunicorn",
      args: "-w 2 -b 127.0.0.1:5001 --timeout 120 app:app",
      cwd: "/var/www/genealogy",
      interpreter: "none",
      env: {
        FLASK_ENV: "production",
        // BASE_URL 填你的域名，用于 SEO（sitemap、Open Graph 等生成完整链接）
        // 如果还没有域名，可以先留空或填服务器 IP
        BASE_URL: "",
        // 在服务器上运行: python3 -c "import secrets; print(secrets.token_hex(32))"
        // 将输出的随机字符串粘贴到这里
        SECRET_KEY: "1ba1a14429ee60625f7d69dd891ae514fd94173503903e55",
      },
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      error_file: "/var/www/genealogy/logs/error.log",
      out_file: "/var/www/genealogy/logs/access.log",
      merge_logs: true,
      max_restarts: 10,
      restart_delay: 3000,
    },
  ],
};
