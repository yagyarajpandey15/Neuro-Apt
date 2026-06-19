from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify, session
from flask_login import login_user, current_user, logout_user, login_required
from neuroapt.app import db, bcrypt
from neuroapt.app.models import User
from neuroapt.app.forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
@auth_bp.route('/home')
def home():
    return render_template('index.html', title='Home')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return redirect(url_for('dashboard.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Check if attempting to login as admin
            if form.user_type.data == 'admin' and not user.is_admin:
                flash('You do not have administrator privileges.', 'danger')
                return render_template('login.html', title='Login', form=form)
            
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            
            if user.is_admin and form.user_type.data == 'admin':
                return redirect(next_page) if next_page else redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('dashboard.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.home'))

@auth_bp.route('/toggle-dark-mode', methods=['POST'])
def toggle_dark_mode():
    """Toggle dark mode preference"""
    data = request.get_json()
    if data and 'dark_mode' in data:
        session['dark_mode'] = data['dark_mode']
    return jsonify({'success': True})

@auth_bp.route('/careers/search')
def career_search():
    """Search for careers based on query"""
    query = request.args.get('query', '')
    # This would typically query a database of careers
    # For now, we'll just render a template with the query
    return render_template('career_search.html', 
                          title='Career Search', 
                          query=query,
                          results=[])

@auth_bp.route('/careers/category/<category>')
def career_category(category):
    """Display careers in a specific category"""
    category_name = category.replace('-', ' ').title()
    # This would typically query a database for careers in this category
    # For now, we'll just render a template with the category
    return render_template('career_category.html', 
                          title=f'{category_name} Careers',
                          category=category_name,
                          careers=[])

@auth_bp.route('/careers/detail/<int:career_id>')
def career_detail(career_id):
    """Display details for a specific career"""
    # This would typically query a database for career details
    # For now, we'll just render a template with placeholder data
    career = {
        'id': career_id,
        'title': 'Sample Career',
        'category': 'Technology',
        'description': 'This is a sample career description that would typically come from a database.',
        'salary_range': '$50,000 - $100,000',
        'education_required': "Bachelor's Degree",
        'growth_outlook': 'Faster than average',
        'skills': ['Problem Solving', 'Communication', 'Technical Knowledge', 'Teamwork'],
        'work_environment': 'Office setting with occasional remote work',
        'job_duties': [
            'Analyze and solve complex problems',
            'Collaborate with team members on projects',
            'Develop and implement new strategies',
            'Communicate with stakeholders'
        ]
    }
    
    return render_template('career_detail.html',
                          title=career['title'],
                          career=career)

@auth_bp.route('/about')
def about():
    """About page with information about the psychometric test platform"""
    return render_template('about.html', title='About Us')

@auth_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with form for users to get in touch"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # In a real application, you would send this message via email
        # or save it to a database for admin review
        
        flash('Your message has been sent! We will get back to you soon.', 'success')
        return redirect(url_for('auth.contact'))
        
    return render_template('contact.html', title='Contact Us') 