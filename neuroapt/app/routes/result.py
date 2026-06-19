from flask import Blueprint, render_template, url_for, flash, redirect, abort, send_file, make_response, request
from flask_login import current_user, login_required
from neuroapt.app import db
from neuroapt.app.models import TestResult, UserAnswer
from neuroapt.app.utils.scoring import calculate_scores, get_percentile, get_interest_category_descriptions, get_orientation_style
from neuroapt.app.utils.recommendation_engine import get_career_recommendations, get_skill_development_recommendations
from neuroapt.app.utils.orchestrator import analyze_student_profile
import io
import os
from datetime import datetime

result_bp = Blueprint('result', __name__)

@result_bp.route('/result/<int:test_result_id>')
@login_required
def show_result(test_result_id):
    try:
        test_result = TestResult.query.get_or_404(test_result_id)
        
        # Ensure the user can only view their own results unless they're an admin
        if test_result.user_id != current_user.id and not current_user.is_admin:
            abort(403)
        
        # Calculate scores if not already calculated
        if test_result.total_score == 0:
            test_result = calculate_scores(test_result_id)
            db.session.commit()
        
        # Get percentiles
        orientation_percentile = get_percentile(test_result.orientation_score, 'orientation')
        interest_percentile = get_percentile(test_result.interest_score, 'interest')
        personality_percentile = get_percentile(test_result.personality_score, 'personality')
        aptitude_percentile = get_percentile(test_result.aptitude_score, 'aptitude')
        eq_percentile = get_percentile(test_result.eq_score, 'eq')
        overall_percentile = get_percentile(test_result.total_score)
        
        # Get recommendations with error handling
        try:
            career_recommendations = get_career_recommendations(test_result_id)
        except Exception as e:
            print(f"Error getting career recommendations: {e}")
            career_recommendations = {}
        
        try:
            skill_recommendations = get_skill_development_recommendations(test_result_id)
        except Exception as e:
            print(f"Error getting skill recommendations: {e}")
            skill_recommendations = []
        
        # AI-Enhanced Career Analysis with error handling
        try:
            ai_outcome = analyze_student_profile(test_result, user_id=current_user.id if hasattr(current_user, 'id') else None)
            confidence_level = ai_outcome.get("confidence_level", "UNKNOWN")
            confidence_warning = "Your response patterns show inconsistency. Consider retaking the assessment for more accurate results." if confidence_level in ["LOW", "UNRELIABLE"] else None
            fallback_notice = "AI analysis is temporarily unavailable. Showing statistical recommendations." if ai_outcome.get("fallback_triggered") else None
            ai_analysis = ai_outcome.get("result", {})
            confidence_score = ai_outcome.get("confidence_score", 0)
            pattern_flag = ai_outcome.get("pattern_flag")
            interest_intersection = ai_outcome.get("interest_intersection")
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            confidence_level = "UNKNOWN"
            confidence_warning = None
            fallback_notice = "AI analysis is temporarily unavailable. Showing statistical recommendations."
            ai_analysis = {}
            confidence_score = 0
            pattern_flag = None
            interest_intersection = None
        
        return render_template('results.html', 
                              title='Test Results',
                              test_result=test_result,
                              orientation_percentile=orientation_percentile,
                              interest_percentile=interest_percentile,
                              personality_percentile=personality_percentile,
                              aptitude_percentile=aptitude_percentile,
                              eq_percentile=eq_percentile,
                              overall_percentile=overall_percentile,
                              career_recommendations=career_recommendations,
                              skill_recommendations=skill_recommendations,
                              ai_analysis=ai_analysis,
                              confidence_level=confidence_level,
                              confidence_warning=confidence_warning,
                              confidence_score=confidence_score,
                              fallback_notice=fallback_notice,
                              pattern_flag=pattern_flag,
                              interest_intersection=interest_intersection)
    except Exception as e:
        print(f"Error in show_result: {e}")
        flash(f"An error occurred while loading the results. Please try again or contact support. Error: {str(e)}", "danger")
        return redirect(url_for('dashboard.dashboard'))

@result_bp.route('/result/interest_category/<int:test_result_id>')
@login_required
def show_interest_category_result(test_result_id):
    test_result = TestResult.query.get_or_404(test_result_id)
    
    # Ensure the user can only view their own results unless they're an admin
    if test_result.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Calculate scores if not already calculated
    if test_result.total_score == 0:
        test_result = calculate_scores(test_result_id)
        db.session.commit()
    
    # Get interest category descriptions
    interest_descriptions = get_interest_category_descriptions()
    
    return render_template('result_interest_category.html', 
                          title='Interest Category Results',
                          test_result=test_result,
                          interest_descriptions=interest_descriptions)

