from flask import Blueprint, redirect, url_for, current_app, render_template, request
from flask_login import current_user, login_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Redirect to dashboard if logged in, otherwise to login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    else:
        return redirect(url_for('auth.login'))

@main.route('/insights')
@login_required
def insights_redirect():
    """Redirect to the careers insights page for easier access"""
    return redirect(url_for('careers.career_insights'))

@main.route('/recommendations')
@login_required
def recommendations():
    """Redirect to combined results page which now has AI-powered recommendations"""
    from neuroapt.app.models import TestResult
    
    # Get user's most recent test result
    test_result = TestResult.query.filter_by(user_id=current_user.id).order_by(
        TestResult.test_date.desc()).first()
    
    if not test_result:
        return render_template('careers/no_results.html', 
                              message="Please complete a test first to get personalized recommendations.")
    
    # Redirect to combined results page which has AI-powered career recommendations
    return redirect(url_for('result.show_combined_result', test_result_id=test_result.id)) 