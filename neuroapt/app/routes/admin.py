from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, make_response
from flask_login import current_user, login_required
from neuroapt.app import db
from neuroapt.app.models import User, Question, QuestionOption, TestResult, UserAnswer
from neuroapt.app.forms import QuestionForm, OptionForm
from neuroapt.app.utils.cache_manager import invalidate_cache
from neuroapt.app.utils.orchestrator import analyze_student_profile
from functools import wraps
from datetime import datetime, timedelta
import io

# Try to import weasyprint, but don't fail if it's not available
try:
    from weasyprint import HTML
    has_weasyprint = True
except ImportError:
    has_weasyprint = False
    HTML = None

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Count statistics for the dashboard
    total_users = User.query.count()
    total_admins = User.query.filter_by(is_admin=True).count()
    total_results = TestResult.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_tests = TestResult.query.order_by(TestResult.test_date.desc()).limit(5).all()
    
    # Active users (users who took a test in the last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_users_count = db.session.query(User).join(TestResult).filter(TestResult.test_date > seven_days_ago).distinct().count()
    
    return render_template('admin_dashboard.html', 
                          title='Admin Dashboard',
                          total_users=total_users,
                          total_admins=total_admins,
                          total_results=total_results,
                          active_users=active_users_count,
                          recent_users=recent_users,
                          recent_tests=recent_tests)

@admin_bp.route('/admin/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    
    # Get statistics for the user management page
    total_tests = TestResult.query.count()
    admin_count = User.query.filter_by(is_admin=True).count()
    active_users = db.session.query(User).join(TestResult).filter(
        TestResult.test_date > (datetime.utcnow() - timedelta(days=30))
    ).distinct().count()
    
    return render_template('admin_users.html', 
                          title='Manage Users', 
                          users=users,
                          total_tests=total_tests,
                          admin_count=admin_count,
                          active_users=active_users)

@admin_bp.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent removing admin status from yourself
    if user.id == current_user.id:
        flash('You cannot remove your own administrator privileges.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    action = "granted to" if user.is_admin else "removed from"
    flash(f'Administrator privileges {action} {user.username} successfully.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/admin/users/<int:user_id>/results')
@login_required
@admin_required
def view_user_results(user_id):
    user = User.query.get_or_404(user_id)
    results = TestResult.query.filter_by(user_id=user_id).order_by(TestResult.test_date.desc()).all()
    
    return render_template('admin_user_results.html',
                          title=f'Results for {user.username}',
                          user=user,
                          results=results)

@admin_bp.route('/admin/questions')
@login_required
@admin_required
def manage_questions():
    questions = Question.query.all()
    return render_template('admin_questions.html', title='Manage Questions', questions=questions)

@admin_bp.route('/admin/questions/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_question():
    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(category=form.category.data.lower(), content=form.content.data)
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('admin.add_options', question_id=question.id))
    return render_template('admin_add_question.html', title='Add Question', form=form)

@admin_bp.route('/admin/questions/<int:question_id>/options/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_options(question_id):
    question = Question.query.get_or_404(question_id)
    form = OptionForm()
    if form.validate_on_submit():
        option = QuestionOption(
            question_id=question_id,
            content=form.content.data,
            is_correct=form.is_correct.data,
            score_value=int(form.score_value.data)
        )
        db.session.add(option)
        db.session.commit()
        flash('Option added successfully!', 'success')
        
        # Check if we want to add another option
        if 'add_another' in request.form:
            return redirect(url_for('admin.add_options', question_id=question_id))
        else:
            return redirect(url_for('admin.manage_questions'))
    
    return render_template('admin_add_option.html', title='Add Option', form=form, question=question)

@admin_bp.route('/admin/questions/<int:question_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin.manage_questions'))

@admin_bp.route('/admin/results')
@login_required
@admin_required
def view_results():
    results = TestResult.query.order_by(TestResult.test_date.desc()).all()
    users = User.query.all()
    
    # Calculate statistics
    today = datetime.utcnow().date()
    today_tests = TestResult.query.filter(db.func.date(TestResult.test_date) == today).count()
    
    # Calculate average score
    avg_score = 0
    if results:
        total = sum(result.total_score for result in results)
        avg_score = round(total / len(results))
    
    # Count active tests (in the last 24 hours)
    day_ago = datetime.utcnow() - timedelta(hours=24)
    active_tests = TestResult.query.filter(TestResult.test_date > day_ago).count()
    
    return render_template('admin_results.html', 
                          title='All Test Results', 
                          results=results,
                          users=users,
                          today_tests=today_tests,
                          avg_score=avg_score,
                          active_tests=active_tests)

@admin_bp.route('/admin/results/<int:result_id>')
@login_required
@admin_required
def view_result_detail(result_id):
    result = TestResult.query.get_or_404(result_id)
    return render_template('admin_result_detail.html',
                          title=f'Result Details for {result.user_account.username}',
                          result=result)

@admin_bp.route('/admin/results/<int:result_id>/pdf')
@login_required
@admin_required
def download_pdf(result_id):
    result = TestResult.query.get_or_404(result_id)
    
    if not has_weasyprint:
        flash('PDF generation requires the weasyprint library. Please install it with: pip install weasyprint', 'warning')
        return redirect(url_for('admin.view_result_detail', result_id=result_id))
    
    try:
        # Generate the HTML for the PDF using the same template as the result detail page
        html_content = render_template('pdf_report.html', 
                                      title=f'Psychometric Test Results - {result.user_account.username}',
                                      result=result)
        
        # Generate PDF from HTML
        pdf_file = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)
        
        # Create response
        pdf_file.seek(0)
        response = make_response(pdf_file.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=test_result_{result_id}.pdf'
        
        return response
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'danger')
        return redirect(url_for('admin.view_result_detail', result_id=result_id))

@admin_bp.route('/admin/regenerate-analysis/<int:result_id>', methods=['POST'])
@login_required
def regenerate_analysis(result_id):
    if not getattr(current_user, 'is_admin', False):
        abort(403)
    test_result = TestResult.query.get_or_404(result_id)
    invalidate_cache(test_result)
    outcome = analyze_student_profile(test_result, user_id=current_user.id, force_regenerate=True)
    flash(f"Analysis regenerated. Source: {outcome['source']}", "success")
    return redirect(url_for('result.show_result', test_result_id=result_id)) 