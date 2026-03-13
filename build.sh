#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$SRC_DIR/.deploy"
ARCHIVE="$SRC_DIR/genealogy-release.tar.gz"

echo "============================================="
echo "  屈氏宗谱 本地构建 & 打包"
echo "============================================="

cd "$SRC_DIR"

echo "[1/5] 安装依赖 ..."
pnpm install

echo "[2/5] 构建 Express API ..."
pnpm --filter @ly/server build

echo "[3/5] 构建 Admin SPA ..."
pnpm --filter @ly/admin build

echo "[4/5] 构建 Nuxt 前端 ..."
pnpm --filter @ly/web build

echo "[5/5] 打包发布文件 ..."
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"/{server,admin/dist,web,logs}

# Server: dist + 为 Linux 安装生产依赖
cp -r "$SRC_DIR/packages/server/dist" "$DIST_DIR/server/dist"
cp "$SRC_DIR/packages/server/package.json" "$DIST_DIR/server/package.json"
cd "$DIST_DIR/server"
npm install --omit=dev --os=linux --cpu=x64

# Admin: 纯静态文件
cp -r "$SRC_DIR/packages/admin/dist/"* "$DIST_DIR/admin/dist/"

# Web: Nuxt .output（自包含）
cp -r "$SRC_DIR/packages/web/.output" "$DIST_DIR/web/.output"

# 部署配置
cp "$SRC_DIR/ecosystem.config.cjs" "$DIST_DIR/"
cp "$SRC_DIR/Caddyfile" "$DIST_DIR/"

cd "$DIST_DIR"
tar -czf "$ARCHIVE" .
rm -rf "$DIST_DIR"

SIZE=$(du -sh "$ARCHIVE" | cut -f1)
echo ""
echo "============================================="
echo "  构建完成！发布包: genealogy-release.tar.gz ($SIZE)"
echo "============================================="
echo ""
echo "  部署到服务器:"
echo "    scp genealogy-release.tar.gz root@39.106.39.125:/var/www/"
echo "    ssh root@39.106.39.125 'mkdir -p /var/www/genealogy && cd /var/www/genealogy && tar -xzf /var/www/genealogy-release.tar.gz && pm2 start ecosystem.config.cjs'"
echo ""
