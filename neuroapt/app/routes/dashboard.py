from flask import Blueprint, render_template
from flask_login import current_user, login_required
from neuroapt.app.models import TestResult

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    # Get the user's most recent test result
    latest_result = TestResult.query.filter_by(user_id=current_user.id).order_by(TestResult.test_date.desc()).first()
    
    # Get the total number of tests taken by the user
    tests_taken = TestResult.query.filter_by(user_id=current_user.id).count()
    
    return render_template('dashboard.html', 
                          title='Dashboard',
                          latest_result=latest_result,
                          tests_taken=tests_taken)
 