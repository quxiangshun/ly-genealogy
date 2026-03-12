#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/var/www/genealogy-node"
NODE_VERSION="22"

echo "============================================="
echo "  屈氏宗谱 Node.js 部署脚本"
echo "============================================="

# 1. 检查 Node.js
if ! command -v node &>/dev/null; then
  echo "[1/7] 安装 Node.js $NODE_VERSION ..."
  curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi
echo "[1/7] Node.js $(node -v)"

# 2. 安装 pnpm / PM2
if ! command -v pnpm &>/dev/null; then
  echo "[2/7] 安装 pnpm ..."
  npm install -g pnpm
fi
if ! command -v pm2 &>/dev/null; then
  echo "[2/7] 安装 PM2 ..."
  npm install -g pm2
fi
echo "[2/7] pnpm $(pnpm -v), PM2 $(pm2 -v)"

# 3. 安装依赖
echo "[3/7] 安装项目依赖 ..."
cd "$APP_DIR"
pnpm install

# 4. 构建
echo "[4/7] 构建 Express API ..."
pnpm --filter @ly/server build

echo "[5/7] 构建 Admin SPA ..."
pnpm --filter @ly/admin build

echo "[6/7] 构建 Nuxt 前端 ..."
pnpm --filter @ly/web build

# 7. 迁移数据（可选）
if [ -f "/var/www/genealogy/genealogy.db" ]; then
  echo "[7/7] 从旧数据库迁移数据 ..."
  pnpm --filter @ly/server migrate -- /var/www/genealogy/genealogy.db
else
  echo "[7/7] 运行种子数据 ..."
  pnpm --filter @ly/server seed
fi

# 创建日志目录
mkdir -p logs

# 启动 PM2
echo "============================================="
echo "  启动服务 ..."
echo "============================================="

# 生成 JWT_SECRET
if [ -z "$(grep 'JWT_SECRET' ecosystem.config.cjs | grep -v '^\s*//' | grep -v "''$")" ]; then
  JWT_SECRET=$(openssl rand -hex 32)
  echo "生成 JWT_SECRET: $JWT_SECRET"
  echo "请将其填入 ecosystem.config.cjs 的 JWT_SECRET 字段"
fi

pm2 start ecosystem.config.cjs
pm2 save

echo ""
echo "部署完成！"
echo "  API:   http://localhost:5001"
echo "  Admin: http://localhost:5001/admin/"
echo ""
echo "还需要："
echo "  1. 配置 Caddy (参考 Caddyfile)"
echo "  2. 启动 Nuxt: cd $APP_DIR && node packages/web/.output/server/index.mjs"
echo "  3. 或用 PM2 管理 Nuxt 进程"