@result_bp.route('/results/history')
@login_required
def results_history():
    # Get all test results for the current user
    test_results = TestResult.query.filter_by(user_id=current_user.id).order_by(TestResult.test_date.desc()).all()
    
    return render_template('results_history.html', 
                          title='Test Results History',
                          test_results=test_results)

@result_bp.route('/result/delete/<int:test_result_id>', methods=['POST'])
@login_required
def delete_result(test_result_id):
    test_result = TestResult.query.get_or_404(test_result_id)
    
    # Ensure the user can only delete their own results unless they're an admin
    if test_result.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Delete associated user answers first (due to foreign key constraint)
    UserAnswer.query.filter_by(test_result_id=test_result_id).delete()
    
    # Delete the test result
    db.session.delete(test_result)
    db.session.commit()
    
    flash('Test result deleted successfully.', 'success')
    return redirect(url_for('result.results_history'))

@result_bp.route('/result/orientation/<int:test_result_id>')
@login_required
def show_orientation_result(test_result_id):
    test_result = TestResult.query.get_or_404(test_result_id)
    
    # Ensure the user can only view their own results unless they're an admin
    if test_result.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Calculate scores if not already calculated
    if test_result.total_score == 0:
        test_result = calculate_scores(test_result_id)
        db.session.commit()
    
    # Get orientation style results
    orientation_results = get_orientation_style(test_result_id)
    
    return render_template('orientation_results.html', 
                          title='Orientation Style Results',
                          test_result=test_result,
                          test_result_id=test_result_id,
                          orientation_results=orientation_results)

@result_bp.route('/result/combined/<int:test_result_id>')
@login_required
def show_combined_result(test_result_id):
    test_result = TestResult.query.get_or_404(test_result_id)
    
    # Ensure the user can only view their own results unless they're an admin
    if test_result.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Calculate scores if not already calculated
    if test_result.total_score == 0:
        test_result = calculate_scores(test_result_id)
        db.session.commit()
    
    # Get orientation style results
    orientation_results = get_orientation_style(test_result_id)
    
    # Get interest category descriptions
    interest_descriptions = get_interest_category_descriptions()
    
    # Get career recommendations
    career_recommendations = get_career_recommendations(test_result_id)
    
    return render_template('combined_results.html', 
                          title='Combined Results Dashboard',
                          test_result=test_result,
                          orientation_results=orientation_results,
                          interest_descriptions=interest_descriptions,
                          career_recommendations=career_recommendations)

