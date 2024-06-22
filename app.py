from asyncio import Task
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required
from sqlalchemy.orm import relationship
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
login_manager.login_view = 'login'
migrate = Migrate(app, db)
login_manager.login_view = 'facility_login'

class HealthWorker(UserMixin, db.Model):
    __tablename__ = 'health_worker'
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
    password_hash = db.Column(db.String(128), nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    assigned_facility_id = db.Column(db.Integer, db.ForeignKey('facility.id'))
    assigned_facility = relationship('Facility', back_populates='assigned_workers', foreign_keys=[assigned_facility_id])

    @property
    def facility(self):
        return Facility.query.get(self.assigned_facility_id)

    @property
    def is_assigned(self):
        return self.assigned_facility_id is not None

    def update_status(self):
        self.status = 'Assigned' if self.is_assigned else 'Pending'
        db.session.commit()

class Facility(db.Model):
    __tablename__ = 'facility'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    role = db.Column(db.String(50), nullable=False, default='facility')
    assigned_workers = relationship('HealthWorker', back_populates='assigned_facility', foreign_keys='HealthWorker.assigned_facility_id')
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        # For simplicity, assuming all facilities are active. Adjust as needed.
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return HealthWorker.query.get(int(user_id))

@login_manager.user_loader
def load_user(user_id):
    return Facility.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register-healthworker', methods=['GET', 'POST'])
def register_healthworker():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('register_healthworker'))

        existing_healthworker = HealthWorker.query.filter_by(email=email).first()
        if existing_healthworker:
            flash('Email already registered. Please use a different email address.', 'danger')
            return redirect(url_for('register_healthworker'))
        
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
            password_hash=generate_password_hash(password)
        )
        try:
            db.session.add(new_healthworker)
            db.session.commit()
            flash('Registration successful! Please wait for admin approval.')
            return redirect(url_for('healthworker_dashboard', id=new_healthworker.id))  # Redirect to health worker dashboard
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('register_healthworker'))
    return render_template('register_healthworker.html')

@app.route('/register-facility', methods=['GET', 'POST'])
def register_facility():
    if request.method == 'POST':
        existing_facility = Facility.query.filter_by(email=request.form['email']).first()
        if existing_facility:
            flash('Email already registered. Please use a different email address.', 'danger')
            return redirect(url_for('register_facility'))

        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('register_facility'))

        new_facility = Facility(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address'],
            location=request.form['location'],
            role='facility'
        )
        new_facility.set_password(password)
        try:
            db.session.add(new_facility)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            # Redirect to facility dashboard with the newly created facility's id
            return redirect(url_for('facility_dashboard', facility_id=new_facility.id))
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('register_facility'))
    return render_template('register_facility.html')

