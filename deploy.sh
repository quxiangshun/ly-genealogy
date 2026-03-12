#!/usr/bin/env bash
set -euo pipefail

# 此脚本在服务器上的部署目录内执行
# 前置步骤: 本地执行 build.sh → scp 上传 → 解压到 /var/www/genealogy/

DEPLOY_DIR="$(cd "$(dirname "$0")" && pwd)"
NODE_VERSION="22"

echo "============================================="
echo "  屈氏宗谱 服务器部署"
echo "  目录: $DEPLOY_DIR"
echo "============================================="

# ---------- 环境检查 ----------

if ! command -v node &>/dev/null; then
  echo "[1/4] 安装 Node.js $NODE_VERSION ..."
  curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi
echo "[1/4] Node.js $(node -v)"

if ! command -v pm2 &>/dev/null; then
  echo "  安装 PM2 ..."
  npm install -g pm2
fi
echo "  PM2 $(pm2 -v)"

# ---------- 安装 server 运行时依赖 ----------

echo "[2/4] 安装 server 依赖 ..."
cd "$DEPLOY_DIR/server"
npm install --omit=dev --no-package-lock 2>/dev/null || npm install --production --no-package-lock

# ---------- 初始化数据目录 ----------

echo "[3/4] 初始化数据目录 ..."
mkdir -p "$DEPLOY_DIR/server/data/uploads"
mkdir -p "$DEPLOY_DIR/logs"

# ---------- 启动服务 ----------

echo "[4/4] 启动服务 ..."
cd "$DEPLOY_DIR"

# 首次部署自动生成 JWT_SECRET
if grep -q "JWT_SECRET: ''" ecosystem.config.cjs; then
  JWT_SECRET=$(openssl rand -hex 32)
  sed -i "s|JWT_SECRET: ''|JWT_SECRET: '$JWT_SECRET'|" ecosystem.config.cjs
  echo "  已自动生成 JWT_SECRET"
fi

pm2 delete ly-genealogy-api ly-genealogy-web 2>/dev/null || true
pm2 start ecosystem.config.cjs
pm2 save

echo ""
echo "============================================="
echo "  部署完成！"
echo "============================================="
echo ""
echo "  目录结构:"
echo "    $DEPLOY_DIR/server/  Express API (端口 5001)"
echo "    $DEPLOY_DIR/admin/   管理后台 SPA"
echo "    $DEPLOY_DIR/web/     Nuxt SSR (端口 3000)"
echo ""
echo "  启动 Caddy (如未运行):"
echo "    caddy start --config $DEPLOY_DIR/Caddyfile"
echo ""
echo "  访问地址:"
echo "    前台: http://39.106.39.125:9997/"
echo "    后台: http://39.106.39.125:9997/admin/"
echo "    API:  http://39.106.39.125:9997/api/"
echo ""
echo "  默认管理员: ly-genealogy / 123456"
echo ""
