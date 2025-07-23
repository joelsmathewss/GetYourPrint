import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

# --- Base paths ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

# Ensure folders exist
os.makedirs(INSTANCE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Flask App ---
app = Flask(__name__, instance_path=INSTANCE_DIR)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secret-and-secure-key-for-dev')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(INSTANCE_DIR, 'printready.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR

# --- Extensions ---
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# --- Models ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # --- FIX: Made mut_id nullable to allow for staff members ---
    mut_id = db.Column(db.String(50), unique=True, nullable=True) 
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    batch = db.Column(db.String(20), nullable=True)
    jobs = db.relationship('PrintJob', foreign_keys='PrintJob.user_id', backref='author', lazy=True)

class PrintJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    copies = db.Column(db.Integer, nullable=False)
    print_type = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='Queued')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    completed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

# --- User loader ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---
@app.route('/')
def index():
    if current_user.is_authenticated:
        # This logic correctly redirects based on role
        return redirect(url_for(f"{current_user.role}_dashboard"))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email')
        pw = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, pw):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials. Please check your email and password.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('signup-email')
        role = request.form.get('role')
        mut_id = request.form.get('mut-id')

        if User.query.filter_by(email=email).first():
            flash('Email address already registered.', 'warning')
            return redirect(url_for('signup'))
        
        # --- FIX: Check if mut_id is unique only if the user is a student ---
        if role == 'student' and User.query.filter_by(mut_id=mut_id).first():
            flash('MUT ID already registered.', 'warning')
            return redirect(url_for('signup'))

        hashed_pw = generate_password_hash(request.form.get('signup-password'), method='pbkdf2:sha256')
        new_user = User(
            name=request.form.get('name'),
            mut_id=mut_id if role == 'student' else None,
            email=email,
            password_hash=hashed_pw,
            role=role,
            batch=request.form.get('batch') if role == 'student' else None
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

# Other routes (logout, student_dashboard, etc.) remain the same...

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/student')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    jobs = PrintJob.query.filter_by(user_id=current_user.id).order_by(PrintJob.submitted_at.desc()).all()
    return render_template('student.html', jobs=jobs)

@app.route('/submit_job', methods=['POST'])
@login_required
def submit_job():
    if 'file' not in request.files or request.files['file'].filename == '':
        flash('No file selected.', 'warning')
        return redirect(url_for('student_dashboard'))
    
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    new_job = PrintJob(
        user_id=current_user.id,
        filename=filename,
        copies=int(request.form.get('copies')),
        print_type=request.form.get('print-type')
    )
    db.session.add(new_job)
    db.session.commit()
    flash('Job submitted successfully!', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/staff')
@login_required
def staff_dashboard():
    if current_user.role != 'staff':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    active_jobs = PrintJob.query.filter(PrintJob.status != 'Completed').order_by(PrintJob.submitted_at.asc()).all()
    completed_jobs = PrintJob.query.filter_by(status='Completed').order_by(PrintJob.completed_at.desc()).limit(50).all()
    return render_template('staff.html', active_jobs=active_jobs, completed_jobs=completed_jobs, User=User)

@app.route('/update_status/<int:job_id>', methods=['POST'])
@login_required
def update_status(job_id):
    if current_user.role != 'staff':
        return redirect(url_for('index'))
    job = PrintJob.query.get_or_404(job_id)
    job.status = request.form.get('status')
    if job.status == 'Completed':
        job.completed_at = datetime.utcnow()
        job.completed_by_id = current_user.id
    db.session.commit()
    flash(f'Job #{job.id} status updated to {job.status}.', 'success')
    return redirect(url_for('staff_dashboard'))

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    job = PrintJob.query.filter_by(filename=filename).first_or_404()
    if current_user.role == 'staff' or current_user.id == job.user_id:
         return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    flash('You do not have permission to access this file.', 'danger')
    return redirect(url_for('index'))

@app.cli.command("init-db")
def init_db_command():
    """Creates the database tables."""
    db.create_all()
    print("Initialized the database.")

if __name__ == '__main__':
    app.run(debug=True)
