#!/usr/bin/env bash
set -euo pipefail

# 在服务器上执行：解压发布包后启动服务
# 前提：已安装 node、pm2、caddy

DEPLOY_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$DEPLOY_DIR/server/data/uploads"
mkdir -p "$DEPLOY_DIR/logs"

# 安装 server 运行依赖（下载 Linux 预编译二进制，无需编译工具）
cd "$DEPLOY_DIR/server"
npm install --omit=dev
cd "$DEPLOY_DIR"

# 首次部署自动生成 JWT_SECRET
if grep -q "JWT_SECRET: ''" ecosystem.config.cjs; then
  JWT_SECRET=$(openssl rand -hex 32)
  sed -i "s|JWT_SECRET: ''|JWT_SECRET: '$JWT_SECRET'|" ecosystem.config.cjs
  echo "已生成 JWT_SECRET"
fi

pm2 delete ly-genealogy-api ly-genealogy-web 2>/dev/null || true
pm2 start ecosystem.config.cjs
pm2 save

echo ""
echo "服务已启动！"
echo "  前台: http://39.106.39.125:9997/"
echo "  后台: http://39.106.39.125:9997/admin/"
echo ""
echo "如 Caddy 未运行: caddy start --config $DEPLOY_DIR/Caddyfile"