@result_bp.route('/result/download-pdf/<int:test_result_id>')
@login_required
def download_pdf_report(test_result_id):
    try:
        # Import FPDF2 which has better Unicode support
        from fpdf import FPDF
        
        test_result = TestResult.query.get_or_404(test_result_id)
        
        # Ensure the user can only view their own results unless they're an admin
        if test_result.user_id != current_user.id and not current_user.is_admin:
            abort(403)
        
        # Calculate scores if not already calculated
        if test_result.total_score == 0:
            test_result = calculate_scores(test_result_id)
            db.session.commit()
        
        # Get orientation style results
        orientation_results = get_orientation_style(test_result_id)
        
        # Get recommendations
        career_recommendations = get_career_recommendations(test_result_id)
        skill_recommendations = get_skill_development_recommendations(test_result_id)
        
        # Create PDF using FPDF2
        class PDF(FPDF):
            def header(self):
                # Logo or title could go here if needed
                pass
                
            def footer(self):
                # Position at 1.5 cm from bottom
                self.set_y(-15)
                # Set font
                self.set_font('helvetica', 'I', 8)
                # Page number
                self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
        
        pdf = PDF()
        pdf.alias_nb_pages()  # For page numbering
        pdf.add_page()
        
        # Enable auto page break
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Set font - use standard fonts to avoid issues
        pdf.set_font('helvetica', 'B', 16)
        
        # Title
        pdf.cell(0, 10, 'Psychometric Test Results', 0, 1, 'C')
        pdf.set_font('helvetica', '', 12)
        pdf.cell(0, 10, f"Test Date: {test_result.test_date.strftime('%B %d, %Y')}", 0, 1, 'C')
        pdf.cell(0, 10, f"User: {current_user.full_name}", 0, 1, 'C')
        pdf.ln(5)
        
        # Overall Score in table format
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'Overall Performance', 0, 1)
        
        # Table headers
        pdf.set_fill_color(240, 240, 240)  # Light gray background
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(130, 10, 'Metric', 1, 0, 'L', 1)
        pdf.cell(60, 10, 'Score', 1, 1, 'C', 1)
        
        # Table data
        pdf.set_font('helvetica', '', 12)
        pdf.cell(130, 10, 'Total Score', 1, 0, 'L')
        pdf.cell(60, 10, f"{test_result.total_score}/500", 1, 1, 'C')
        pdf.ln(5)
        
        # Section Scores in table format
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'Section Scores', 0, 1)
        
        # Table headers
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(130, 10, 'Section', 1, 0, 'L', 1)
        pdf.cell(60, 10, 'Score', 1, 1, 'C', 1)
        
        # Table data
        pdf.set_font('helvetica', '', 12)
        section_scores = [
            ("Orientation", f"{test_result.orientation_score}/100"),
            ("Interest", f"{test_result.interest_score}/100"),
            ("Personality", f"{test_result.personality_score}/100"),
            ("Aptitude", f"{test_result.aptitude_score}/100"),
            ("Emotional Quotient", f"{test_result.eq_score}/100"),
            ("Work Style", f"{test_result.work_style_score}/100")
        ]
        
        for section, score in section_scores:
            pdf.cell(130, 10, section, 1, 0, 'L')
            pdf.cell(60, 10, score, 1, 1, 'C')
        pdf.ln(5)
        
        # Personality Traits in table format
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'Personality Profile', 0, 1)
        
        # Table headers
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(130, 10, 'Trait', 1, 0, 'L', 1)
        pdf.cell(60, 10, 'Score', 1, 1, 'C', 1)
        
        # Table data
        pdf.set_font('helvetica', '', 12)
        personality_traits = [
            ("Openness", f"{test_result.openness_score}/40"),
            ("Conscientiousness", f"{test_result.conscientiousness_score}/40"),
            ("Extraversion", f"{test_result.extraversion_score}/40"),
            ("Agreeableness", f"{test_result.agreeableness_score}/40"),
            ("Neuroticism", f"{test_result.neuroticism_score}/40")
        ]
        
        for trait, score in personality_traits:
            pdf.cell(130, 10, trait, 1, 0, 'L')
            pdf.cell(60, 10, score, 1, 1, 'C')
        pdf.ln(5)
        
        # Orientation Styles in table format
        if orientation_results and 'scores' in orientation_results:
            pdf.set_font('helvetica', 'B', 14)
            pdf.cell(0, 10, 'Orientation Style', 0, 1)
            
            # Table headers
            pdf.set_fill_color(240, 240, 240)
            pdf.set_font('helvetica', 'B', 12)
            pdf.cell(130, 10, 'Style', 1, 0, 'L', 1)
            pdf.cell(60, 10, 'Score', 1, 1, 'C', 1)
            
            # Table data
            pdf.set_font('helvetica', '', 12)
            for style, score in orientation_results['scores'].items():
                pdf.cell(130, 10, style, 1, 0, 'L')
                pdf.cell(60, 10, f"{score}/40", 1, 1, 'C')
            
            # Dominant style
            if 'dominant_style' in orientation_results and orientation_results['dominant_style']:
                pdf.set_font('helvetica', 'B', 12)
                pdf.cell(0, 10, f"Primary Style: {orientation_results['dominant_style']}", 0, 1)
            pdf.ln(5)
        
        # Career Recommendations
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'Career Recommendations Based on Your Abilities', 0, 1)
        
        if career_recommendations and isinstance(career_recommendations, dict):
            # Loop through top 3 categories to get careers
            for i, (category, data) in enumerate(career_recommendations.items()):
                if i >= 3:  # Limit to top 3 categories
                    break
                
                # Category header with match percentage
                pdf.set_font('helvetica', 'B', 12)
                pdf.cell(0, 10, f"{data['description']} ({data['match_percentage']}% match)", 0, 1)
                
                # Ability Match Analysis - Table headers
                pdf.set_fill_color(240, 240, 240)
                pdf.set_font('helvetica', 'B', 11)
                pdf.cell(190, 10, 'Ability Match Analysis', 1, 1, 'L', 1)
                
                # Ability Match Analysis - Table data
                pdf.set_font('helvetica', '', 11)
                
                # Check if abilities_breakdown exists and has the expected structure
                if 'abilities_breakdown' in data:
                    # Cognitive ability
                    cognitive = data['abilities_breakdown'].get('cognitive', 0)
                    pdf.cell(60, 8, 'Cognitive Abilities:', 1, 0, 'L')
                    pdf.cell(130, 8, f"{cognitive}%", 1, 1, 'L')
                    
                    # Personality traits
                    personality = data['abilities_breakdown'].get('personality', 0)
                    pdf.cell(60, 8, 'Personality Traits:', 1, 0, 'L')
                    pdf.cell(130, 8, f"{personality}%", 1, 1, 'L')
                    
                    # Emotional intelligence
                    eq = data['abilities_breakdown'].get('emotional_intelligence', 0)
                    if eq:
                        pdf.cell(60, 8, 'Emotional Intelligence:', 1, 0, 'L')
                        pdf.cell(130, 8, f"{eq}%", 1, 1, 'L')
                
                # Your Matching Traits
                if 'matching_traits' in data and isinstance(data['matching_traits'], list):
                    pdf.set_fill_color(240, 240, 240)
                    pdf.set_font('helvetica', 'B', 11)
                    pdf.cell(190, 10, 'Your Matching Traits', 1, 1, 'L', 1)
                    
                    pdf.set_font('helvetica', '', 11)
                    for trait in data['matching_traits']:
                        if isinstance(trait, dict) and 'trait' in trait and 'match_percent' in trait:
                            trait_name = trait['trait'].capitalize()
                            match_percent = round(trait['match_percent'])
                            pdf.cell(60, 8, trait_name + ':', 1, 0, 'L')
                            pdf.cell(130, 8, f"{match_percent}% match", 1, 1, 'L')
                
                # Career list header
                pdf.set_fill_color(240, 240, 240)
                pdf.set_font('helvetica', 'B', 11)
                pdf.cell(190, 10, 'Recommended Careers', 1, 1, 'L', 1)
                
                # Career list
                pdf.set_font('helvetica', '', 11)
                if 'careers' in data and isinstance(data['careers'], list):
                    for career in data['careers']:
                        pdf.cell(190, 8, f"- {career}", 1, 1, 'L')
                
                # Future outlook
                if 'future_outlook' in data:
                    pdf.set_fill_color(240, 240, 240)
                    pdf.set_font('helvetica', 'B', 11)
                    pdf.cell(190, 10, 'Industry Outlook', 1, 1, 'L', 1)
                    
                    pdf.set_font('helvetica', '', 11)
                    pdf.cell(190, 8, data['future_outlook'], 1, 1, 'L')
                
                # Add a small gap between categories
                pdf.ln(5)
        else:
            pdf.set_font('helvetica', '', 12)
            pdf.cell(0, 10, "No specific career recommendations available", 0, 1)
        pdf.ln(5)
        
        # Skill Recommendations
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'Skill Development Recommendations', 0, 1)
        
        if skill_recommendations and isinstance(skill_recommendations, list):
            # Take only the first 4 recommendations if there are more
            recommendations_to_show = skill_recommendations[:4] if len(skill_recommendations) > 4 else skill_recommendations
            
            for recommendation in recommendations_to_show:
                if isinstance(recommendation, dict) and 'area' in recommendation:
                    # Skill area header
                    pdf.set_font('helvetica', 'B', 12)
                    pdf.cell(0, 10, f"{recommendation['area']}", 0, 1)
                    
                    # Table header
                    pdf.set_fill_color(240, 240, 240)
                    pdf.set_font('helvetica', 'B', 11)
                    pdf.cell(190, 10, 'Recommended Activities', 1, 1, 'L', 1)
                    
                    # Activities
                    pdf.set_font('helvetica', '', 11)
                    if 'activities' in recommendation and isinstance(recommendation['activities'], list):
                        # Show only first 3 activities to keep the PDF concise
                        activities = recommendation['activities'][:3] if len(recommendation['activities']) > 3 else recommendation['activities']
                        for activity in activities:
                            pdf.cell(190, 8, f"- {activity}", 1, 1, 'L')
                    
                    # Add a small gap between skill areas
                    pdf.ln(3)
                else:
                    # Simple text fallback
                    pdf.set_font('helvetica', '', 11)
                    pdf.cell(0, 8, f"- {recommendation}", 0, 1)
        else:
            pdf.set_font('helvetica', '', 12)
            pdf.cell(0, 10, "No specific skill recommendations available", 0, 1)
        
        # Footer information
        pdf.ln(5)
        pdf.set_font('helvetica', 'I', 10)
        pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%B %d, %Y')} by Neuro Apt Psychometric Assessment", 0, 1, 'C')
        
        # Get PDF content using FPDF2's output method
        pdf_content = pdf.output()
        
        # Create response
        filename = f"psychometric_results_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.pdf"
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    except ImportError:
        # If FPDF is not available, show an error message
        flash("PDF generation is not available. Please ensure FPDF2 is properly installed.", "warning")
        return redirect(url_for('result.show_combined_result', test_result_id=test_result_id))
    except Exception as e:
        flash(f"Error generating PDF: {str(e)}", "danger")
        return redirect(url_for('result.show_combined_result', test_result_id=test_result_id)) 