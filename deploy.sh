#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
DEPLOY_DIR="/var/www/genealogy"
NODE_VERSION="22"

echo "============================================="
echo "  屈氏宗谱 部署脚本"
echo "  源码: $SRC_DIR"
echo "  部署: $DEPLOY_DIR"
echo "============================================="

# ---------- 环境检查 ----------

if ! command -v node &>/dev/null; then
  echo "[1/8] 安装 Node.js $NODE_VERSION ..."
  curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi
echo "[1/8] Node.js $(node -v)"

if ! command -v pnpm &>/dev/null; then
  echo "[2/8] 安装 pnpm ..."
  npm install -g pnpm
fi
if ! command -v pm2 &>/dev/null; then
  echo "[2/8] 安装 PM2 ..."
  npm install -g pm2
fi
echo "[2/8] pnpm $(pnpm -v), PM2 $(pm2 -v)"

# ---------- 构建 ----------

echo "[3/8] 安装项目依赖 ..."
cd "$SRC_DIR"
pnpm install

echo "[4/8] 构建 Express API ..."
pnpm --filter @ly/server build

echo "[5/8] 构建 Admin SPA ..."
pnpm --filter @ly/admin build

echo "[6/8] 构建 Nuxt 前端 ..."
pnpm --filter @ly/web build

# ---------- 部署到目标目录 ----------

echo "[7/8] 部署文件到 $DEPLOY_DIR ..."

mkdir -p "$DEPLOY_DIR"/{server,admin,web,logs}
mkdir -p "$DEPLOY_DIR/server/data/uploads"

# Server: dist + package.json + 安装生产依赖
rm -rf "$DEPLOY_DIR/server/dist"
cp -r "$SRC_DIR/packages/server/dist" "$DEPLOY_DIR/server/dist"
cp "$SRC_DIR/packages/server/package.json" "$DEPLOY_DIR/server/package.json"
cd "$DEPLOY_DIR/server"
npm install --omit=dev --no-package-lock 2>/dev/null || npm install --production --no-package-lock

# Admin: 静态文件
rm -rf "$DEPLOY_DIR/admin/dist"
cp -r "$SRC_DIR/packages/admin/dist" "$DEPLOY_DIR/admin/dist"

# Web: Nuxt .output (自包含)
rm -rf "$DEPLOY_DIR/web/.output"
cp -r "$SRC_DIR/packages/web/.output" "$DEPLOY_DIR/web/.output"

# 配置文件
cp "$SRC_DIR/ecosystem.config.cjs" "$DEPLOY_DIR/ecosystem.config.cjs"
cp "$SRC_DIR/Caddyfile" "$DEPLOY_DIR/Caddyfile"

# ---------- 数据迁移（首次部署可选） ----------

cd "$SRC_DIR"
if [ ! -f "$DEPLOY_DIR/server/data/genealogy.db" ]; then
  if [ -f "/var/www/genealogy-old/genealogy.db" ]; then
    echo "[8/8] 从旧数据库迁移数据 ..."
    DB_PATH="$DEPLOY_DIR/server/data/genealogy.db" \
      pnpm --filter @ly/server migrate -- /var/www/genealogy-old/genealogy.db
  else
    echo "[8/8] 运行种子数据 ..."
    DB_PATH="$DEPLOY_DIR/server/data/genealogy.db" \
      pnpm --filter @ly/server seed
  fi
else
  echo "[8/8] 数据库已存在，跳过迁移"
fi

# ---------- 启动服务 ----------

echo "============================================="
echo "  启动服务 ..."
echo "============================================="

cd "$DEPLOY_DIR"

# 检查 JWT_SECRET
if grep -q "JWT_SECRET: ''" ecosystem.config.cjs; then
  JWT_SECRET=$(openssl rand -hex 32)
  sed -i "s|JWT_SECRET: ''|JWT_SECRET: '$JWT_SECRET'|" ecosystem.config.cjs
  echo "已自动生成 JWT_SECRET"
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
echo "  访问地址 (需启动 Caddy):"
echo "    前台: http://39.106.39.125:9997/"
echo "    后台: http://39.106.39.125:9997/admin/"
echo "    API:  http://39.106.39.125:9997/api/"
echo ""
echo "  启动 Caddy:"
echo "    caddy start --config $DEPLOY_DIR/Caddyfile"
echo ""
