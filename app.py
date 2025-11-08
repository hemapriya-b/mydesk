from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    subjects = db.relationship('Subject', backref='user', lazy=True)
    notes = db.relationship('Note', backref='user', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    units = db.relationship('Unit', backref='subject', lazy=True)
    notes = db.relationship('Note', backref='subject', lazy=True)  # Added this relationship

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    
    notes = db.relationship('Note', backref='unit', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255))
    file_path = db.Column(db.String(500))
    file_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('signup'))
        
        # Create new user
        new_user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully!', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's data for dashboard
    total_subjects = Subject.query.filter_by(user_id=current_user.id).count()
    total_notes = Note.query.filter_by(user_id=current_user.id).count()
    total_units = Unit.query.join(Subject).filter(Subject.user_id == current_user.id).count()
    
    # Get recent notes (last 5)
    recent_notes = Note.query.filter_by(user_id=current_user.id)\
        .order_by(Note.created_at.desc())\
        .limit(5)\
        .all()
    
    # Get all subjects for the create subject card
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    
    return render_template('dashboard.html',
                         total_subjects=total_subjects,
                         total_notes=total_notes,
                         total_units=total_units,
                         recent_notes=recent_notes,
                         subjects=subjects)

@app.route('/subjects', methods=['GET', 'POST'])
@login_required
def subjects():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        new_subject = Subject(
            name=name,
            description=description,
            user_id=current_user.id
        )
        
        db.session.add(new_subject)
        db.session.commit()
        
        flash(f'Subject "{name}" created successfully!', 'success')
        return redirect(url_for('subjects'))
    
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('subjects.html', subjects=subjects)

@app.route('/subject/<int:subject_id>')
@login_required
def view_subject(subject_id):
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    units = Unit.query.filter_by(subject_id=subject_id).all()
    return render_template('units.html', subject=subject, units=units)

@app.route('/subject/<int:subject_id>/add_unit', methods=['POST'])
@login_required
def add_unit(subject_id):
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    
    name = request.form['name']
    description = request.form['description']
    
    new_unit = Unit(
        name=name,
        description=description,
        subject_id=subject_id
    )
    
    db.session.add(new_unit)
    db.session.commit()
    
    flash(f'Unit "{name}" added successfully!', 'success')
    return redirect(url_for('view_subject', subject_id=subject_id))

@app.route('/subject/<int:subject_id>/delete')
@login_required
def delete_subject(subject_id):
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    
    # Delete all notes and units associated with this subject
    Note.query.filter_by(subject_id=subject_id).delete()
    Unit.query.filter_by(subject_id=subject_id).delete()
    
    db.session.delete(subject)
    db.session.commit()
    
    flash(f'Subject "{subject.name}" deleted successfully!', 'success')
    return redirect(url_for('subjects'))

@app.route('/unit/<int:unit_id>/delete')
@login_required
def delete_unit(unit_id):
    unit = Unit.query.join(Subject).filter(Unit.id == unit_id, Subject.user_id == current_user.id).first_or_404()
    subject_id = unit.subject_id
    
    # Delete all notes associated with this unit
    Note.query.filter_by(unit_id=unit_id).delete()
    
    db.session.delete(unit)
    db.session.commit()
    
    flash(f'Unit "{unit.name}" deleted successfully!', 'success')
    return redirect(url_for('view_subject', subject_id=subject_id))

@app.route('/notes')
@login_required
def notes():
    # FIXED: Added joins to include subject and unit data
    notes = Note.query.filter_by(user_id=current_user.id)\
        .join(Subject, Note.subject_id == Subject.id)\
        .join(Unit, Note.unit_id == Unit.id)\
        .order_by(Note.created_at.desc())\
        .all()
    
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('notes.html', notes=notes, subjects=subjects)

@app.route('/add_note', methods=['GET', 'POST'])
@login_required
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        subject_id = request.form['subject_id']
        unit_id = request.form.get('unit_id')  # FIXED: Use get() to avoid KeyError
        
        # Check if required fields are present
        if not unit_id:
            flash('Please select both subject and unit!', 'danger')
            return redirect(request.url)
        
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected!', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected!', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Ensure unique filename
            counter = 1
            while os.path.exists(file_path):
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{counter}{ext}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                counter += 1
            
            file.save(file_path)
            
            # Get file type
            file_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown'
            
            new_note = Note(
                title=title,
                description=description,
                filename=filename,
                file_path=file_path,
                file_type=file_type,
                user_id=current_user.id,
                subject_id=subject_id,
                unit_id=unit_id
            )
            
            db.session.add(new_note)
            db.session.commit()
            
            flash(f'Note "{title}" added successfully!', 'success')
            return redirect(url_for('notes'))
        else:
            flash('File type not allowed!', 'danger')
            return redirect(request.url)
    
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('add_note.html', subjects=subjects)

@app.route('/get_units/<int:subject_id>')
@login_required
def get_units(subject_id):
    units = Unit.query.filter_by(subject_id=subject_id).all()
    units_data = [{'id': unit.id, 'name': unit.name} for unit in units]
    return jsonify(units_data)

@app.route('/view_note/<int:note_id>')
@login_required
def view_note(note_id):
    # FIXED: Added joins to include subject and unit data
    note = Note.query.filter_by(id=note_id, user_id=current_user.id)\
        .join(Subject, Note.subject_id == Subject.id)\
        .join(Unit, Note.unit_id == Unit.id)\
        .first_or_404()
    
    file_content = None
    if note.file_type == 'txt' and os.path.exists(note.file_path):
        try:
            with open(note.file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except:
            file_content = "Unable to read file content"
    
    return render_template('view_note.html', note=note, file_content=file_content)

@app.route('/download_note/<int:note_id>')
@login_required
def download_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    return send_file(note.file_path, as_attachment=True, download_name=note.filename)

@app.route('/delete_note/<int:note_id>')
@login_required
def delete_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    
    # Delete the file from filesystem
    if os.path.exists(note.file_path):
        os.remove(note.file_path)
    
    db.session.delete(note)
    db.session.commit()
    
    flash(f'Note "{note.title}" deleted successfully!', 'success')
    return redirect(url_for('notes'))

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    
    if query:
        # Search in notes, subjects, and units
        # FIXED: Added joins for notes search
        notes_results = Note.query.filter(
            Note.user_id == current_user.id,
            (Note.title.ilike(f'%{query}%')) | (Note.description.ilike(f'%{query}%'))
        ).join(Subject, Note.subject_id == Subject.id)\
         .join(Unit, Note.unit_id == Unit.id)\
         .all()
        
        subjects_results = Subject.query.filter(
            Subject.user_id == current_user.id,
            (Subject.name.ilike(f'%{query}%')) | (Subject.description.ilike(f'%{query}%'))
        ).all()
        
        units_results = Unit.query.join(Subject).filter(
            Subject.user_id == current_user.id,
            (Unit.name.ilike(f'%{query}%')) | (Unit.description.ilike(f'%{query}%'))
        ).all()
    else:
        notes_results = []
        subjects_results = []
        units_results = []
    
    return render_template('search.html',
                         query=query,
                         notes_results=notes_results,
                         subjects_results=subjects_results,
                         units_results=units_results)

# with app.app_context():
#    db.create_all()