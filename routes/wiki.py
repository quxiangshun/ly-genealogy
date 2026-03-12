from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, WikiEntry, WIKI_CATEGORIES, WIKI_CAT_MAP, _slugify
from utils.auth import login_required

bp = Blueprint('wiki', __name__, url_prefix='/wiki')


@bp.route('/')
def index():
    """百科首页：分类浏览 + 搜索"""
    cat = request.args.get('cat', '')
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    query = WikiEntry.query.filter_by(is_published=True)
    if cat and cat in WIKI_CAT_MAP:
        query = query.filter_by(category=cat)
    if q:
        query = query.filter(
            db.or_(WikiEntry.title.contains(q), WikiEntry.summary.contains(q))
        )
    entries = query.order_by(
        WikiEntry.sort_order.desc(), WikiEntry.create_time.desc()
    ).paginate(page=page, per_page=12, error_out=False)

    cat_counts = {}
    for code, _ in WIKI_CATEGORIES:
        cat_counts[code] = WikiEntry.query.filter_by(is_published=True, category=code).count()

    return render_template(
        'wiki_index.html',
        entries=entries, cat=cat, q=q,
        categories=WIKI_CATEGORIES, cat_counts=cat_counts,
    )


@bp.route('/<slug>')
def detail(slug):
    """百科词条详情"""
    entry = WikiEntry.query.filter_by(slug=slug, is_published=True).first_or_404()
    related = WikiEntry.query.filter(
        WikiEntry.category == entry.category,
        WikiEntry.id != entry.id,
        WikiEntry.is_published == True,
    ).order_by(WikiEntry.sort_order.desc()).limit(6).all()
    return render_template('wiki_detail.html', entry=entry, related=related)


# ========== 后台管理 ==========

@bp.route('/admin')
@login_required
def admin_list():
    page = request.args.get('page', 1, type=int)
    entries = WikiEntry.query.order_by(
        WikiEntry.create_time.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    return render_template('wiki_admin_list.html', entries=entries, categories=WIKI_CATEGORIES)


@bp.route('/admin/add', methods=['GET', 'POST'])
@login_required
def admin_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('标题不能为空', 'danger')
            return render_template('wiki_admin_form.html', entry=None, categories=WIKI_CATEGORIES, title_text='新增百科词条')
        slug = request.form.get('slug', '').strip() or _slugify(title)
        if WikiEntry.query.filter_by(slug=slug).first():
            slug = slug + '-' + str(int(__import__('time').time()))
        entry = WikiEntry(
            title=title, slug=slug,
            category=request.form.get('category', 'other'),
            summary=request.form.get('summary', '').strip() or None,
            content=request.form.get('content', ''),
            cover_image=request.form.get('cover_image', '').strip() or None,
            era=request.form.get('era', '').strip() or None,
            is_published=request.form.get('is_published') == '1',
            sort_order=int(request.form.get('sort_order', 0) or 0),
        )
        db.session.add(entry)
        db.session.commit()
        flash('百科词条已添加', 'success')
        return redirect(url_for('wiki.admin_list'))
    return render_template('wiki_admin_form.html', entry=None, categories=WIKI_CATEGORIES, title_text='新增百科词条')


@bp.route('/admin/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit(entry_id):
    entry = WikiEntry.query.get_or_404(entry_id)
    if request.method == 'POST':
        entry.title = request.form.get('title', '').strip() or entry.title
        new_slug = request.form.get('slug', '').strip()
        if new_slug and new_slug != entry.slug:
            if not WikiEntry.query.filter(WikiEntry.slug == new_slug, WikiEntry.id != entry.id).first():
                entry.slug = new_slug
        entry.category = request.form.get('category', entry.category)
        entry.summary = request.form.get('summary', '').strip() or None
        entry.content = request.form.get('content', '') or entry.content
        entry.cover_image = request.form.get('cover_image', '').strip() or None
        entry.era = request.form.get('era', '').strip() or None
        entry.is_published = request.form.get('is_published') == '1'
        entry.sort_order = int(request.form.get('sort_order', 0) or 0)
        db.session.commit()
        flash('百科词条已更新', 'success')
        return redirect(url_for('wiki.admin_list'))
    return render_template('wiki_admin_form.html', entry=entry, categories=WIKI_CATEGORIES, title_text='编辑百科词条')


@bp.route('/admin/<int:entry_id>/delete', methods=['POST'])
@login_required
def admin_delete(entry_id):
    entry = WikiEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('百科词条已删除', 'success')
    return redirect(url_for('wiki.admin_list'))
