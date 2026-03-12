# 族谱管理路由（列表/详情公开；新增编辑删除字辈需登录）
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, GenealogyMain, GenealogyGeneration, FamilyMember
from utils.auth import login_required

bp = Blueprint('genealogy', __name__, url_prefix='/genealogy')


def _member_counts(genealogy_ids):
    """返回族谱 id -> 成员数的字典"""
    if not genealogy_ids:
        return {}
    from sqlalchemy import func
    q = db.session.query(FamilyMember.genealogy_id, func.count(FamilyMember.id)).filter(
        FamilyMember.genealogy_id.in_(genealogy_ids)
    ).group_by(FamilyMember.genealogy_id)
    return dict(q.all())


@bp.route('/')
def list_genealogies():
    """族谱库列表，支持按姓氏、地区、年代筛选"""
    surname = request.args.get('surname', '').strip()
    region = request.args.get('region', '').strip()
    period = request.args.get('period', '').strip()
    query = GenealogyMain.query.order_by(GenealogyMain.surname, GenealogyMain.region, GenealogyMain.genealogy_name)
    if surname:
        query = query.filter(GenealogyMain.surname == surname)
    if region:
        query = query.filter(GenealogyMain.region.ilike(f'%{region}%'))
    if period:
        query = query.filter(GenealogyMain.period.ilike(f'%{period}%'))
    genealogies = query.all()
    member_counts = _member_counts([g.id for g in genealogies])
    # 筛选项：所有出现过的姓氏、地区（去重排序）
    all_surnames = db.session.query(GenealogyMain.surname).distinct().order_by(GenealogyMain.surname).all()
    all_regions = db.session.query(GenealogyMain.region).distinct().filter(
        GenealogyMain.region.isnot(None), GenealogyMain.region != ''
    ).order_by(GenealogyMain.region).all()
    return render_template(
        'genealogy_list.html',
        genealogies=genealogies,
        member_counts=member_counts,
        filter_surname=surname,
        filter_region=region,
        filter_period=period,
        all_surnames=[s[0] for s in all_surnames],
        all_regions=[r[0] for r in all_regions],
    )


@bp.route('/<int:genealogy_id>')
def detail(genealogy_id):
    """族谱详情"""
    genealogy = GenealogyMain.query.get_or_404(genealogy_id)
    member_count = genealogy.members.count()
    gen_count = len(genealogy.generations) if genealogy.generations else 0
    return render_template(
        'genealogy_detail.html',
        genealogy=genealogy,
        member_count=member_count,
        gen_count=gen_count,
    )


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """新增族谱"""
    if request.method == 'POST':
        surname = request.form.get('surname', '').strip()
        genealogy_name = request.form.get('genealogy_name', '').strip()
        description = request.form.get('description', '').strip()
        region = request.form.get('region', '').strip() or None
        period = request.form.get('period', '').strip() or None
        volumes = request.form.get('volumes', '').strip() or None
        hall_name = request.form.get('hall_name', '').strip() or None
        source_url = request.form.get('source_url', '').strip() or None
        founder_info = request.form.get('founder_info', '').strip() or None
        collection_info = request.form.get('collection_info', '').strip() or None
        scattered_region = request.form.get('scattered_region', '').strip() or None
        if not surname or not genealogy_name:
            flash('姓氏和族谱名称为必填项', 'danger')
            return render_template('genealogy_form.html', title='新增族谱', genealogy=None)
        g = GenealogyMain(
            surname=surname,
            genealogy_name=genealogy_name,
            description=description or None,
            region=region,
            period=period,
            volumes=volumes,
            hall_name=hall_name,
            source_url=source_url,
            founder_info=founder_info,
            collection_info=collection_info,
            scattered_region=scattered_region,
        )
        db.session.add(g)
        db.session.commit()
        flash('族谱创建成功', 'success')
        return redirect(url_for('genealogy.detail', genealogy_id=g.id))
    return render_template('genealogy_form.html', title='新增族谱', genealogy=None)


@bp.route('/<int:genealogy_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(genealogy_id):
    """编辑族谱"""
    genealogy = GenealogyMain.query.get_or_404(genealogy_id)
    if request.method == 'POST':
        genealogy.genealogy_name = request.form.get('genealogy_name', '').strip() or genealogy.genealogy_name
        genealogy.description = request.form.get('description', '').strip() or None
        genealogy.region = request.form.get('region', '').strip() or None
        genealogy.period = request.form.get('period', '').strip() or None
        genealogy.volumes = request.form.get('volumes', '').strip() or None
        genealogy.hall_name = request.form.get('hall_name', '').strip() or None
        genealogy.source_url = request.form.get('source_url', '').strip() or None
        genealogy.founder_info = request.form.get('founder_info', '').strip() or None
        genealogy.collection_info = request.form.get('collection_info', '').strip() or None
        genealogy.scattered_region = request.form.get('scattered_region', '').strip() or None
        db.session.commit()
        flash('族谱已更新', 'success')
        return redirect(url_for('genealogy.detail', genealogy_id=genealogy_id))
    return render_template('genealogy_form.html', title='编辑族谱', genealogy=genealogy)


@bp.route('/<int:genealogy_id>/generations', methods=['GET', 'POST'])
@login_required
def generations(genealogy_id):
    """字辈表：查看与编辑"""
    genealogy = GenealogyMain.query.get_or_404(genealogy_id)
    if request.method == 'POST':
        # 提交字辈：按行解析，每行一字或“序号 字”或“字 备注”
        raw = request.form.get('generations_text', '').strip()
        # 先删除原有
        GenealogyGeneration.query.filter(GenealogyGeneration.genealogy_id == genealogy_id).delete()
        if raw:
            for i, line in enumerate(raw.splitlines()):
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                char = parts[0] if parts else line[:1]
                if not char:
                    continue
                note = parts[1] if len(parts) > 1 else None
                gen = GenealogyGeneration(
                    genealogy_id=genealogy_id,
                    sort_order=i,
                    character=char[:10],
                    note=note[:50] if note else None,
                )
                db.session.add(gen)
        db.session.commit()
        flash('字辈表已保存', 'success')
        return redirect(url_for('genealogy.generations', genealogy_id=genealogy_id))
    gens = genealogy.generations or []
    return render_template('genealogy_generations.html', genealogy=genealogy, generations=gens)


@bp.route('/<int:genealogy_id>/delete', methods=['POST'])
@login_required
def delete(genealogy_id):
    """删除族谱（级联删除该族谱下所有成员）"""
    genealogy = GenealogyMain.query.get_or_404(genealogy_id)
    db.session.delete(genealogy)
    db.session.commit()
    flash('族谱已删除', 'success')
    return redirect(url_for('genealogy.list_genealogies'))
