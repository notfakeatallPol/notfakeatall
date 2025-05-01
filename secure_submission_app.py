import os
import sys
import sqlite3
import datetime
from pathlib import Path
from flask import Flask, render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Determine if we're running in a bundled environment
if getattr(sys, 'frozen', False):
    # If bundled with PyInstaller, get the application's base path
    application_path = sys._MEIPASS
    # Create a user data directory in the user's documents folder
    user_data_dir = os.path.join(os.path.expanduser('~'), 'SecureSubmissionSystem')
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    # Create uploads directory
    uploads_dir = os.path.join(user_data_dir, 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    # Set database path
    db_path = os.path.join(user_data_dir, 'submission_system.db')
    # Set static folder path
    static_folder = os.path.join(application_path, 'static')
    templates_folder = os.path.join(application_path, 'templates')
else:
    # Development environment - use current directory
    application_path = os.path.abspath('.')
    user_data_dir = application_path
    uploads_dir = os.path.join(application_path, 'static', 'uploads')
    # Make sure uploads directory exists
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    db_path = os.path.join(application_path, 'submission_system.db')
    static_folder = os.path.join(application_path, 'static')
    templates_folder = os.path.join(application_path, 'templates')

logger.info(f"Application path: {application_path}")
logger.info(f"User data directory: {user_data_dir}")
logger.info(f"Database path: {db_path}")
logger.info(f"Uploads directory: {uploads_dir}")

# Create the Flask app
app = Flask(__name__, 
            static_folder=static_folder,
            template_folder=templates_folder)
app.secret_key = 'secure_submission_app_secret_key'  # Change this in production

# SQLite database setup
def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Create database tables if they don't exist
def init_db():
    with get_db_connection() as conn:
        # Create users table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL,
            last_login TEXT
        )
        ''')
        
        # Create submissions table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            caption TEXT NOT NULL,
            image_path TEXT,
            encrypted_caption TEXT,
            status TEXT DEFAULT 'pending',
            admin_comment TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create system_config table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS system_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT
        )
        ''')
        
        conn.commit()

# Initialize database
init_db()

# User model
class User:
    def __init__(self, id, username, email, password_hash, role, created_at, last_login):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at
        self.last_login = last_login
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    
    def get_id(self):
        return str(self.id)
    
    @staticmethod
    def get(user_id):
        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            if user:
                return User(
                    id=user['id'],
                    username=user['username'],
                    email=user['email'],
                    password_hash=user['password_hash'],
                    role=user['role'],
                    created_at=user['created_at'],
                    last_login=user['last_login']
                )
        return None
    
    @staticmethod
    def get_by_username(username):
        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if user:
                return User(
                    id=user['id'],
                    username=user['username'],
                    email=user['email'],
                    password_hash=user['password_hash'],
                    role=user['role'],
                    created_at=user['created_at'],
                    last_login=user['last_login']
                )
        return None
    
    @staticmethod
    def get_by_email(email):
        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            if user:
                return User(
                    id=user['id'],
                    username=user['username'],
                    email=user['email'],
                    password_hash=user['password_hash'],
                    role=user['role'],
                    created_at=user['created_at'],
                    last_login=user['last_login']
                )
        return None
    
    @staticmethod
    def create(username, email, password, role='user'):
        password_hash = generate_password_hash(password)
        created_at = datetime.datetime.utcnow().isoformat()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)',
                (username, email, password_hash, role, created_at)
            )
            conn.commit()
            return User.get(cursor.lastrowid)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        last_login = datetime.datetime.utcnow().isoformat()
        with get_db_connection() as conn:
            conn.execute('UPDATE users SET last_login = ? WHERE id = ?', (last_login, self.id))
            conn.commit()
        self.last_login = last_login

