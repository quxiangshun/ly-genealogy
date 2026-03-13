$ErrorActionPreference = "Stop"

$SRC_DIR = $PSScriptRoot
$DIST_DIR = "$SRC_DIR\.deploy"
$ARCHIVE = "$SRC_DIR\genealogy-release.tar.gz"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  屈氏宗谱 本地构建 & 打包 (Windows)" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

Set-Location $SRC_DIR

Write-Host "`n[1/5] 安装依赖 ..." -ForegroundColor Yellow
pnpm install
if ($LASTEXITCODE -ne 0) { throw "pnpm install failed" }

Write-Host "`n[2/5] 构建 Express API ..." -ForegroundColor Yellow
pnpm --filter @ly/server build
if ($LASTEXITCODE -ne 0) { throw "server build failed" }

Write-Host "`n[3/5] 构建 Admin SPA ..." -ForegroundColor Yellow
pnpm --filter @ly/admin build
if ($LASTEXITCODE -ne 0) { throw "admin build failed" }

Write-Host "`n[4/5] 构建 Nuxt 前端 ..." -ForegroundColor Yellow
pnpm --filter @ly/web build
if ($LASTEXITCODE -ne 0) { throw "web build failed" }

Write-Host "`n[5/5] 打包发布文件 ..." -ForegroundColor Yellow

if (Test-Path $DIST_DIR) { Remove-Item $DIST_DIR -Recurse -Force }
New-Item -ItemType Directory -Path "$DIST_DIR\server" -Force | Out-Null
New-Item -ItemType Directory -Path "$DIST_DIR\admin\dist" -Force | Out-Null
New-Item -ItemType Directory -Path "$DIST_DIR\web" -Force | Out-Null
New-Item -ItemType Directory -Path "$DIST_DIR\logs" -Force | Out-Null
New-Item -ItemType Directory -Path "$DIST_DIR\server\data\uploads" -Force | Out-Null

# Server: dist + package.json
Copy-Item -Path "$SRC_DIR\packages\server\dist" -Destination "$DIST_DIR\server\dist" -Recurse
Copy-Item -Path "$SRC_DIR\packages\server\package.json" -Destination "$DIST_DIR\server\package.json"

# Admin: 纯静态文件
Copy-Item -Path "$SRC_DIR\packages\admin\dist\*" -Destination "$DIST_DIR\admin\dist\" -Recurse

# Web: Nuxt .output（自包含）
Copy-Item -Path "$SRC_DIR\packages\web\.output" -Destination "$DIST_DIR\web\.output" -Recurse

# 部署配置
Copy-Item "$SRC_DIR\ecosystem.config.cjs" "$DIST_DIR\"
Copy-Item "$SRC_DIR\Caddyfile" "$DIST_DIR\"
Copy-Item "$SRC_DIR\deploy.sh" "$DIST_DIR\"

# 打包
Set-Location $DIST_DIR
if (Test-Path $ARCHIVE) { Remove-Item $ARCHIVE -Force }
tar -czf $ARCHIVE *

Set-Location $SRC_DIR
Remove-Item $DIST_DIR -Recurse -Force

$size = "{0:N1} MB" -f ((Get-Item $ARCHIVE).Length / 1MB)

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "  构建完成！" -ForegroundColor Green
Write-Host "  发布包: genealogy-release.tar.gz ($size)" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  部署步骤:" -ForegroundColor White
Write-Host '    1. scp genealogy-release.tar.gz root@39.106.39.125:/var/www/' -ForegroundColor Gray
Write-Host '    2. ssh root@39.106.39.125' -ForegroundColor Gray
Write-Host '    3. mkdir -p /var/www/genealogy; cd /var/www/genealogy' -ForegroundColor Gray
Write-Host '    4. tar -xzf /var/www/genealogy-release.tar.gz' -ForegroundColor Gray
Write-Host '    5. bash deploy.sh' -ForegroundColor Gray
Write-Host '    6. caddy start --config /var/www/genealogy/Caddyfile' -ForegroundColor Gray
Write-Host ""
