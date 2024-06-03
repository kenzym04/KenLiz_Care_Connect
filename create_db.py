from app import app, db
from models import HealthWorker, Facility

with app.app_context():
    db.create_all()
    print("Database created successfully!")
