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

```
├── packages/
│   ├── server/          # Express API
│   ├── web/             # Nuxt 3 公共前端
│   └── admin/           # Vue Admin SPA
├── docs/                # 族谱原始资料（PDF/DOC）
├── ecosystem.config.cjs # PM2 配置
├── Caddyfile            # Caddy 反向代理
└── deploy.sh            # Ubuntu 部署脚本
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
- 管理后台: http://localhost:3002/admin/

### 种子数据

```bash
pnpm seed
```

### 从旧数据库迁移

```bash
pnpm migrate -- /path/to/old/genealogy.db
```

## 生产部署

### 构建

```bash
pnpm build
```

### PM2 启动

```bash
# 编辑 ecosystem.config.cjs 中的 JWT_SECRET
pm2 start ecosystem.config.cjs
node packages/web/.output/server/index.mjs
```

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
