from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from neuroapt.app import db
from neuroapt.app.models import Career, CareerSkill, CareerEducation, CareerSalary, TestResult
from neuroapt.app.utils.openai_api import get_career_insights
import os
import logging

logger = logging.getLogger(__name__)

careers = Blueprint('careers', __name__)

@careers.route('/careers')
def career_library():
    """Redirect to career insights page instead of showing career library"""
    return redirect(url_for('careers.career_insights'))

@careers.route('/careers/category/<string:category>')
def career_category(category):
    """Display careers in a specific category"""
    careers_list = Career.query.filter_by(category=category).all()
    return render_template('career_category.html', 
                          careers=careers_list,
                          category=category,
                          title=f"{category} Careers")

@careers.route('/careers/detail/<int:career_id>')
def career_detail(career_id):
    """Display detailed information about a specific career"""
    career = Career.query.get_or_404(career_id)
    return render_template('career_detail.html', 
                          career=career,
                          title=career.title)

@careers.route('/careers/recommendations')
@login_required
def career_recommendations():
    """Display personalized career recommendations based on test results"""
    # Get user's most recent test result
    test_result = TestResult.query.filter_by(user_id=current_user.id).order_by(
        TestResult.test_date.desc()).first()
    
    if not test_result:
        flash("Please complete a psychometric test first to get personalized recommendations.", "info")
        return redirect(url_for('careers.career_library'))
    
    # Redirect to combined results page which now has AI-powered recommendations
    return redirect(url_for('result.show_combined_result', test_result_id=test_result.id))

@careers.route('/admin/careers/populate', methods=['GET', 'POST'])
@login_required
def populate_careers():
    """Admin endpoint to populate careers - currently disabled"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        flash('Career population feature is currently disabled during AI upgrade.', 'warning')
        return redirect(url_for('careers.populate_careers'))
    
    return render_template('admin/populate_careers.html', 
                          title="Populate Careers")

@careers.route('/careers/insights', methods=['GET', 'POST'])
def career_insights():
    """Get AI-powered insights about careers using OpenAI GPT-4o-mini"""
    insights = None
    query = ""
    
    if request.method == 'POST':
        # Handle both form submissions and AJAX requests
        if request.is_json:
            data = request.get_json()
            query = data.get('query', '')
        else:
            query = request.form.get('query', '')
        
        if not query:
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Please enter a career query'
                }), 400
            else:
                flash('Please enter a career query.', 'warning')
                return redirect(url_for('careers.career_insights'))
        
        # Get AI-powered insights from OpenAI
        try:
            insights = get_career_insights(query)
            
            if not insights:
                # Fallback message if AI fails
                insights = "We're experiencing technical difficulties generating insights. Please try again in a moment, or contact support if the issue persists."
                logger.error(f"Career insights returned None for query: {query}")
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'insights': insights,
                    'query': query
                })
        except Exception as e:
            logger.error(f"Error generating career insights: {str(e)}")
            error_message = "Unable to generate insights at this time. Please try again later."
            
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': error_message
                }), 500
            else:
                flash(error_message, 'danger')
                insights = None
    
    return render_template('career_insights.html', 
                          insights=insights,
                          query=query,
                          title="Career Insights")

@careers.route('/api/careers/insights', methods=['POST'])
def api_career_insights():
    """API endpoint to get career insights using OpenAI"""
    data = request.get_json()
    query = data.get('query', '') if data else ''
    
    if not query:
        return jsonify({
            'success': False,
            'error': 'Query is required'
        }), 400
    
    try:
        # Get AI-powered insights
        insights = get_career_insights(query)
        
        if not insights:
            logger.error(f"API career insights returned None for query: {query}")
            return jsonify({
                'success': False,
                'error': 'Failed to generate insights'
            }), 500
        
        return jsonify({
            'success': True,
            'insights': insights
        })
    except Exception as e:
        logger.error(f"Error in API career insights: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@careers.route('/api/career/<int:career_id>')
def api_career_details(career_id):
    """API endpoint to get career details for modal display"""
    career = Career.query.get_or_404(career_id)
    
    skills = [{"id": skill.id, "name": skill.name} for skill in career.skills]
    
    # Get salary info if available
    salary_info = None
    if career.salary_info:
        salary_info = {
            "entry_level": career.salary_info.entry_level,
            "senior_level": career.salary_info.senior_level
        }
    
    # Get education requirements if available
    education_requirements = None
    if hasattr(career, 'education') and career.education:
        education_requirements = career.education.requirements
        
    # Prepare response data
    career_data = {
        "id": career.id,
        "title": career.title,
        "description": career.description,
        "category": career.category,
        "skills": skills,
        "salary_info": salary_info,
        "education_requirements": education_requirements,
        "job_outlook": career.job_outlook if hasattr(career, 'job_outlook') else None
    }
    
    return jsonify(career_data) 