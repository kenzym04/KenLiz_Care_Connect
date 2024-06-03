from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kenliz_careconnect.db'
app.config['SECRET_KEY'] = 'kenzym04'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'kenlizcareconnect@gmail.com'
app.config['MAIL_PASSWORD'] = 'kenlizcareconnect24'

db = SQLAlchemy(app)
mail = Mail(app)

# Import models after initializing db to avoid circular import
from models import HealthWorker, Facility

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register-healthworker', methods=['GET', 'POST'])
def register_healthworker():
    if request.method == 'POST':
        new_healthworker = HealthWorker(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address'],
            qualifications=request.form['qualifications'],
            experience=request.form['experience'],
            specializations=request.form['specializations'],
            availability='Available',
            worker_type=request.form['worker_type'],
            status='Pending',
            id_number=request.form['id_number'],
            cv=request.form['cv'],
            certifications=request.form['certifications'],
            photo=request.form['photo'],
            location=request.form['location']
        )
        db.session.add(new_healthworker)
        db.session.commit()
        flash('Registration successful! Please wait for admin approval.')
        return redirect(url_for('index'))
    return render_template('register_healthworker.html')

@app.route('/register-facility', methods=['GET', 'POST'])
def register_facility():
    if request.method == 'POST':
        new_facility = Facility(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address'],
            location=request.form['location']
        )
        db.session.add(new_facility)
        db.session.commit()
        flash('Registration successful! Please wait for admin approval.')
        return redirect(url_for('index'))
    return render_template('register_facility.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    location = request.args.get('location')
    worker_type = request.args.get('worker_type')
    facility_location = request.args.get('facility_location')

    healthworkers = HealthWorker.query
    facilities = Facility.query

    if location:
        healthworkers = healthworkers.filter(HealthWorker.location.ilike(f'%{location}%'))
    if worker_type:
        healthworkers = healthworkers.filter_by(worker_type=worker_type)
    if facility_location:
        facilities = facilities.filter(Facility.location.ilike(f'%{facility_location}%'))

    healthworkers = healthworkers.all()
    facilities = facilities.all()

    return render_template('admin_dashboard.html', healthworkers=healthworkers, facilities=facilities)

@app.route('/healthworker-update/<int:id>', methods=['GET', 'POST'])
def healthworker_update(id):
    healthworker = HealthWorker.query.get_or_404(id)
    if request.method == 'POST':
        healthworker.availability = request.form['availability']
        db.session.commit()
        flash('Availability updated successfully.')
        return redirect(url_for('admin_dashboard'))
    return render_template('healthworker_update.html', healthworker=healthworker)

@app.route('/create-invoice/<int:application_id>', methods=['GET', 'POST'])
def create_invoice(application_id):
    if request.method == 'POST':
        client_email = request.form['email']
        service_details = request.form['services']
        total_amount = request.form['amount']
        invoice = f"Invoice Details:\nService: {service_details}\nTotal Amount: {total_amount}"
        
        msg = Message('Invoice from KenLiz CareConnect', sender='your_email@example.com', recipients=[client_email])
        msg.body = invoice
        mail.send(msg)

        flash('Invoice sent successfully.')
        return redirect(url_for('admin_dashboard'))
    return render_template('invoice.html', application_id=application_id)

@app.route('/service-application', methods=['GET', 'POST'])
def service_application():
    if request.method == 'POST':
        # Handle service application form
        pass
    return render_template('service_application.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/delete_healthworker/<int:id>', methods=['POST'])
def delete_healthworker(id):
    healthworker = HealthWorker.query.get_or_404(id)
    db.session.delete(healthworker)
    db.session.commit()
    flash('Health worker deleted successfully.')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_facility/<int:id>', methods=['POST'])
def delete_facility(id):
    facility = Facility.query.get_or_404(id)
    db.session.delete(facility)
    db.session.commit()
    flash('Facility deleted successfully.')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
