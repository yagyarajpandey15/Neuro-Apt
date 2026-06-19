from flask import Blueprint, render_template, url_for, flash, redirect, request, session, jsonify
from flask_login import current_user, login_required
from neuroapt.app import db
from neuroapt.app.models import Question, QuestionOption, TestResult, UserAnswer
from neuroapt.app.forms import TestAnswerForm
from datetime import datetime
from neuroapt.app.utils.scoring import calculate_scores

test_bp = Blueprint('test', __name__)

@test_bp.route('/test/instructions')
@login_required
def test_instructions():
    return render_template('test_instructions.html', title='Test Instructions')

@test_bp.route('/test/start')
@login_required
def start_test():
    # Create a new test result
    test_result = TestResult(user_id=current_user.id)
    db.session.add(test_result)
    db.session.commit()
    
    # Store the test result ID in the session
    session['test_result_id'] = test_result.id
    session['current_section'] = 'orientation'
    session['section_index'] = 0
    
    # Define the test flow
    test_sections = ['orientation', 'interest', 'personality', 'aptitude', 'eq', 'work_style', 'interest_category']
    session['test_sections'] = test_sections
    
    # MODIFIED: Find a section that has questions
    first_section_with_questions = find_next_section_with_questions('orientation', test_sections)
    if first_section_with_questions != 'orientation':
        session['current_section'] = first_section_with_questions
    
    # Redirect to the test page
    return redirect(url_for('test.test_wizard'))

# Helper function to find next section with questions
def find_next_section_with_questions(current_section, test_sections):
    # Get the index of the current section
    try:
        current_index = test_sections.index(current_section)
    except ValueError:
        # If current section is not in the list, start from the beginning
        current_index = 0
    
    # Check the current section first
    if Question.query.filter_by(category=current_section).count() > 0:
        return current_section
    
    # Loop through remaining sections
    for i in range(current_index + 1, len(test_sections)):
        section = test_sections[i]
        if Question.query.filter_by(category=section).count() > 0:
            return section
    
    # If no sections have questions, return the last section
    return test_sections[-1]

@test_bp.route('/test/wizard')
@login_required
def test_wizard():
    if 'test_result_id' not in session:
        flash('Test session expired. Please start a new test.', 'danger')
        return redirect(url_for('test.test_instructions'))
    
    test_sections = session.get('test_sections', ['orientation', 'interest', 'personality', 'aptitude', 'eq', 'work_style', 'interest_category'])
    current_section = session.get('current_section', 'orientation')
    
    # MODIFIED: Check if current section has questions, if not find one that does
    if Question.query.filter_by(category=current_section).count() == 0:
        next_section = find_next_section_with_questions(current_section, test_sections)
        if next_section != current_section:
            current_section = next_section
            session['current_section'] = current_section
    
    # Check if a section was selected from the buttons
    selected_section = request.args.get('section')
    if selected_section and selected_section in test_sections:
        # Verify the selected section is available (completed or active)
        section_index = test_sections.index(selected_section)
        current_index = test_sections.index(current_section)
        
        if section_index <= current_index:
            # Allow selecting this section
            current_section = selected_section
            session['current_section'] = current_section
    
    section_index = session.get('section_index', 0)
    
    section_progress = {
        'orientation': {'status': 'upcoming', 'icon': 'fas fa-brain'},
        'interest': {'status': 'upcoming', 'icon': 'fas fa-lightbulb'},
        'personality': {'status': 'upcoming', 'icon': 'fas fa-user'},
        'aptitude': {'status': 'upcoming', 'icon': 'fas fa-cogs'},
        'eq': {'status': 'upcoming', 'icon': 'fas fa-heart'},
        'work_style': {'status': 'upcoming', 'icon': 'fas fa-briefcase'},
        'interest_category': {'status': 'upcoming', 'icon': 'fas fa-compass'}
    }
    
    # Update section statuses based on progress
    for i, section in enumerate(test_sections):
        if i < test_sections.index(current_section):
            section_progress[section]['status'] = 'completed'
        elif i == test_sections.index(current_section):
            section_progress[section]['status'] = 'active'
        else:
            section_progress[section]['status'] = 'upcoming'
    
    return render_template('test_wizard.html', 
                           title='Psychometric Test',
                           test_sections=test_sections,
                           current_section=current_section,
                           section_progress=section_progress)

