from app import app, db, HealthWorker
from werkzeug.security import generate_password_hash

# Create all tables
with app.app_context():
    db.create_all()
    
    # Check if admin user already exists
    admin_user = HealthWorker.query.filter_by(email='kenlizcareconnect@gmail.com').first()
    
    if not admin_user:
        # Create default admin user
        admin_user = HealthWorker(
            name='Admin',
            email='kenlizcareconnect@gmail.com',
            phone='',
            address='',
            qualifications='',
            experience='',
            specializations='',
            availability='',
            worker_type='admin',
            status='',
            id_number='',
            cv='',
            certifications='',
            photo='',
            location='',
            password_hash=generate_password_hash('kenlizcareconnect24$#')
        )
        db.session.add(admin_user)
        db.session.commit()

    print("Database created successfully!")
