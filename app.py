from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import UTC, datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kenliz_careconnect.db'
app.config['SECRET_KEY'] = 'kenzym04'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'kenlizccareconnect@gmail.com'
app.config['MAIL_PASSWORD'] = 'kenlizccareconnect24$#'

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)

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
        
        msg = Message('Invoice from KenLiz CareConnect', sender='your_email@example.com', recipients=[client_email])
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

if __name__ == '__main__':
    app.run(debug=True)