@app.route('/facility-login', methods=['GET', 'POST'])
def facility_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Facility.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('facility_dashboard', facility_id=user.id))  # Specify facility_id
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    return render_template('facility_login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = HealthWorker.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            if user.worker_type == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('healthworker_dashboard', id=user.id))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

# Admin Dashboard Route
@app.route('/admin')
def admin_dashboard():
    location = request.args.get('location')
    worker_type = request.args.get('worker_type')
    facility_location = request.args.get('facility_location')
    task_status = request.args.get('task_status')

    healthworkers = HealthWorker.query.all()
    facilities = Facility.query.all()

    # Apply filters
    if location:
        healthworkers = [hw for hw in healthworkers if hw.location == location]
    if worker_type:
        healthworkers = [hw for hw in healthworkers if hw.worker_type == worker_type]
    if facility_location:
        facilities = [f for f in facilities if f.location == facility_location]
    if task_status:
        tasks = Task.query.filter_by(status=task_status).all()
        healthworkers = [hw for hw in healthworkers if any(task.healthworker_id == hw.id for task in tasks)]

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

# Assign Task Route
@app.route('/assign_task/<int:healthworker_id>', methods=['GET', 'POST'])
def assign_task(healthworker_id):
    healthworker = HealthWorker.query.get_or_404(healthworker_id)
    facilities = Facility.query.all()

    if request.method == 'POST':
        facility_id = request.form.get('facility_id')
        facility = Facility.query.get_or_404(facility_id)

        # Create and save the task
        task = Task(healthworker_id=healthworker.id, facility_id=facility.id, status='Pending')
        db.session.add(task)
        db.session.commit()

        # Update health worker status
        healthworker.status = 'Assigned'
        db.session.commit()

        flash('Task assigned successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('assign_task.html', healthworker=healthworker, facilities=facilities)

@app.route('/create-invoice/<int:id>', methods=['GET', 'POST'])
@login_required
def create_invoice(id):
    if request.method == 'POST':
        client_email = request.form['email']
        service_details = request.form['services']
        total_amount = request.form['amount']
        invoice = f"Invoice Details:\nService: {service_details}\nTotal Amount: {total_amount}"
        
        msg = Message('Invoice from MediConnect International', sender=os.getenv('MAIL_USERNAME'), recipients=[client_email])
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

@app.route('/healthworker-dashboard/<int:id>', methods=['GET', 'POST'])
def healthworker_dashboard(id):
    healthworker = HealthWorker.query.get_or_404(id)

    if request.method == 'POST':
        healthworker.name = request.form['name']
        healthworker.email = request.form['email']
        healthworker.phone = request.form['phone']
        healthworker.address = request.form['address']
        healthworker.qualifications = request.form['qualifications']
        healthworker.experience = request.form['experience']
        healthworker.specializations = request.form['specializations']
        healthworker.availability = request.form['availability']
        healthworker.id_number = request.form['id_number']
        healthworker.cv = request.form['cv']
        healthworker.certifications = request.form['certifications']
        healthworker.photo = request.form['photo']
        healthworker.location = request.form['location']
        healthworker.worker_type = request.form['worker_type']  # Ensure worker_type is updated

        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating profile.', 'danger')
            print(str(e))

    return render_template('healthworker_dashboard.html', healthworker=healthworker)

@app.route('/facility_dashboard/<int:facility_id>')
@login_required
def facility_dashboard(facility_id):
    facility = Facility.query.get_or_404(facility_id)
    return render_template('facility_dashboard.html', facility=facility)

@app.route('/update_facility_profile/<int:facility_id>', methods=['POST'])
@login_required
def update_facility_profile(facility_id):
    facility = Facility.query.get_or_404(facility_id)
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
        
        return redirect(url_for('facility_dashboard', facility_id=facility.id))

    # Handle GET request (if needed)
    return render_template('facility_dashboard.html', facility=facility)
    
@app.route('/healthworker_update_profile/<int:id>', methods=['GET', 'POST'])
@login_required
def healthworker_update_profile(id):
    healthworker = HealthWorker.query.get_or_404(id)
    if request.method == 'POST':
        healthworker.name = request.form['name']
        healthworker.email = request.form['email']
        healthworker.phone = request.form['phone']
        healthworker.address = request.form['address']
        healthworker.qualifications = request.form['qualifications']
        healthworker.experience = request.form['experience']
        healthworker.specializations = request.form['specializations']
        healthworker.availability = request.form['availability']
        healthworker.location = request.form['location']
        healthworker.worker_type = request.form['worker_type']
        healthworker.status = request.form['status']
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            print(str(e))
        
        return redirect(url_for('healthworker_dashboard', id=healthworker.id))

    return render_template('healthworker_dashboard.html', healthworker=healthworker)

@app.route('/assign_healthworker/<int:healthworker_id>', methods=['GET', 'POST'])
@login_required
def assign_healthworker(healthworker_id):
    healthworker = HealthWorker.query.get_or_404(healthworker_id)
    facilities = Facility.query.all()
    if request.method == 'POST':
        try:
            facility_id = request.form['facility']
            facility = Facility.query.get(facility_id)
            if facility:
                healthworker.facility_id = facility.id
                healthworker.status = 'Assigned'
            else:
                healthworker.facility_id = None
                healthworker.status = 'Pending'
            db.session.commit()
            flash('Health worker assigned to facility successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            print(str(e))
        
        return redirect(url_for('healthworker_dashboard', id=healthworker.id))
    
    return render_template('assign_healthworker.html', healthworker=healthworker, facilities=facilities)

@app.route('/unassign_healthworker/<int:healthworker_id>', methods=['POST'])
@login_required
def unassign_healthworker(healthworker_id):
    healthworker = HealthWorker.query.get_or_404(healthworker_id)
    try:
        healthworker.facility_id = None
        healthworker.status = 'Pending'
        db.session.commit()
        flash('Health worker unassigned from facility successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'danger')
        print(str(e))
    
    return redirect(url_for('healthworker_dashboard', id=healthworker.id))

if __name__ == '__main__':
    app.run(debug=True)
