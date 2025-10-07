import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from app import db
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    is_staff = db.Column(db.Boolean, default=False)
    print_jobs = db.relationship('PrintJob', backref='uploader', lazy=True)
class PrintJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    original_filename = db.Column(db.String(200))
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pages = db.Column(db.Integer)
    copies = db.Column(db.Integer)
    color = db.Column(db.Boolean)
    cost = db.Column(db.Integer)
    status = db.Column(db.String(50), default='Queued')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)