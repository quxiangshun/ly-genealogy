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
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def category_label(self):
        return NEWS_CAT_MAP.get(self.category, self.category)
