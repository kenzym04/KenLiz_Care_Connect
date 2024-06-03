from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from . import db, HealthWorker, Facility

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kenlizcareconnect.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register-healthworker', methods=['GET', 'POST'])
def register_healthworker():
    if request.method == 'POST':
        # Handle form submission
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        qualifications = request.form['qualifications']
        experience = request.form['experience']
        specializations = request.form['specializations']
        availability = request.form['availability']
        worker_type = request.form['worker_type']
        status = request.form['status']
        id_number = request.form['id_number']
        cv = request.form['cv']
        certifications = request.form['certifications']
        photo = request.form['photo']
        
        new_worker = HealthWorker(
            name=name, email=email, phone=phone, address=address, qualifications=qualifications,
            experience=experience, specializations=specializations, availability=availability,
            worker_type=worker_type, status=status, id_number=id_number, cv=cv, certifications=certifications,
            photo=photo)
        
        try:
            db.session.add(new_worker)
            db.session.commit()
            return redirect(url_for('home'))
        except:
            return 'There was an issue adding the health worker'
    
    return render_template('register_healthworker.html')

@app.route('/register-facility', methods=['GET', 'POST'])
def register_facility():
    if request.method == 'POST':
        # Handle form submission
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        
        new_facility = Facility(name=name, email=email, phone=phone, address=address)
        
        try:
            db.session.add(new_facility)
            db.session.commit()
            return redirect(url_for('home'))
        except:
            return 'There was an issue adding the facility'
    
    return render_template('register_facility.html')

@app.route('/admin')
def admin_dashboard():
    health_workers = HealthWorker.query.all()
    facilities = Facility.query.all()
    return render_template('admin_dashboard.html', health_workers=health_workers, facilities=facilities)

if __name__ == '__main__':
    app.run(debug=True)
