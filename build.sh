#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$SRC_DIR/.deploy"
ARCHIVE="$SRC_DIR/genealogy-release.tar.gz"

echo "============================================="
echo "  屈氏宗谱 本地构建 & 打包"
echo "============================================="

# 1. 安装依赖
echo "[1/5] 安装依赖 ..."
cd "$SRC_DIR"
pnpm install

# 2. 构建三个项目
echo "[2/5] 构建 Express API ..."
pnpm --filter @ly/server build

echo "[3/5] 构建 Admin SPA ..."
pnpm --filter @ly/admin build

echo "[4/5] 构建 Nuxt 前端 ..."
pnpm --filter @ly/web build

# 5. 组装部署目录
echo "[5/5] 打包发布文件 ..."

rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"/{server,admin/dist,web}

# Server: dist + package.json
cp -r "$SRC_DIR/packages/server/dist" "$DIST_DIR/server/dist"
cp "$SRC_DIR/packages/server/package.json" "$DIST_DIR/server/package.json"

# Admin: 静态文件
cp -r "$SRC_DIR/packages/admin/dist/"* "$DIST_DIR/admin/dist/"

# Web: Nuxt .output（自包含，含内置 node_modules）
cp -r "$SRC_DIR/packages/web/.output" "$DIST_DIR/web/.output"

# 配置文件
cp "$SRC_DIR/ecosystem.config.cjs" "$DIST_DIR/"
cp "$SRC_DIR/Caddyfile" "$DIST_DIR/"
cp "$SRC_DIR/deploy.sh" "$DIST_DIR/"

# 打包
cd "$DIST_DIR"
tar -czf "$ARCHIVE" .

rm -rf "$DIST_DIR"

echo ""
echo "============================================="
echo "  构建完成！"
echo "============================================="
echo ""
echo "  发布包: $ARCHIVE"
echo "  大小: $(du -sh "$ARCHIVE" | cut -f1)"
echo ""
echo "  上传到服务器:"
echo "    scp genealogy-release.tar.gz root@39.106.39.125:/tmp/"
echo ""
echo "  在服务器上执行:"
echo "    mkdir -p /var/www/genealogy && cd /var/www/genealogy"
echo "    tar -xzf /tmp/genealogy-release.tar.gz"
echo "    bash deploy.sh"
echo ""
