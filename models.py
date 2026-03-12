from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import re

db = SQLAlchemy()


class AdminUser(db.Model):
    """管理员账户"""
    __tablename__ = 'admin_user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    must_change_password = db.Column(db.Boolean, default=True)
    create_time = db.Column(db.DateTime, default=datetime.now)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)


def _slugify(text):
    """简单 slug：保留中英文数字，空格和标点转连字符"""
    s = re.sub(r'[^\w\u4e00-\u9fff]+', '-', text.strip())
    return s.strip('-').lower() or str(int(datetime.now().timestamp()))


class GenealogyMain(db.Model):
    """族谱主表"""
    __tablename__ = 'genealogy_main'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    surname = db.Column(db.String(20), nullable=False, index=True)
    genealogy_name = db.Column(db.String(200), nullable=False)
    region = db.Column(db.String(100), nullable=True, index=True)
    period = db.Column(db.String(100), nullable=True)
    volumes = db.Column(db.String(50), nullable=True)
    hall_name = db.Column(db.String(100), nullable=True)
    source_url = db.Column(db.String(500), nullable=True)
    founder_info = db.Column(db.Text, nullable=True)
    collection_info = db.Column(db.Text, nullable=True)
    scattered_region = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.now)

    members = db.relationship(
        'FamilyMember', backref='genealogy',
        cascade='all, delete-orphan', lazy='dynamic',
    )
    generations = db.relationship(
        'GenealogyGeneration', backref='genealogy',
        cascade='all, delete-orphan',
        order_by='GenealogyGeneration.sort_order',
    )


class GenealogyGeneration(db.Model):
    """字辈表"""
    __tablename__ = 'genealogy_generation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genealogy_id = db.Column(db.Integer, db.ForeignKey('genealogy_main.id'), nullable=False, index=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    character = db.Column(db.String(10), nullable=False)
    note = db.Column(db.String(100), nullable=True)


class FamilyMember(db.Model):
    """家族成员表"""
    __tablename__ = 'family_member'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genealogy_id = db.Column(db.Integer, db.ForeignKey('genealogy_main.id'), nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(1), nullable=False, default='M')
    generation_number = db.Column(db.Integer, nullable=True)
    courtesy_name = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.String(30), nullable=True)
    death_date = db.Column(db.String(30), nullable=True)
    birth_place = db.Column(db.String(100), nullable=True)
    father_id = db.Column(db.Integer, db.ForeignKey('family_member.id'), nullable=True)
    mother_id = db.Column(db.Integer, db.ForeignKey('family_member.id'), nullable=True)
    spouse_name = db.Column(db.String(50), nullable=True)
    photo = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    path = db.Column(db.String(2000), nullable=True, index=True)

    father = db.relationship('FamilyMember', foreign_keys=[father_id], remote_side=[id], lazy='joined')
    mother = db.relationship('FamilyMember', foreign_keys=[mother_id], remote_side=[id], lazy='joined')

    def get_children(self):
        return FamilyMember.query.filter(
            (FamilyMember.father_id == self.id) | (FamilyMember.mother_id == self.id)
        ).order_by(FamilyMember.generation_number, FamilyMember.id).all()

    def get_siblings(self):
        ids = set()
        if self.father_id:
            for c in FamilyMember.query.filter(FamilyMember.father_id == self.father_id).all():
                if c.id != self.id:
                    ids.add(c.id)
        if self.mother_id:
            for c in FamilyMember.query.filter(FamilyMember.mother_id == self.mother_id).all():
                if c.id != self.id:
                    ids.add(c.id)
        return FamilyMember.query.filter(FamilyMember.id.in_(ids)).all() if ids else []

    @staticmethod
    def rebuild_paths(genealogy_id):
        """重建指定族谱内所有成员的物化路径（/root_id/.../self_id/）"""
        members = FamilyMember.query.filter_by(genealogy_id=genealogy_id).all()
        member_map = {m.id: m for m in members}

        computed = {}

        def _compute(mid):
            if mid in computed:
                return computed[mid]
            m = member_map.get(mid)
            if not m:
                return ''
            if m.father_id and m.father_id in member_map:
                parent_path = _compute(m.father_id)
                result = f'{parent_path}{mid}/'
            else:
                result = f'/{mid}/'
            computed[mid] = result
            return result

        for m in members:
            m.path = _compute(m.id)
        db.session.commit()

    def get_ancestor_ids(self):
        """从 path 中解析出祖先 id 列表（从根到自身）"""
        if not self.path:
            return [self.id]
        return [int(x) for x in self.path.strip('/').split('/') if x]


# ---------- 亲缘关系计算 ----------

_ANCESTOR_M = ['自己', '父亲', '祖父', '曾祖父', '高祖父',
               '天祖父', '烈祖父', '太祖父', '远祖父', '鼻祖']
_ANCESTOR_F = ['自己', '母亲', '祖母', '曾祖母', '高祖母',
               '天祖母', '烈祖母', '太祖母', '远祖母', '鼻祖母']
_DESC_M = ['自己', '儿子', '孙子', '曾孙', '玄孙',
           '来孙', '晜孙', '仍孙', '云孙', '耳孙']
