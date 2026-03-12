from flask import Flask, redirect, url_for, render_template, request, session, flash, make_response
from flask_wtf.csrf import CSRFProtect
from models import db, GenealogyMain, AdminUser
from utils.auth import login_required
from config import (
    DATABASE_URI, SECRET_KEY, DEBUG, MAX_CONTENT_LENGTH, UPLOAD_FOLDER,
    SITE_NAME, SITE_DESCRIPTION, BASE_URL,
    ADMIN_USERNAME, ADMIN_PASSWORD,
)
from routes import genealogy, member, query, culture, wiki, news

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)
CSRFProtect(app)


def mask_name(name):
    if not name or not isinstance(name, str):
        return ""
    s = name.strip()
    if not s:
        return ""
    n = len(s)
    if n == 1:
        return "*"
    if n == 2:
        return s[0] + "*"
    if n == 3:
        return s[0] + "*" + s[-1]
    if n == 4:
        return s[0] + "**" + s[-1]
    return s[:2] + "*" * (n - 4) + s[-2:]


@app.context_processor
def inject_config():
    return {
        "config": type("Config", (), {
            "BASE_URL": BASE_URL,
            "SITE_NAME": SITE_NAME,
            "SITE_DESCRIPTION": SITE_DESCRIPTION,
        })(),
        "is_logged_in": session.get("logged_in", False),
    }


@app.template_filter("mask_name")
def mask_name_filter(name):
    return mask_name(name)


import markdown as _md
from markupsafe import Markup

@app.template_filter("md")
def markdown_filter(text):
    """将 Markdown 文本转换为 HTML"""
    if not text:
        return ''
    html = _md.markdown(text, extensions=['tables', 'fenced_code', 'nl2br', 'toc'])
    return Markup(html)


app.register_blueprint(genealogy.bp)
app.register_blueprint(member.bp)
app.register_blueprint(query.bp)
app.register_blueprint(culture.bp)
app.register_blueprint(wiki.bp)
app.register_blueprint(news.bp)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        if session.get("must_change_password"):
            return redirect(url_for("change_password"))
        return redirect(url_for("index"))
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["logged_in"] = True
            session["admin_user_id"] = user.id
            if user.must_change_password:
                session["must_change_password"] = True
                flash("首次登录，请先修改默认密码", "warning")
                return redirect(url_for("change_password"))
            session.pop("must_change_password", None)
            next_url = request.args.get("next") or url_for("index")
            return redirect(next_url)
        return render_template("login.html", error="用户名或密码错误")
    return render_template("login.html")


@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    user = AdminUser.query.get(session.get("admin_user_id"))
    if not user:
        session.clear()
        return redirect(url_for("login"))
    if request.method == "POST":
        old_pwd = request.form.get("old_password", "")
        new_pwd = request.form.get("new_password", "")
        confirm_pwd = request.form.get("confirm_password", "")
        if not user.check_password(old_pwd):
            flash("当前密码错误", "danger")
        elif len(new_pwd) < 6:
            flash("新密码长度不能少于 6 位", "danger")
        elif new_pwd != confirm_pwd:
            flash("两次输入的新密码不一致", "danger")
        elif new_pwd == old_pwd:
            flash("新密码不能与当前密码相同", "danger")
        else:
            user.set_password(new_pwd)
            user.must_change_password = False
            db.session.commit()
            session.pop("must_change_password", None)
            flash("密码修改成功", "success")
            return redirect(url_for("index"))
    return render_template("change_password.html", is_forced=session.get("must_change_password", False))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/robots.txt")
def robots_txt():
    base = (BASE_URL or request.url_root.rstrip("/"))
    text = f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n"
    resp = make_response(text)
    resp.mimetype = "text/plain"
    return resp


@app.route("/sitemap.xml")
def sitemap_xml():
    import html as html_mod
    from models import WikiEntry, NewsArticle
    base = (BASE_URL or request.url_root.rstrip("/"))
    urls = [
        base + url_for("index"),
        base + url_for("genealogy.list_genealogies"),
        base + url_for("culture.index"),
        base + url_for("culture.zibei"),
        base + url_for("culture.contact"),
        base + url_for("culture.relationship"),
        base + url_for("wiki.index"),
        base + url_for("news.index"),
    ]
    for g in GenealogyMain.query.all():
        urls.append(base + url_for("genealogy.detail", genealogy_id=g.id))
    for w in WikiEntry.query.filter_by(is_published=True).all():
        urls.append(base + url_for("wiki.detail", slug=w.slug))
    for n in NewsArticle.query.filter_by(is_published=True).all():
        urls.append(base + url_for("news.detail", slug=n.slug))
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        xml += f"  <url><loc>{html_mod.escape(u)}</loc><changefreq>weekly</changefreq></url>\n"
    xml += "</urlset>"
    resp = make_response(xml)
    resp.mimetype = "application/xml"
    return resp


@app.route('/')
def index():
    from models import FamilyMember, GenealogyGeneration, WikiEntry, NewsArticle
    surnames = db.session.query(GenealogyMain.surname).distinct().order_by(GenealogyMain.surname).all()
    surnames = [s[0] for s in surnames]
    recent = GenealogyMain.query.order_by(GenealogyMain.create_time.desc()).limit(8).all()

    total_genealogies = GenealogyMain.query.count()
    total_members = FamilyMember.query.count()
    total_generations = GenealogyGeneration.query.count()
    regions = db.session.query(GenealogyMain.region).filter(
        GenealogyMain.region.isnot(None), GenealogyMain.region != ''
    ).distinct().all()
    region_list = sorted(set(r[0] for r in regions))

    recent_news = NewsArticle.query.filter_by(is_published=True).order_by(
        NewsArticle.is_pinned.desc(), NewsArticle.create_time.desc()
    ).limit(5).all()

    return render_template(
        'home.html',
        surnames=surnames,
        recent_genealogies=recent,
        total_genealogies=total_genealogies,
        total_members=total_members,
        total_generations=total_generations,
        region_list=region_list,
        recent_news=recent_news,
    )


with app.app_context():
    db.create_all()

    # SQLite: 检测并添加新列（已有数据库平滑迁移）
    from sqlalchemy import inspect as sa_inspect, text
    insp = sa_inspect(db.engine)

    _migrate_map = {
        'family_member': [('path', 'VARCHAR(2000)')],
        'wiki_entry': [('view_count', 'INTEGER DEFAULT 0')],
        'news_article': [('view_count', 'INTEGER DEFAULT 0')],
    }
    for table, columns in _migrate_map.items():
        try:
            existing = [c['name'] for c in insp.get_columns(table)]
        except Exception:
            continue
        for col_name, col_type in columns:
            if col_name not in existing:
                db.session.execute(text(f'ALTER TABLE {table} ADD COLUMN {col_name} {col_type}'))
    db.session.commit()

    # 为缺少 path 的成员自动重建
    from models import FamilyMember
    need_rebuild = FamilyMember.query.filter(
        (FamilyMember.path == None) | (FamilyMember.path == '')
    ).first()
    if need_rebuild:
        gids = db.session.query(FamilyMember.genealogy_id).distinct().all()
        for (gid,) in gids:
            FamilyMember.rebuild_paths(gid)

    if not AdminUser.query.first():
        default_admin = AdminUser(username=ADMIN_USERNAME, must_change_password=True)
        default_admin.set_password(ADMIN_PASSWORD)
        db.session.add(default_admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
