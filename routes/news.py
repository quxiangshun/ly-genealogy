from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, NewsArticle, NEWS_CATEGORIES, NEWS_CAT_MAP, _slugify
from utils.auth import login_required

bp = Blueprint('news', __name__, url_prefix='/news')


@bp.route('/')
def index():
    """新闻动态列表"""
    cat = request.args.get('cat', '')
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    query = NewsArticle.query.filter_by(is_published=True)
    if cat and cat in NEWS_CAT_MAP:
        query = query.filter_by(category=cat)
    if q:
        query = query.filter(
            db.or_(NewsArticle.title.contains(q), NewsArticle.summary.contains(q))
        )
    articles = query.order_by(
        NewsArticle.is_pinned.desc(), NewsArticle.create_time.desc()
    ).paginate(page=page, per_page=12, error_out=False)

    cat_counts = {}
    for code, _ in NEWS_CATEGORIES:
        cat_counts[code] = NewsArticle.query.filter_by(is_published=True, category=code).count()

    hot_articles = NewsArticle.query.filter_by(is_published=True).order_by(
        NewsArticle.view_count.desc()
    ).limit(5).all()

    total_views = db.session.query(db.func.sum(NewsArticle.view_count)).filter(
        NewsArticle.is_published == True
    ).scalar() or 0

    return render_template(
        'news_index.html',
        articles=articles, cat=cat, q=q,
        categories=NEWS_CATEGORIES, cat_counts=cat_counts,
        hot_articles=hot_articles, total_views=total_views,
    )


@bp.route('/<slug>')
def detail(slug):
    """新闻详情"""
    article = NewsArticle.query.filter_by(slug=slug, is_published=True).first_or_404()
    article.view_count = (article.view_count or 0) + 1
    db.session.commit()
    prev_art = NewsArticle.query.filter(
        NewsArticle.is_published == True,
        NewsArticle.create_time < article.create_time,
    ).order_by(NewsArticle.create_time.desc()).first()
    next_art = NewsArticle.query.filter(
        NewsArticle.is_published == True,
        NewsArticle.create_time > article.create_time,
    ).order_by(NewsArticle.create_time.asc()).first()
    return render_template('news_detail.html', article=article, prev_art=prev_art, next_art=next_art)


# ========== 后台管理 ==========

@bp.route('/admin')
@login_required
def admin_list():
    page = request.args.get('page', 1, type=int)
    articles = NewsArticle.query.order_by(
        NewsArticle.create_time.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    return render_template('news_admin_list.html', articles=articles, categories=NEWS_CATEGORIES)


@bp.route('/admin/add', methods=['GET', 'POST'])
@login_required
def admin_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('标题不能为空', 'danger')
            return render_template('news_admin_form.html', article=None, categories=NEWS_CATEGORIES, title_text='发布新闻')
        slug = request.form.get('slug', '').strip() or _slugify(title)
        if NewsArticle.query.filter_by(slug=slug).first():
            slug = slug + '-' + str(int(__import__('time').time()))
        article = NewsArticle(
            title=title, slug=slug,
            category=request.form.get('category', 'other'),
            summary=request.form.get('summary', '').strip() or None,
            content=request.form.get('content', ''),
            cover_image=request.form.get('cover_image', '').strip() or None,
            source=request.form.get('source', '').strip() or None,
            event_date=request.form.get('event_date', '').strip() or None,
            is_published=request.form.get('is_published') == '1',
            is_pinned=request.form.get('is_pinned') == '1',
        )
        db.session.add(article)
        db.session.commit()
        flash('新闻已发布', 'success')
        return redirect(url_for('news.admin_list'))
    return render_template('news_admin_form.html', article=None, categories=NEWS_CATEGORIES, title_text='发布新闻')


@bp.route('/admin/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit(article_id):
    article = NewsArticle.query.get_or_404(article_id)
    if request.method == 'POST':
        article.title = request.form.get('title', '').strip() or article.title
        new_slug = request.form.get('slug', '').strip()
        if new_slug and new_slug != article.slug:
            if not NewsArticle.query.filter(NewsArticle.slug == new_slug, NewsArticle.id != article.id).first():
                article.slug = new_slug
        article.category = request.form.get('category', article.category)
        article.summary = request.form.get('summary', '').strip() or None
        article.content = request.form.get('content', '') or article.content
        article.cover_image = request.form.get('cover_image', '').strip() or None
        article.source = request.form.get('source', '').strip() or None
        article.event_date = request.form.get('event_date', '').strip() or None
        article.is_published = request.form.get('is_published') == '1'
        article.is_pinned = request.form.get('is_pinned') == '1'
        db.session.commit()
        flash('新闻已更新', 'success')
        return redirect(url_for('news.admin_list'))
    return render_template('news_admin_form.html', article=article, categories=NEWS_CATEGORIES, title_text='编辑新闻')


@bp.route('/admin/<int:article_id>/delete', methods=['POST'])
@login_required
def admin_delete(article_id):
    article = NewsArticle.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    flash('新闻已删除', 'success')
    return redirect(url_for('news.admin_list'))