@test_bp.route('/test/section/<section>/<int:index>', methods=['GET', 'POST'])
@login_required
def section_question(section, index):
    if 'test_result_id' not in session:
        flash('Test session expired. Please start a new test.', 'danger')
        return redirect(url_for('test.test_instructions'))
    
    # Get questions for the current section
    all_questions = Question.query.filter_by(category=section).all()
    
    # Limit to only 15 questions per section
    questions = all_questions[:15] if len(all_questions) > 15 else all_questions
    
    # MODIFIED: If no questions are found, find next section with questions
    if not questions:
        test_sections = session.get('test_sections', ['orientation', 'interest', 'personality', 'aptitude', 'eq', 'work_style', 'interest_category'])
        
        # Find the next section with questions
        next_section = find_next_section_with_questions(section, test_sections)
        
        if next_section != section:
            # Update session variables
            session['current_section'] = next_section
            session['section_index'] = 0
            
            # Return HTMX response for next section
            return render_template('partials/question.html', 
                                  section=next_section,
                                  question={'content': f'Moving to {next_section.capitalize()} section...'},
                                  options=[],
                                  index=0,
                                  total=1,
                                  is_last=False,
                                  hx_redirect=url_for('test.section_question', section=next_section, index=0))
        
        # If we can't find any section with questions, show a placeholder
        return render_template('partials/question.html', 
                              section=section,
                              question={'content': f'No questions available for {section} section.'},
                              options=[],
                              index=index,
                              total=1,
                              is_last=True)
    
    # Check if we've reached the end of this section
    if index >= len(questions):
        # Move to the next section or finish the test
        test_sections = session.get('test_sections', ['orientation', 'interest', 'personality', 'aptitude', 'eq', 'work_style', 'interest_category'])
        current_section_index = test_sections.index(section)
        
        if current_section_index < len(test_sections) - 1:
            # MODIFIED: Find the next section with questions
            next_section = None
            for i in range(current_section_index + 1, len(test_sections)):
                if Question.query.filter_by(category=test_sections[i]).count() > 0:
                    next_section = test_sections[i]
                    break
            
            if not next_section:
                # No more sections with questions, finish the test
                session['current_section'] = test_sections[-1]
                # Add HX-Redirect header for HTMX to redirect client-side
                response = jsonify({'redirect': url_for('test.finish_test')})
                response.headers['HX-Redirect'] = url_for('test.finish_test')
                return response
            
            session['current_section'] = next_section
            session['section_index'] = 0
            
            # Return HTMX response for the next section's first question
            return render_template('partials/question.html', 
                                  section=next_section,
                                  question={'content': f'Moving to {next_section.capitalize()} section...'},
                                  options=[],
                                  index=0,
                                  total=1,
                                  is_last=False,
                                  hx_redirect=url_for('test.section_question', section=next_section, index=0))
        else:
            # End of all sections
            response = jsonify({'redirect': url_for('test.finish_test')})
            response.headers['HX-Redirect'] = url_for('test.finish_test')
            return response
    
    # Get the current question
    question = questions[index]
    options = QuestionOption.query.filter_by(question_id=question.id).all()
    
    # Handle form submission
    if request.method == 'POST':
        selected_option_id = request.form.get('option')
        
        if selected_option_id:
            # Save the answer
            answer = UserAnswer(
                test_result_id=session['test_result_id'],
                question_id=question.id,
                selected_option_id=selected_option_id
            )
            db.session.add(answer)
            db.session.commit()
            
            # Reset the warning flag
            session.pop('option_required_warned', None)
            
            # Update session index
            session['section_index'] = index + 1
            
            # Use HTMX to load the next question without a page refresh
            next_index = index + 1
            
            # If it's the last question in this section, handle section transition
            if next_index >= len(questions):
                test_sections = session.get('test_sections', ['orientation', 'interest', 'personality', 'aptitude', 'eq', 'work_style', 'interest_category'])
                current_section_index = test_sections.index(section)
                
                if current_section_index < len(test_sections) - 1:
                    next_section = None
                    for i in range(current_section_index + 1, len(test_sections)):
                        if Question.query.filter_by(category=test_sections[i]).count() > 0:
                            next_section = test_sections[i]
                            break
                    
                    if next_section:
                        session['current_section'] = next_section
                        session['section_index'] = 0
                        
                        # Add HX-Redirect header for HTMX to navigate
                        response = render_template('partials/question.html',
                                                 section=section,
                                                 question=question,
                                                 options=options,
                                                 index=index,
                                                 total=len(questions),
                                                 is_last=True)
                        headers = {'HX-Redirect': url_for('test.test_wizard') + f'?section={next_section}'}
                        return response, 200, headers
                    else:
                        # No more sections with questions
                        response = render_template('partials/question.html',
                                                 section=section,
                                                 question=question,
                                                 options=options,
                                                 index=index,
                                                 total=len(questions),
                                                 is_last=True)
                        headers = {'HX-Redirect': url_for('test.finish_test')}
                        return response, 200, headers
            
            # Return the next question with HTMX (FIXED: using render_template instead of redirect)
            next_question = questions[next_index]
            next_options = QuestionOption.query.filter_by(question_id=next_question.id).all()
            is_last_question = (next_index == len(questions) - 1)
            
            # Check if this is the last question of the last section
            test_sections = session.get('test_sections', ['orientation', 'interest', 'personality', 'aptitude', 'eq', 'work_style', 'interest_category'])
            current_section_index = test_sections.index(section)
            is_last_section = True
            
            # Check if there are more sections with questions after this one
            for i in range(current_section_index + 1, len(test_sections)):
                if Question.query.filter_by(category=test_sections[i]).count() > 0:
                    is_last_section = False
                    break
            
            return render_template('partials/question.html', 
                                  section=section,
                                  question=next_question,
                                  options=next_options,
                                  index=next_index,
                                  total=len(questions),
                                  progress_percent=(next_index / len(questions)) * 100 if len(questions) > 0 else 0,
                                  is_last=is_last_question,
                                  is_last_question=is_last_question,
                                  is_last_section=is_last_section)
        else:
            # Flash a warning message (only once)
            if 'option_required_warned' not in session or not session['option_required_warned']:
                flash('Please select an option to continue.', 'warning')
                session['option_required_warned'] = True
            
            # Return the same question without redirection
            return render_template('partials/question.html', 
                              section=section,
                              question=question,
                              options=options,
                              index=index,
                              total=len(questions),
                              progress_percent=(index / len(questions)) * 100 if len(questions) > 0 else 0,
                              is_last=(index == len(questions) - 1))

    # Calculate question progress
    total_questions = len(questions)
    progress_percent = (index / total_questions) * 100 if total_questions > 0 else 0
    is_last = (index == total_questions - 1)
    
    # Render the question
    return render_template('partials/question.html', 
                          section=section,
                          question=question,
                          options=options,
                          index=index,
                          total=total_questions,
                          progress_percent=progress_percent,
                          is_last=is_last)