# Submission model
class Submission:
    def __init__(self, id, user_id, caption, image_path, encrypted_caption, status, admin_comment, created_at, updated_at):
        self.id = id
        self.user_id = user_id
        self.caption = caption
        self.image_path = image_path
        self.encrypted_caption = encrypted_caption
        self.status = status
        self.admin_comment = admin_comment
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def get(submission_id):
        with get_db_connection() as conn:
            sub = conn.execute('SELECT * FROM submissions WHERE id = ?', (submission_id,)).fetchone()
            if sub:
                return Submission(
                    id=sub['id'],
                    user_id=sub['user_id'],
                    caption=sub['caption'],
                    image_path=sub['image_path'],
                    encrypted_caption=sub['encrypted_caption'],
                    status=sub['status'],
                    admin_comment=sub['admin_comment'],
                    created_at=sub['created_at'],
                    updated_at=sub['updated_at']
                )
        return None
    
    @staticmethod
    def create(user_id, caption, image_path=None):
        now = datetime.datetime.utcnow().isoformat()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO submissions (user_id, caption, image_path, created_at, updated_at) VALUES (?, ?, ?, ?, ?)',
                (user_id, caption, image_path, now, now)
            )
            conn.commit()
            return Submission.get(cursor.lastrowid)
    
    @staticmethod
    def get_all():
        with get_db_connection() as conn:
            submissions = conn.execute('SELECT * FROM submissions ORDER BY created_at DESC').fetchall()
            return [Submission(
                id=sub['id'],
                user_id=sub['user_id'],
                caption=sub['caption'],
                image_path=sub['image_path'],
                encrypted_caption=sub['encrypted_caption'],
                status=sub['status'],
                admin_comment=sub['admin_comment'],
                created_at=sub['created_at'],
                updated_at=sub['updated_at']
            ) for sub in submissions]
    
    @staticmethod
    def get_by_user(user_id):
        with get_db_connection() as conn:
            submissions = conn.execute(
                'SELECT * FROM submissions WHERE user_id = ? ORDER BY created_at DESC', 
                (user_id,)
            ).fetchall()
            return [Submission(
                id=sub['id'],
                user_id=sub['user_id'],
                caption=sub['caption'],
                image_path=sub['image_path'],
                encrypted_caption=sub['encrypted_caption'],
                status=sub['status'],
                admin_comment=sub['admin_comment'],
                created_at=sub['created_at'],
                updated_at=sub['updated_at']
            ) for sub in submissions]
    
    def update_status(self, status, admin_comment=None):
        updated_at = datetime.datetime.utcnow().isoformat()
        with get_db_connection() as conn:
            conn.execute(
                'UPDATE submissions SET status = ?, admin_comment = ?, updated_at = ? WHERE id = ?',
                (status, admin_comment, updated_at, self.id)
            )
            conn.commit()
        self.status = status
        self.admin_comment = admin_comment
        self.updated_at = updated_at
    
    def update_caption(self, caption):
        updated_at = datetime.datetime.utcnow().isoformat()
        with get_db_connection() as conn:
            conn.execute(
                'UPDATE submissions SET caption = ?, updated_at = ? WHERE id = ?',
                (caption, updated_at, self.id)
            )
            conn.commit()
        self.caption = caption
        self.updated_at = updated_at

# System config model
class SystemConfig:
    @staticmethod
    def get(key, default=None):
        with get_db_connection() as conn:
            config = conn.execute('SELECT value FROM system_config WHERE key = ?', (key,)).fetchone()
            return config['value'] if config else default
    
    @staticmethod
    def set(key, value):
        with get_db_connection() as conn:
            existing = conn.execute('SELECT id FROM system_config WHERE key = ?', (key,)).fetchone()
            if existing:
                conn.execute('UPDATE system_config SET value = ? WHERE key = ?', (value, key))
            else:
                conn.execute('INSERT INTO system_config (key, value) VALUES (?, ?)', (key, value))
            conn.commit()

# Utility functions
def get_unique_filename(filename):
    """Generate a unique filename to prevent overwriting."""
    base, ext = os.path.splitext(filename)
    return f"{base}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"