_DESC_F = ['自己', '女儿', '孙女', '曾孙女', '玄孙女',
           '来孙女', '晜孙女', '仍孙女', '云孙女', '耳孙女']
_SIBLING_RANK = {
    1: '亲',
    2: '堂',
    3: '族',
}


def _gen_label(labels, n):
    if n < len(labels):
        return labels[n]
    return f'{n}世' + ('祖' if labels is _ANCESTOR_M or labels is _ANCESTOR_F else '孙')


def find_relationship(member_a, member_b):
    """
    计算两人的亲缘关系。
    返回 dict: relation(文字描述), lca(共同祖先), path_a_members, path_b_members, up_a, up_b
    如果无关系返回 None。
    """
    if member_a.id == member_b.id:
        return {'relation': '同一人', 'up_a': 0, 'up_b': 0}

    if member_a.genealogy_id != member_b.genealogy_id:
        return None

    if not member_a.path or not member_b.path:
        FamilyMember.rebuild_paths(member_a.genealogy_id)
        db.session.refresh(member_a)
        db.session.refresh(member_b)

    ids_a = member_a.get_ancestor_ids()
    ids_b = member_b.get_ancestor_ids()

    lca_idx = -1
    for i in range(min(len(ids_a), len(ids_b))):
        if ids_a[i] == ids_b[i]:
            lca_idx = i
        else:
            break

    if lca_idx == -1:
        return None

    lca_id = ids_a[lca_idx]
    up_a = len(ids_a) - 1 - lca_idx
    up_b = len(ids_b) - 1 - lca_idx

    lca = FamilyMember.query.get(lca_id)

    chain_a_ids = ids_a[lca_idx:]
    chain_b_ids = ids_b[lca_idx + 1:]
    chain_a = [FamilyMember.query.get(i) for i in chain_a_ids]
    chain_b = [FamilyMember.query.get(i) for i in chain_b_ids]

    gender_b = member_b.gender or 'M'

    if up_b == 0:
        labels = _ANCESTOR_M if gender_b == 'M' else _ANCESTOR_F
        rel = f'{member_b.name} 是 {member_a.name} 的 {_gen_label(labels, up_a)}'
    elif up_a == 0:
        labels = _DESC_M if gender_b == 'M' else _DESC_F
        rel = f'{member_b.name} 是 {member_a.name} 的 {_gen_label(labels, up_b)}'
    elif up_a == up_b:
        rank = _SIBLING_RANK.get(up_a, '远房')
        if up_a == 1:
            sib = '兄弟' if gender_b == 'M' else '姐妹'
        else:
            sib = '兄弟' if gender_b == 'M' else '姐妹'
        rel = f'{member_a.name} 与 {member_b.name} 是{rank}{sib}（共同祖先：{lca.name}）'
    else:
        gen_diff = abs(up_a - up_b)
        if up_a > up_b:
            rel = f'{member_b.name} 比 {member_a.name} 高 {gen_diff} 辈（共同祖先：{lca.name}）'
        else:
            rel = f'{member_a.name} 比 {member_b.name} 高 {gen_diff} 辈（共同祖先：{lca.name}）'

    return {
        'relation': rel,
        'lca': lca,
        'up_a': up_a,
        'up_b': up_b,
        'chain_a': chain_a,
        'chain_b': chain_b,
    }


# ---------- 百科词条 ----------
WIKI_CATEGORIES = [
    ('celebrity', '名人'),
    ('hall', '堂号'),
    ('origin', '姓氏起源'),
    ('custom', '宗族礼俗'),
    ('relic', '遗迹文物'),
    ('other', '其他'),
]
WIKI_CAT_MAP = dict(WIKI_CATEGORIES)


class WikiEntry(db.Model):
    """百科词条"""
    __tablename__ = 'wiki_entry'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True, index=True)
    category = db.Column(db.String(30), nullable=False, default='other', index=True)
    summary = db.Column(db.String(500), nullable=True)
    content = db.Column(db.Text, nullable=False)
    cover_image = db.Column(db.String(500), nullable=True)
    era = db.Column(db.String(50), nullable=True)
    is_published = db.Column(db.Boolean, default=True, index=True)
    sort_order = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def category_label(self):
        return WIKI_CAT_MAP.get(self.category, self.category)


# ---------- 新闻动态 ----------
NEWS_CATEGORIES = [
    ('event', '宗亲活动'),
    ('history', '历史事件'),
    ('culture', '文化研究'),
    ('notice', '平台公告'),
    ('other', '其他'),
]
NEWS_CAT_MAP = dict(NEWS_CATEGORIES)


class NewsArticle(db.Model):
    """新闻动态"""
    __tablename__ = 'news_article'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), nullable=False, unique=True, index=True)
    category = db.Column(db.String(30), nullable=False, default='other', index=True)
    summary = db.Column(db.String(500), nullable=True)
    content = db.Column(db.Text, nullable=False)
    cover_image = db.Column(db.String(500), nullable=True)
    source = db.Column(db.String(200), nullable=True)
    event_date = db.Column(db.String(30), nullable=True)
    is_published = db.Column(db.Boolean, default=True, index=True)
    is_pinned = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def category_label(self):
        return NEWS_CAT_MAP.get(self.category, self.category)