@test_bp.route('/test/finish')
@login_required
def finish_test():
    """
    Finish the test and redirect to results
    """
    test_result_id = session.get('test_result_id', None)
    
    if not test_result_id:
        flash('No active test found. Please start a new test.', 'danger')
        return redirect(url_for('test.test_instructions'))
    
    # Calculate scores for the test
    test_result = calculate_scores(test_result_id)
    
    # Save the scores
    db.session.commit()
    
    # Clear the session data
    session.pop('test_result_id', None)
    session.pop('current_section', None)
    session.pop('section_index', None)
    session.pop('test_sections', None)
    session.pop('orientation_complete', None)
    session.pop('interest_complete', None)
    session.pop('personality_complete', None)
    session.pop('aptitude_complete', None)
    session.pop('eq_complete', None)
    session.pop('work_style_complete', None)
    session.pop('interest_category_complete', None)
    
    # Add a success message with instructions for the PDF report
    flash('Test completed successfully! You can now view your results and download a detailed PDF report.', 'success')
    
    # Check if this is an HTMX request
    if request.headers.get('HX-Request'):
        # Return a response with HX-Redirect
        response = jsonify({
            'success': True,
            'message': 'Test completed successfully!',
            'redirect': url_for('result.show_combined_result', test_result_id=test_result_id)
        })
        response.headers['HX-Redirect'] = url_for('result.show_combined_result', test_result_id=test_result_id)
        return response
    
    # Regular redirect for non-HTMX requests
    return redirect(url_for('result.show_combined_result', test_result_id=test_result_id)) 