def save_image(file):
    """Save an uploaded image and return the path."""
    if file and file.filename:
        filename = secure_filename(file.filename)
        unique_filename = get_unique_filename(filename)
        file_path = os.path.join(uploads_dir, unique_filename)
        file.save(file_path)
        # Return relative path for database storage
        if getattr(sys, 'frozen', False):
            # For compiled app, store just the filename
            return unique_filename
        else:
            # For development, store relative path
            return os.path.join('uploads', unique_filename)
    return None

def is_setup_required():
    """Check if initial setup is required (no admin exists)."""
    with get_db_connection() as conn:
        admin_count = conn.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'").fetchone()['count']
        return admin_count == 0

def create_admin_user(username, email, password):
    """Create the initial admin user during setup."""
    return User.create(username, email, password, role='admin')

def update_user_login_time(user):
    """Update the last login time for a user."""
    user.update_last_login()

def get_user_stats():
    """Get statistics for admin dashboard."""
    with get_db_connection() as conn:
        user_count = conn.execute("SELECT COUNT(*) as count FROM users WHERE role = 'user'").fetchone()['count']
        submission_counts = {
            'total': conn.execute("SELECT COUNT(*) as count FROM submissions").fetchone()['count'],
            'pending': conn.execute("SELECT COUNT(*) as count FROM submissions WHERE status = 'pending'").fetchone()['count'],
            'accepted': conn.execute("SELECT COUNT(*) as count FROM submissions WHERE status = 'accepted'").fetchone()['count'],
            'rejected': conn.execute("SELECT COUNT(*) as count FROM submissions WHERE status = 'rejected'").fetchone()['count'],
            'needs_edits': conn.execute("SELECT COUNT(*) as count FROM submissions WHERE status = 'needs_edits'").fetchone()['count']
        }
        return {
            'user_count': user_count,
            'submission_counts': submission_counts
        }

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(int(user_id))

# Forms
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, HiddenField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class SetupForm(FlaskForm):
    username = StringField('Admin Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Admin Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Complete Setup')

    def validate_username(self, username):
        if User.get_by_username(username.data):
            raise ValidationError('Username already exists.')

    def validate_email(self, email):
        if User.get_by_email(email.data):
            raise ValidationError('Email already exists.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Create User')

    def validate_username(self, username):
        if User.get_by_username(username.data):
            raise ValidationError('Username already exists.')

    def validate_email(self, email):
        if User.get_by_email(email.data):
            raise ValidationError('Email already exists.')

class SubmissionForm(FlaskForm):
    caption = TextAreaField('Caption', validators=[DataRequired()])
    image = FileField('Image (Optional)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Submit')

class ReviewSubmissionForm(FlaskForm):
    submission_id = HiddenField('Submission ID')
    status = SelectField('Status', choices=[
        ('accepted', 'Accept'),
        ('rejected', 'Reject'),
        ('needs_edits', 'Needs Edits')
    ], validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Review')

# Context processor to inject datetime
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.utcnow()}

