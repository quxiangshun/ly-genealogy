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

### 第一步：本地构建打包

```bash
bash build.sh
```

生成 `genealogy-release.tar.gz`，包含所有构建产物和 Linux 运行依赖，服务器无需安装任何构建工具。

### 第二步：上传并部署

```bash
scp genealogy-release.tar.gz root@39.106.39.125:/var/www/
ssh root@39.106.39.125

# 服务器上执行
mkdir -p /var/www/genealogy && cd /var/www/genealogy
tar -xzf /var/www/genealogy-release.tar.gz
bash deploy.sh
caddy start --config /var/www/genealogy/Caddyfile
```

服务器只需预装 Node.js、PM2、Caddy。`deploy.sh` 仅创建数据目录和启动 PM2，不执行 install 或 build。

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
