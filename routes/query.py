# 查询展示路由（成员、树形需登录）
from flask import Blueprint, render_template, request
from models import FamilyMember, GenealogyMain
from utils.auth import login_required

bp = Blueprint('query', __name__, url_prefix='/query')


@bp.route('/member', methods=['GET', 'POST'])
@login_required
def query_member():
    """按姓名查询成员"""
    results = []
    if request.method == 'POST':
        name = request.form.get('name', '')
        genealogy_id = request.form.get('genealogy_id', '')

        query = FamilyMember.query
        if name:
            query = query.filter(FamilyMember.name.like(f'%{name}%'))
        if genealogy_id and genealogy_id.isdigit():
            query = query.filter(FamilyMember.genealogy_id == int(genealogy_id))

        results = query.all()

    genealogies = GenealogyMain.query.order_by(GenealogyMain.surname, GenealogyMain.genealogy_name).all()
    return render_template('query.html', results=results, genealogies=genealogies)


@bp.route('/member/<int:member_id>')
@login_required
def member_detail(member_id):
    """展示成员完整亲属关系（直系长辈、直系晚辈、平辈）"""
    member = FamilyMember.query.get_or_404(member_id)

    def get_ancestors(person, ancestors=None):
        if ancestors is None:
            ancestors = []
        if person.father:
            ancestors.append(('父亲', person.father))
            get_ancestors(person.father, ancestors)
        if person.mother:
            ancestors.append(('母亲', person.mother))
            get_ancestors(person.mother, ancestors)
        return ancestors

    def get_descendants(person, descendants=None):
        if descendants is None:
            descendants = []
        for child in person.get_children():
            relation = '儿子' if child.gender == 'M' else '女儿'
            descendants.append((relation, child))
            get_descendants(child, descendants)
        return descendants

    ancestors = get_ancestors(member)
    descendants = get_descendants(member)
    siblings = member.get_siblings()

    return render_template(
        'tree_view.html',
        member=member,
        ancestors=ancestors,
        descendants=descendants,
        siblings=siblings,
    )


@bp.route('/tree/<int:genealogy_id>')
@login_required
def tree_view(genealogy_id):
    """族谱全局树形展示"""
    genealogy = GenealogyMain.query.get_or_404(genealogy_id)
    members = FamilyMember.query.filter(FamilyMember.genealogy_id == genealogy_id).all()
    return render_template('genealogy_tree.html', genealogy=genealogy, members=members)
