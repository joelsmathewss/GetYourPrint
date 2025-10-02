import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

from app import db, login_manager
from models import User, PrintJob

bp = Blueprint('routes', __name__)

@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))

# --- Routes ---
@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email, password, role = request.form['email'], request.form['password'], request.form.get('role')
        if User.query.filter_by(email=email).first():
            flash("Email exists")
            return redirect(url_for('routes.signup'))
        u = User(email=email, password=generate_password_hash(password), is_staff=(role=="staff"))
        db.session.add(u)
        db.session.commit()
        flash("Account created")
        return redirect(url_for('routes.login'))
    return render_template('signup.html')

@bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(email=request.form['email']).first()
        if u and check_password_hash(u.password, request.form['password']):
            login_user(u)
            return redirect(url_for('routes.staff_dashboard' if u.is_staff else 'routes.student_dashboard'))
        flash("Invalid")
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

@bp.route('/student', methods=['GET','POST'])
@login_required
def student_dashboard():
    if current_user.is_staff:
        return redirect(url_for('routes.staff_dashboard'))
    if request.method == 'POST':
        f = request.files['file']
        fname = secure_filename(f.filename)
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], fname)   
        f.save(path)
        pages = len(PdfReader(path).pages)
        copies = int(request.form['copies'])
        color = (request.form['color'] == "color")
        cost = pages * copies * (5 if color else 2)
        job = PrintJob(filename=fname, original_filename=f.filename,
                       uploader_id=current_user.id, pages=pages, copies=copies, color=color, cost=cost)
        db.session.add(job)
        db.session.commit()
        flash(f"Uploaded. Cost: ₹{cost}")
    jobs = PrintJob.query.filter_by(uploader_id=current_user.id).all()
    return render_template('student_dashboard.html', jobs=jobs)

@bp.route('/staff')
@login_required
def staff_dashboard():
    if not current_user.is_staff:
        return redirect(url_for('routes.student_dashboard'))
    jobs = PrintJob.query.all()
    return render_template('staff_dashboard.html', jobs=jobs)

@bp.route('/download/<int:jid>')
@login_required
def download(jid):
    if not current_user.is_staff:
        return "Forbidden", 403
    job = PrintJob.query.get(jid)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], job.filename, as_attachment=True)  # ✅ FIXED

@bp.route('/update/<int:jid>/<status>')
@login_required
def update(jid, status):
    if not current_user.is_staff:
        return "Forbidden", 403
    job = PrintJob.query.get(jid)
    job.status = status
    db.session.commit()
    return redirect(url_for('routes.staff_dashboard'))
