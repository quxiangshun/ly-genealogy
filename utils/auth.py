from functools import wraps
from flask import session, redirect, url_for, request, flash


def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login", next=request.url))
        if session.get("must_change_password"):
            flash("请先修改默认密码", "warning")
            return redirect(url_for("change_password"))
        return f(*args, **kwargs)
    return wrapped
