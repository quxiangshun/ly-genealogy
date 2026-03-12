#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/var/www/genealogy"

echo "===== 屈氏宗谱 Ubuntu 部署脚本 ====="

# ---------- 1. 系统依赖 ----------
echo "[1/6] 检查系统依赖..."
NEED_INSTALL=()
command -v python3 &>/dev/null || NEED_INSTALL+=(python3 python3-venv python3-pip)
command -v node    &>/dev/null || NEED_INSTALL+=(nodejs npm)

if [ ${#NEED_INSTALL[@]} -gt 0 ]; then
  echo "  安装: ${NEED_INSTALL[*]}"
  sudo apt update -y
  sudo apt install -y "${NEED_INSTALL[@]}"
else
  echo "  系统依赖已就绪，跳过"
fi

if ! command -v pm2 &>/dev/null; then
  echo "  安装 pm2..."
  sudo npm install -g pm2
else
  echo "  pm2 已安装，跳过"
fi

# ---------- 2. 创建日志目录 ----------
echo "[2/6] 检查日志目录..."
if [ -d "$APP_DIR/logs" ]; then
  echo "  目录已存在，跳过"
else
  mkdir -p "$APP_DIR/logs"
  echo "  已创建 $APP_DIR/logs"
fi

# ---------- 3. Python 虚拟环境 ----------
echo "[3/6] 检查 Python 虚拟环境..."
cd "$APP_DIR"

if [ -d ".venv" ]; then
  echo "  虚拟环境已存在，跳过创建"
else
  echo "  创建虚拟环境..."
  python3 -m venv .venv
fi

source .venv/bin/activate

if ! .venv/bin/python -m pip show gunicorn &>/dev/null; then
  echo "  安装 gunicorn..."
  pip install --upgrade pip
  pip install gunicorn
else
  echo "  gunicorn 已安装，跳过"
fi

echo "  同步 requirements.txt 依赖..."
pip install -r requirements.txt

# ---------- 4. 生成 SECRET_KEY ----------
echo "[4/6] 检查 SECRET_KEY..."
CURRENT_SK=$(node -p "require('./ecosystem.config.js').apps[0].env.SECRET_KEY" 2>/dev/null || echo "")
if [ -z "$CURRENT_SK" ]; then
  SK=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  echo "  生成的 SECRET_KEY: $SK"
  echo "  请将此值填入 ecosystem.config.js 的 SECRET_KEY 字段"
else
  echo "  SECRET_KEY 已配置，跳过"
fi

# ---------- 5. 初始化数据库 ----------
echo "[5/6] 检查数据库..."
if [ -f "$APP_DIR/genealogy.db" ]; then
  echo "  数据库已存在，跳过初始化"
else
  echo "  初始化数据库..."
  python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('  数据库初始化完成')"
fi

# ---------- 6. 使用 PM2 启动 ----------
echo "[6/6] 启动应用..."
if pm2 describe ly-genealogy &>/dev/null; then
  echo "  应用已在运行，执行重启..."
  pm2 restart ly-genealogy
else
  echo "  首次启动应用..."
  pm2 start ecosystem.config.js
fi
pm2 save

# 设置开机自启（仅首次需要）
if ! systemctl is-enabled pm2-"$USER" &>/dev/null 2>&1; then
  echo "  配置 PM2 开机自启..."
  pm2 startup systemd -u "$USER" --hp "$HOME" | tail -1 | sudo bash
  pm2 save
else
  echo "  PM2 开机自启已配置，跳过"
fi

echo ""
echo "===== 部署完成 ====="
echo "应用已在 127.0.0.1:5001 上运行"
echo ""
echo "下一步：配置 Caddy 反向代理（参考项目中的 Caddyfile）"
