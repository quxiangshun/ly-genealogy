import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 数据库路径
DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'genealogy.db')}"
# Flask配置
SECRET_KEY = "genealogy_system_2026"
DEBUG = True

# 成员照片上传
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'members')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

# SEO / 站点信息（用于 canonical、Open Graph、sitemap）
SITE_NAME = "屈氏宗谱"
SITE_DESCRIPTION = "屈氏宗亲族谱与文化传承，按地区年代检索屈氏族谱，字辈表、成员查询、世系树。"
# 部署时改为实际域名，如 https://qu.example.com
BASE_URL = os.environ.get("BASE_URL", "").rstrip("/") or None

# 管理登录（首次启动自动创建，首次登录必须修改密码）
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "ly-genealogy")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "123456")
