# 屈氏文化展示（参考 ly-web 屈氏文化研究会内容）
from flask import Blueprint, render_template, request
from models import db, GenealogyMain, GenealogyGeneration

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