# Routes
@app.route('/')
def index():
    if is_setup_required():
        return redirect(url_for('setup'))
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    return render_template('index.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if not is_setup_required():
        flash('Setup has already been completed.', 'info')
        return redirect(url_for('index'))
    
    form = SetupForm()
    if form.validate_on_submit():
        admin = create_admin_user(form.username.data, form.email.data, form.password.data)
        flash('Admin account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('setup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            update_user_login_time(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    stats = get_user_stats()
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/create-user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    form = CreateUserForm()
    if form.validate_on_submit():
        User.create(form.username.data, form.email.data, form.password.data)
        flash('User created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/create_user.html', form=form)

@app.route('/admin/users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    with get_db_connection() as conn:
        users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    
    return render_template('admin/users.html', users=users)

@app.route('/admin/submissions')
@login_required
def admin_submissions():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    submissions = Submission.get_all()
    
    # Get username for each submission
    user_map = {}
    with get_db_connection() as conn:
        for sub in submissions:
            if sub.user_id not in user_map:
                user = conn.execute('SELECT username FROM users WHERE id = ?', (sub.user_id,)).fetchone()
                user_map[sub.user_id] = user['username'] if user else 'Unknown'
    
    return render_template('admin/submissions.html', submissions=submissions, user_map=user_map)

@app.route('/admin/submissions/<int:submission_id>/review', methods=['GET', 'POST'])
@login_required
def review_submission(submission_id):
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    submission = Submission.get(submission_id)
    if not submission:
        flash('Submission not found.', 'danger')
        return redirect(url_for('admin_submissions'))
    
    # Get author name
    with get_db_connection() as conn:
        author = conn.execute('SELECT username FROM users WHERE id = ?', (submission.user_id,)).fetchone()
        author_name = author['username'] if author else 'Unknown'
    
    form = ReviewSubmissionForm(obj=submission)
    if form.validate_on_submit():
        submission.update_status(form.status.data, form.comment.data)
        flash('Review submitted successfully!', 'success')
        return redirect(url_for('admin_submissions'))
    
    return render_template('admin/review_submission.html', 
                          submission=submission, 
                          form=form, 
                          author_name=author_name)

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        flash('This page is for regular users only.', 'warning')
        return redirect(url_for('index'))
    
    submissions = Submission.get_by_user(current_user.id)
    return render_template('user/dashboard.html', submissions=submissions)

@app.route('/user/submissions/create', methods=['GET', 'POST'])
@login_required
def create_submission():
    if current_user.role != 'user':
        flash('This feature is for regular users only.', 'warning')
        return redirect(url_for('index'))
    
    form = SubmissionForm()
    if form.validate_on_submit():
        image_path = None
        if form.image.data:
            image_path = save_image(form.image.data)
        
        submission = Submission.create(
            user_id=current_user.id,
            caption=form.caption.data,
            image_path=image_path
        )
        
        flash('Submission created successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    
    return render_template('user/create_submission.html', form=form)

@app.route('/user/submissions/<int:submission_id>')
@login_required
def submission_details(submission_id):
    submission = Submission.get(submission_id)
    if not submission:
        flash('Submission not found.', 'danger')
        return redirect(url_for('user_dashboard'))
    
    if submission.user_id != current_user.id and current_user.role != 'admin':
        flash('Access denied. You can only view your own submissions.', 'danger')
        return redirect(url_for('user_dashboard'))
    
    return render_template('user/submission_details.html', submission=submission)

@app.route('/user/submissions/<int:submission_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_submission(submission_id):
    submission = Submission.get(submission_id)
    if not submission:
        flash('Submission not found.', 'danger')
        return redirect(url_for('user_dashboard'))
    
    if submission.user_id != current_user.id:
        flash('Access denied. You can only edit your own submissions.', 'danger')
        return redirect(url_for('user_dashboard'))
    
    if submission.status != 'needs_edits':
        flash('You can only edit submissions that require changes.', 'warning')
        return redirect(url_for('submission_details', submission_id=submission_id))
    
    form = SubmissionForm(obj=submission)
    if form.validate_on_submit():
        submission.update_caption(form.caption.data)
        
        if form.image.data:
            image_path = save_image(form.image.data)
            # Update image path in database
            with get_db_connection() as conn:
                conn.execute(
                    'UPDATE submissions SET image_path = ?, updated_at = ? WHERE id = ?',
                    (image_path, datetime.datetime.utcnow().isoformat(), submission.id)
                )
                conn.commit()
        
        # Reset status to pending
        submission.update_status('pending', 'Resubmitted with edits')
        
        flash('Submission updated successfully!', 'success')
        return redirect(url_for('submission_details', submission_id=submission_id))
    
    return render_template('user/edit_submission.html', form=form, submission=submission)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    if getattr(sys, 'frozen', False):
        # For compiled app, serve from user data directory
        return send_from_directory(uploads_dir, filename)
    else:
        # For development, use the static folder
        return send_from_directory(os.path.join(application_path, 'static', 'uploads'), filename)


if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        print(f"Starting Secure Submission System")
        print(f"User data directory: {user_data_dir}")
        print(f"Access the application at http://127.0.0.1:5000")
        app.run(host='127.0.0.1', port=5000, debug=False)
    else:
        # Running in development mode
        app.run(host='0.0.0.0', port=5000, debug=True)