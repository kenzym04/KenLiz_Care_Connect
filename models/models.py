from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, UTC

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
    availability = db.Column(db.String(50), nullable=False)
    worker_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    id_number = db.Column(db.String(20), nullable=False)
    cv = db.Column(db.String(100), nullable=False)
    certifications = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

class Facility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
