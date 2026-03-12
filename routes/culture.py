# 屈氏文化展示（参考 ly-web 屈氏文化研究会内容）
from flask import Blueprint, render_template, request, jsonify
from models import db, GenealogyMain, GenealogyGeneration, FamilyMember, find_relationship

bp = Blueprint('culture', __name__, url_prefix='/culture')


@bp.route('/')
def index():
    """屈氏文化：起源、郡望堂号、关于我们"""
    return render_template('qu_culture.html')


@bp.route('/zibei')
def zibei():
    """字辈查询：按辈字搜索所属族谱"""
    keyword = request.args.get('q', '').strip()
    results = []
    all_genealogies = []

    genealogies = GenealogyMain.query.order_by(
        GenealogyMain.surname, GenealogyMain.region
    ).all()

    for g in genealogies:
        gens = GenealogyGeneration.query.filter_by(genealogy_id=g.id).order_by(
            GenealogyGeneration.sort_order
        ).all()
        if not gens:
            continue
        chars = ''.join(gen.character for gen in gens)
        entry = {
            'genealogy': g,
            'generations': gens,
            'chars_str': chars,
        }
        all_genealogies.append(entry)
        if keyword and keyword in chars:
            matched_positions = []
            for gen in gens:
                if keyword in gen.character:
                    matched_positions.append(gen.sort_order + 1)
            entry['matched_positions'] = matched_positions
            results.append(entry)

    return render_template(
        'zibei_search.html',
        keyword=keyword,
        results=results,
        all_genealogies=all_genealogies,
    )


@bp.route('/contact')
def contact():
    """联系我们"""
    return render_template('contact.html')


# ---------- 亲缘关系查询 ----------

@bp.route('/relationship', methods=['GET', 'POST'])
def relationship():
    """亲缘关系查询"""
    genealogies = GenealogyMain.query.order_by(
        GenealogyMain.surname, GenealogyMain.genealogy_name
    ).all()

    result = None
    form = {
        'genealogy_id': request.form.get('genealogy_id', type=int) or request.args.get('genealogy_id', type=int),
        'name_a': (request.form.get('name_a') or '').strip(),
        'name_b': (request.form.get('name_b') or '').strip(),
        'id_a': request.form.get('id_a', type=int),
        'id_b': request.form.get('id_b', type=int),
    }

    if request.method == 'POST' and form['genealogy_id'] and form['name_a'] and form['name_b']:
        gid = form['genealogy_id']

        if form['id_a']:
            member_a = FamilyMember.query.filter_by(id=form['id_a'], genealogy_id=gid).first()
        else:
            member_a = FamilyMember.query.filter_by(name=form['name_a'], genealogy_id=gid).first()

        if form['id_b']:
            member_b = FamilyMember.query.filter_by(id=form['id_b'], genealogy_id=gid).first()
        else:
            member_b = FamilyMember.query.filter_by(name=form['name_b'], genealogy_id=gid).first()

        members_a = FamilyMember.query.filter_by(name=form['name_a'], genealogy_id=gid).all()
        members_b = FamilyMember.query.filter_by(name=form['name_b'], genealogy_id=gid).all()

        if not members_a:
            result = {'error': f'未找到成员「{form["name_a"]}」'}
        elif not members_b:
            result = {'error': f'未找到成员「{form["name_b"]}」'}
        elif (len(members_a) > 1 and not form['id_a']) or (len(members_b) > 1 and not form['id_b']):
            result = {
                'disambiguate': True,
                'members_a': members_a if len(members_a) > 1 and not form['id_a'] else None,
                'members_b': members_b if len(members_b) > 1 and not form['id_b'] else None,
                'selected_a': member_a,
                'selected_b': member_b,
            }
        else:
            if not member_a:
                member_a = members_a[0]
            if not member_b:
                member_b = members_b[0]
            rel = find_relationship(member_a, member_b)
            if rel:
                result = {**rel, 'member_a': member_a, 'member_b': member_b}
            else:
                result = {
                    'error': f'在此族谱中未找到「{member_a.name}」与「{member_b.name}」之间的亲缘关系',
                    'member_a': member_a,
                    'member_b': member_b,
                }

    return render_template(
        'relationship.html',
        genealogies=genealogies,
        result=result,
        form=form,
    )


@bp.route('/api/members')
def api_members():
    """成员名称自动补全 API"""
    gid = request.args.get('genealogy_id', type=int)
    q = request.args.get('q', '').strip()
    if not gid or not q:
        return jsonify([])
    members = FamilyMember.query.filter(
        FamilyMember.genealogy_id == gid,
        FamilyMember.name.contains(q),
    ).limit(20).all()
    seen = {}
    for m in members:
        key = m.name
        if key not in seen:
            seen[key] = []
        seen[key].append({
            'id': m.id,
            'name': m.name,
            'generation': m.generation_number,
            'birth_date': m.birth_date or '',
            'father': m.father.name if m.father else '',
        })
    results = []
    for name, items in seen.items():
        if len(items) == 1:
            results.append(items[0])
        else:
            for item in items:
                item['display'] = f"{item['name']}（第{item['generation'] or '?'}世" \
                                  + (f"，父：{item['father']}" if item['father'] else '') + '）'
                results.append(item)
    return jsonify(results)
