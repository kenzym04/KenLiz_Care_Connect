from flask_sqlalchemy import SQLAlchemy
from datetime import UTC, datetime
from flask_migrate import Migrate

db = SQLAlchemy()

class HealthWorker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    qualifications = db.Column(db.Text, nullable=False)
    experience = db.Column(db.Text, nullable=False)
    specializations = db.Column(db.Text, nullable=True)
    availability = db.Column(db.String(20), nullable=False, default='Unavailable')
    worker_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    id_number = db.Column(db.String(100), nullable=False)
    cv = db.Column(db.String(100), nullable=False)
    certifications = db.Column(db.String(200), nullable=True)
    photo = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    assigned_facility_id = db.Column(db.Integer, db.ForeignKey('facility.id'), nullable=True)
    assigned_facility = db.relationship('Facility', foreign_keys=[assigned_facility_id], backref=db.backref('assigned_workers', lazy=True))

class Facility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    health_workers = db.relationship('HealthWorker', backref='facility', lazy=True)
    
    def is_facility(self):
        return True  # You would implement your own logic here based on your requirements

# Initialize Flask-Migrate
migrate = Migrate()

# This function will initialize Flask app with SQLAlchemy and Flask-Migrate
def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)
