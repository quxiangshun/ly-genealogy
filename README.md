# 屈氏宗谱

基于 Node.js 技术栈的屈氏宗谱数字化平台，包含公共前端（H5 移动端适配）、管理后台和 REST API。

## 技术栈

| 模块 | 技术 | 说明 |
|------|------|------|
| API 后端 | Express + TypeScript | REST API、JWT 认证、文件上传 |
| 数据库 | better-sqlite3 | 高性能同步 SQLite |
| 公共前端 | Nuxt 3 + Vue 3 | SSR/SSG/ISR，SEO 友好，PWA |
| 管理后台 | Vue 3 + Element Plus | SPA，独立构建 |
| 包管理 | pnpm workspace | Monorepo |

## 目录结构

**源码（开发）：**

```
├── packages/
│   ├── server/          # Express API
│   ├── web/             # Nuxt 3 公共前端
│   └── admin/           # Vue Admin SPA
├── docs/                # 族谱原始资料（PDF/DOC）
├── ecosystem.config.cjs # PM2 配置
├── Caddyfile            # Caddy 反向代理（端口 9997）
└── deploy.sh            # 一键部署脚本
```

**生产部署（/var/www/genealogy/）：**

```
├── server/              # Express API
│   ├── dist/            # 编译后的 JS
│   ├── data/            # SQLite 数据库 + 上传文件
│   ├── node_modules/    # 运行时依赖
│   └── package.json
├── admin/
│   └── dist/            # 管理后台静态文件
├── web/
│   └── .output/         # Nuxt SSR 构建产物
├── logs/                # 日志
├── ecosystem.config.cjs # PM2 配置
└── Caddyfile            # Caddy 反向代理
```

## 快速开始

### 安装依赖

```bash
pnpm install
```

### 开发模式

```bash
# 终端 1: 启动 API
pnpm dev:server

# 终端 2: 启动 Nuxt 前端
pnpm dev:web

# 终端 3: 启动 Admin
pnpm dev:admin
```

- API: http://localhost:5001
- 前端: http://localhost:3000
- 管理后台: http://localhost:3001/admin/

## 生产部署

### 一键部署

```bash
# 在源码目录执行（自动构建 + 部署到 /var/www/genealogy/）
bash deploy.sh
```

脚本会自动：构建三个项目 → 复制到 `/var/www/genealogy/{server,admin,web}` → 安装 server 生产依赖 → PM2 启动

### 手动部署

```bash
# 1. 构建
pnpm build

# 2. 启动 PM2（在部署目录）
cd /var/www/genealogy
pm2 start ecosystem.config.cjs

# 3. 启动 Caddy（监听 9997 端口）
caddy start --config Caddyfile
```

### 服务架构

```
浏览器 → Caddy(:9997)
              ├─ /api/*     → Express(:5001)
              ├─ /admin/*   → Express(:5001) → 静态文件
              ├─ /uploads/* → Express(:5001)
              └─ /*         → Nuxt SSR(:3000)
```

生产访问地址：
- 前台: http://39.106.39.125:9997/
- 后台: http://39.106.39.125:9997/admin/
- API:  http://39.106.39.125:9997/api/

### 默认管理员

- 用户名: `ly-genealogy`
- 密码: `123456`
- 首次登录需要修改密码

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login | 登录 |
| POST | /api/auth/change-password | 修改密码 |
| GET | /api/genealogies | 族谱列表 |
| GET | /api/genealogies/:id | 族谱详情 |
| GET | /api/generations/:id | 字辈列表 |
| GET | /api/members | 成员列表 |
| GET | /api/query/autocomplete | 成员搜索 |
| POST | /api/culture/relationship | 亲缘查询 |
| GET | /api/culture/zibei | 字辈搜索 |
| GET | /api/wiki | 百科列表 |
| GET | /api/wiki/:slug | 百科详情 |
| GET | /api/news | 新闻列表 |
| GET | /api/news/:slug | 新闻详情 |
| GET | /api/stats | 统计数据 |

## License

见 [LICENSE](LICENSE) 文件。
