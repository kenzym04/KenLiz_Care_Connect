from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from datetime import UTC, datetime

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///default.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'localhost')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 25))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'default_username')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'default_password')

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
migrate = Migrate(app, db)

class HealthWorker(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    qualifications = db.Column(db.Text, nullable=False)
    experience = db.Column(db.Text, nullable=False)
    specializations = db.Column(db.Text, nullable=True)
    availability = db.Column(db.String(20), nullable=False, default='Available')
    worker_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    id_number = db.Column(db.String(100), nullable=False)
    cv = db.Column(db.String(100), nullable=False)
    certifications = db.Column(db.String(200), nullable=True)
    photo = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    password = db.Column(db.String(200), nullable=False)

class Facility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

@login_manager.user_loader
def load_user(user_id):
    return HealthWorker.query.get(int(user_id))

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
            location=request.form['location'],
            password=generate_password_hash(request.form['password'])
        )
        db.session.add(new_healthworker)
        db.session.commit()
        flash('Registration successful! Please wait for admin approval.')
        return redirect(url_for('index'))
    return render_template('register_healthworker.html')

@app.route('/register-facility', methods=['GET', 'POST'])
def register_facility():
    if request.method == 'POST':
        # Check if the email already exists
        existing_facility = Facility.query.filter_by(email=request.form['email']).first()
        if existing_facility:
            flash('Email already registered. Please use a different email address.', 'danger')
            return redirect(url_for('register_facility'))

        new_facility = Facility(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address'],
            location=request.form['location']
        )

        try:
            db.session.add(new_facility)
            db.session.commit()
            flash('Registration successful! You are being redirected to your dashboard.', 'success')
            return redirect(url_for('facility_dashboard', id=new_facility.id))
        except IntegrityError:
            db.session.rollback()
            flash('Email already registered. Please use a different email address.', 'danger')
            return redirect(url_for('register_facility'))
    return render_template('register_facility.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        healthworker = HealthWorker.query.filter_by(email=email).first()
        if healthworker and check_password_hash(healthworker.password, password):
            login_user(healthworker)
            if healthworker.worker_type == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif healthworker.worker_type == 'healthworker':
                return redirect(url_for('healthworker_dashboard', id=healthworker.id))
        facility = Facility.query.filter_by(email=email).first()
        if facility:
            session['user_id'] = facility.id
            session['user_type'] = 'facility'
            flash('Login successful.')
            return redirect(url_for('facility_dashboard', id=facility.id))
        else:
            flash('Invalid email or password.')
    return render_template('login.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.worker_type != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('index'))
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
@login_required
def healthworker_update(id):
    healthworker = HealthWorker.query.get_or_404(id)
    if request.method == 'POST':
        healthworker.availability = request.form['availability']
        db.session.commit()
        flash('Availability updated successfully.')
        return redirect(url_for('admin_dashboard'))
    return render_template('healthworker_update.html', healthworker=healthworker)

@app.route('/assign-task/<int:id>', methods=['GET', 'POST'])
@login_required
def assign_task(id):
    healthworker = HealthWorker.query.get_or_404(id)
    if request.method == 'POST':
        healthworker.status = 'deployed'
        db.session.commit()
        flash('Health worker assigned to task successfully.')
        return redirect(url_for('admin_dashboard'))
    return render_template('assign_task.html', healthworker=healthworker)

@app.route('/create-invoice/<int:id>', methods=['GET', 'POST'])
@login_required
def create_invoice(id):
    if request.method == 'POST':
        client_email = request.form['email']
        service_details = request.form['services']
        total_amount = request.form['amount']
        invoice = f"Invoice Details:\nService: {service_details}\nTotal Amount: {total_amount}"
        
        msg = Message('Invoice from KenLiz CareConnect', sender=os.getenv('MAIL_USERNAME'), recipients=[client_email])
        msg.body = invoice
        mail.send(msg)

        flash('Invoice sent successfully.')
        return redirect(url_for('admin_dashboard'))
    return render_template('create_invoice.html', id=id)

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
@login_required
def delete_healthworker(id):
    healthworker = HealthWorker.query.get_or_404(id)
    db.session.delete(healthworker)
    db.session.commit()
    flash('Health worker deleted successfully.')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_facility/<int:id>', methods=['POST'])
@login_required
def delete_facility(id):
    facility = Facility.query.get_or_404(id)
    db.session.delete(facility)
    db.session.commit()
    flash('Facility deleted successfully.')
    return redirect(url_for('admin_dashboard'))

@app.route('/healthworker_dashboard/<int:id>')
@login_required
def healthworker_dashboard(id):
    healthworker = HealthWorker.query.get_or_404(id)
    return render_template('healthworker_dashboard.html', healthworker=healthworker)

@app.route('/facility_dashboard/<int:id>')
@login_required
def facility_dashboard(id):
    facility = Facility.query.get_or_404(id)
    return render_template('facility_dashboard.html', facility=facility)

@app.route('/update_facility_profile/<int:id>', methods=['POST'])
@login_required
def update_facility_profile(id):
    facility = Facility.query.get_or_404(id)
    if request.method == 'POST':
        facility.name = request.form['name']
        facility.email = request.form['email']
        facility.phone = request.form['phone']
        facility.address = request.form['address']
        facility.location = request.form['location']
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
        
        return redirect(url_for('facility_dashboard', id=facility.id))


if __name__ == '__main__':
    app.run(debug=True)
