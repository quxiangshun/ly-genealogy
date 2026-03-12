import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from models import db, FamilyMember, GenealogyMain
from utils.auth import login_required

bp = Blueprint('member', __name__, url_prefix='/member')


def _allowed_file(filename):
    if not filename or '.' not in filename:
        return False
    return filename.rsplit('.', 1)[-1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def _save_photo(member, file_storage):
    if not file_storage or not file_storage.filename or not _allowed_file(file_storage.filename):
        return None
    folder = current_app.config.get('UPLOAD_FOLDER')
    if not folder:
        return None
    os.makedirs(folder, exist_ok=True)
    ext = file_storage.filename.rsplit('.', 1)[-1].lower()
    if ext == 'jpeg':
        ext = 'jpg'
    rel = f"uploads/members/{member.id}.{ext}"
    full = os.path.join(current_app.static_folder, rel.replace('/', os.sep))
    try:
        file_storage.save(full)
        return rel
    except Exception:
        return None


def _delete_photo(rel_path):
    if not rel_path:
        return
    try:
        full = os.path.join(current_app.static_folder, rel_path.replace('/', os.sep))
        if os.path.isfile(full):
            os.remove(full)
    except Exception:
        pass


def _form_str(key, default=''):
    return request.form.get(key, default).strip() or None


def _form_int(key):
    v = request.form.get(key, '').strip()
    return int(v) if v else None


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    genealogies = GenealogyMain.query.order_by(GenealogyMain.surname, GenealogyMain.genealogy_name).all()
    if request.method == 'POST':
        genealogy_id = _form_int('genealogy_id')
        name = _form_str('name')
        if not genealogy_id or not name:
            flash('请选择族谱并填写姓名', 'danger')
            return render_template('member_form.html', title='新增成员', genealogies=genealogies, member=None, father_candidates=None, mother_candidates=None)

        father_id = _form_int('father_id')
        mother_id = _form_int('mother_id')
        if father_id:
            f = FamilyMember.query.get(father_id)
            if not f or f.genealogy_id != genealogy_id:
                flash('父亲必须属于同一族谱', 'danger')
                return render_template('member_form.html', title='新增成员', genealogies=genealogies, member=None, father_candidates=None, mother_candidates=None)
        if mother_id:
            m = FamilyMember.query.get(mother_id)
            if not m or m.genealogy_id != genealogy_id:
                flash('母亲必须属于同一族谱', 'danger')
                return render_template('member_form.html', title='新增成员', genealogies=genealogies, member=None, father_candidates=None, mother_candidates=None)

        member = FamilyMember(
            genealogy_id=genealogy_id,
            name=name,
            gender=request.form.get('gender', 'M'),
            generation_number=_form_int('generation_number'),
            courtesy_name=_form_str('courtesy_name'),
            birth_date=_form_str('birth_date'),
            death_date=_form_str('death_date'),
            birth_place=_form_str('birth_place'),
            father_id=father_id,
            mother_id=mother_id,
            spouse_name=_form_str('spouse_name'),
            notes=_form_str('notes'),
        )
        db.session.add(member)
        db.session.commit()

        photo = request.files.get('photo')
        if photo and photo.filename:
            if not _allowed_file(photo.filename):
                flash('照片格式仅支持 png/jpg/gif/webp', 'warning')
            else:
                rel = _save_photo(member, photo)
                if rel:
                    member.photo = rel
                    db.session.commit()

        flash('成员添加成功', 'success')
        return redirect(url_for('member.list_members', genealogy_id=genealogy_id))
    return render_template('member_form.html', title='新增成员', genealogies=genealogies, member=None, father_candidates=None, mother_candidates=None)


@bp.route('/list')
@login_required
def list_members():
    genealogy_id = request.args.get('genealogy_id', type=int)
    q = FamilyMember.query
    if genealogy_id:
        q = q.filter(FamilyMember.genealogy_id == genealogy_id)
    members = q.order_by(FamilyMember.genealogy_id, FamilyMember.generation_number, FamilyMember.id).all()
    genealogies = GenealogyMain.query.order_by(GenealogyMain.surname, GenealogyMain.genealogy_name).all()
    return render_template('member_list.html', members=members, genealogies=genealogies, filter_genealogy_id=genealogy_id)


@bp.route('/<int:member_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(member_id):
    member = FamilyMember.query.get_or_404(member_id)
    genealogies = GenealogyMain.query.order_by(GenealogyMain.surname, GenealogyMain.genealogy_name).all()

    if request.method == 'POST':
        member.name = _form_str('name') or member.name
        member.gender = request.form.get('gender', member.gender)
        member.generation_number = _form_int('generation_number')
        member.courtesy_name = _form_str('courtesy_name')
        member.birth_date = _form_str('birth_date')
        member.death_date = _form_str('death_date')
        member.birth_place = _form_str('birth_place')
        member.spouse_name = _form_str('spouse_name')
        member.notes = _form_str('notes')

        fid = _form_int('father_id')
        mid = _form_int('mother_id')
        if fid and fid == member.id:
            flash('不能将自己设为父亲', 'danger')
        elif fid:
            f = FamilyMember.query.get(fid)
            if not f or f.genealogy_id != member.genealogy_id:
                flash('父亲必须属于同一族谱', 'danger')
                fid = member.father_id
        if mid and mid == member.id:
            flash('不能将自己设为母亲', 'danger')
        elif mid:
            m = FamilyMember.query.get(mid)
            if not m or m.genealogy_id != member.genealogy_id:
                flash('母亲必须属于同一族谱', 'danger')
                mid = member.mother_id
        member.father_id = fid
        member.mother_id = mid

        if request.form.get('remove_photo') == '1' and member.photo:
            _delete_photo(member.photo)
            member.photo = None
        photo = request.files.get('photo')
        if photo and photo.filename:
            if not _allowed_file(photo.filename):
                flash('照片格式仅支持 png/jpg/gif/webp', 'warning')
            else:
                if member.photo:
                    _delete_photo(member.photo)
                rel = _save_photo(member, photo)
                if rel:
                    member.photo = rel

        db.session.commit()
        flash('成员信息已更新', 'success')
        return redirect(url_for('member.list_members', genealogy_id=member.genealogy_id))

    father_candidates = [m for m in member.genealogy.members if m.gender == 'M' and m.id != member.id]
    mother_candidates = [m for m in member.genealogy.members if m.gender == 'F' and m.id != member.id]
    return render_template('member_form.html', title='编辑成员', genealogies=genealogies, member=member, father_candidates=father_candidates, mother_candidates=mother_candidates)


@bp.route('/<int:member_id>/delete', methods=['POST'])
@login_required
def delete(member_id):
    member = FamilyMember.query.get_or_404(member_id)
    gid = member.genealogy_id
    if member.photo:
        _delete_photo(member.photo)
    children = member.get_children()
    for c in children:
        if c.father_id == member.id:
            c.father_id = None
        if c.mother_id == member.id:
            c.mother_id = None
    db.session.delete(member)
    db.session.commit()
    flash('成员已删除' + ('；子女父母信息已置空' if children else ''), 'success')
    return redirect(url_for('member.list_members', genealogy_id=gid))
