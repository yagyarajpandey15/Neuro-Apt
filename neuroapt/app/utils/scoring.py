from neuroapt.app.models import UserAnswer, Question, QuestionOption, TestResult
import json
from neuroapt.app import db
from neuroapt.app.utils.interest_scoring import calculate_interest_category_scores
from neuroapt.app.utils.orientation_scoring import calculate_orientation_scores, get_orientation_styles
import statistics

def calculate_scores(test_result_id):
    """
    UPGRADED: Calculate scores with advanced pattern analysis, consistency checking, and confidence scoring
    
    Args:
        test_result_id: ID of the test result to calculate scores for
    
    Returns:
        Updated TestResult object with AI-ready metadata
    """
    test_result = TestResult.query.get(test_result_id)
    if not test_result:
        return None
    
    # Initialize scores
    orientation_score = 0
    interest_score = 0
    personality_score = 0
    aptitude_score = 0
    eq_score = 0
    work_style_score = 0
    
    # Initialize trait scores for personality
    openness_score = 0
    conscientiousness_score = 0
    extraversion_score = 0
    agreeableness_score = 0
    neuroticism_score = 0
    
    # Initialize work attribute scores
    leadership_score = 0
    teamwork_score = 0
    creativity_score = 0
    analytical_score = 0
    communication_score = 0
    adaptability_score = 0
    
    # NEW: Initialize EQ component scores (direct measurement)
    eq_empathy_score = 0
    eq_self_awareness_score = 0
    eq_social_skills_score = 0
    eq_emotional_regulation_score = 0
    
    # Initialize interest category scores
    stem_tech_score = 0
    creative_media_score = 0
    people_oriented_score = 0
    business_management_score = 0
    legal_governance_score = 0
    logistics_distribution_score = 0
    
    # NEW: Pattern detection tracking
    answer_values_by_section = {
        'orientation': [],
        'interest': [],
        'personality': [],
        'aptitude': [],
        'eq': [],
        'work_style': []
    }
    
    # Get all user answers for this test
    user_answers = UserAnswer.query.filter_by(test_result_id=test_result_id).all()
    
    if not user_answers:
        return test_result
    
    # Calculate scores based on user answers WITH DIFFERENTIAL WEIGHTING
    verbal_score = 0
    numerical_score = 0
    abstract_score = 0
    
    for answer in user_answers:
        question = Question.query.get(answer.question_id)
        selected_option = QuestionOption.query.get(answer.selected_option_id)
        
        # NEW: Apply differential weighting based on question diagnostic value
        weight = 1.5 if question.is_high_diagnostic else (0.8 if not question.is_high_diagnostic else 1.0)
        weighted_score = selected_option.score_value * weight
        
        # Track answer values for pattern analysis
        if question.category in answer_values_by_section:
            answer_values_by_section[question.category].append(selected_option.score_value)
        
        # Add the weighted score to the appropriate category
        if question.category == 'verbal':
            verbal_score += weighted_score
        elif question.category == 'numerical':
            numerical_score += weighted_score
        elif question.category == 'abstract':
            abstract_score += weighted_score
        elif question.category == 'orientation':
            orientation_score += weighted_score
        elif question.category == 'interest':
            interest_score += weighted_score
        elif question.category == 'personality':
            personality_score += weighted_score
        elif question.category == 'aptitude':
            aptitude_score += weighted_score
        elif question.category == 'eq':
            eq_score += weighted_score
            
            # NEW: Direct EQ component measurement from EQ section
            # Map specific traits from EQ questions directly
            if selected_option.trait_impact:
                trait_name = selected_option.trait_impact.lower()
                trait_value = selected_option.trait_value
                
                if 'empathy' in trait_name:
                    eq_empathy_score += trait_value
                elif 'self_awareness' in trait_name or 'awareness' in trait_name:
                    eq_self_awareness_score += trait_value
                elif 'social' in trait_name:
                    eq_social_skills_score += trait_value
                elif 'regulation' in trait_name or 'emotional' in trait_name:
                    eq_emotional_regulation_score += trait_value
                    
        elif question.category == 'work_style':
            work_style_score += weighted_score
        
        # Process personality traits and work attributes
        if selected_option.trait_impact:
            trait_name = selected_option.trait_impact.lower()
            trait_value = selected_option.trait_value
            
            # Update personality trait scores
            if trait_name == 'openness':
                openness_score += trait_value
            elif trait_name == 'conscientiousness':
                conscientiousness_score += trait_value
            elif trait_name == 'extraversion':
                extraversion_score += trait_value
            elif trait_name == 'agreeableness':
                agreeableness_score += trait_value
            elif trait_name == 'neuroticism':
                neuroticism_score += trait_value
                
            # Update work attribute scores
            elif trait_name == 'leadership':
                leadership_score += trait_value
            elif trait_name == 'teamwork':
                teamwork_score += trait_value
            elif trait_name == 'creativity':
                creativity_score += trait_value
            elif trait_name == 'analytical':
                analytical_score += trait_value
            elif trait_name == 'communication':
                communication_score += trait_value
            elif trait_name == 'adaptability':
                adaptability_score += trait_value
    
    # Update test result scores
    test_result.orientation_score = int(orientation_score)
    test_result.interest_score = int(interest_score)
    test_result.personality_score = int(personality_score)
    test_result.aptitude_score = int(aptitude_score)
    test_result.eq_score = int(eq_score)
    test_result.work_style_score = int(work_style_score)
    
    # Update aptitude scores
    test_result.verbal_score = int(verbal_score)
    test_result.numerical_score = int(numerical_score)
    test_result.abstract_score = int(abstract_score)
    
    # Update personality trait scores
    test_result.openness_score = openness_score
    test_result.conscientiousness_score = conscientiousness_score
    test_result.extraversion_score = extraversion_score
    test_result.agreeableness_score = agreeableness_score
    test_result.neuroticism_score = neuroticism_score
    
    # Update work attribute scores
    test_result.leadership_score = leadership_score
    test_result.teamwork_score = teamwork_score
    test_result.creativity_score = creativity_score
    test_result.analytical_score = analytical_score
    test_result.communication_score = communication_score
    test_result.adaptability_score = adaptability_score
    
    # IMPORTANT: Use the dedicated functions for specialized scoring
    calculate_interest_category_scores(test_result_id)
    calculate_orientation_scores(test_result_id)
    
    # Reload to get updated interest scores
    db.session.refresh(test_result)
    
    # NEW: Detect interest domain intersection (top 2 domains)
    interest_domains = [
        ('STEM', test_result.stem_tech_score),
        ('Creative', test_result.creative_media_score),
        ('People', test_result.people_oriented_score),
        ('Business', test_result.business_management_score),
        ('Legal', test_result.legal_governance_score),
        ('Logistics', test_result.logistics_distribution_score)
    ]
    top_two = sorted(interest_domains, key=lambda x: x[1], reverse=True)[:2]
    test_result.interest_intersection = f"{top_two[0][0]}+{top_two[1][0]}"
    
    # NEW: Analyze answer patterns
    pattern_flag = detect_answer_pattern(answer_values_by_section)
    test_result.answer_pattern_flag = pattern_flag
    
    # NEW: Check cross-section consistency
    contradictions = check_consistency(test_result)
    test_result.contradictions_list = contradictions
    
    # NEW: Calculate confidence level
    confidence = calculate_confidence_level(
        test_result,
        answer_values_by_section,
        pattern_flag,
        contradictions
    )
    test_result.confidence_level = confidence
    
    # Calculate total score
    test_result.total_score = sum([
        int(verbal_score), int(numerical_score), int(abstract_score),
        int(orientation_score), int(interest_score), int(personality_score),
        int(aptitude_score), int(eq_score), int(work_style_score)
    ])
    
    db.session.commit()
    
    return test_result

def detect_answer_pattern(answer_values_by_section):
    """
    NEW: Detect if user consistently picks extreme, middle, or random options
    
    Returns: 'decisive', 'ambivalent', or 'random'
    """
    all_values = []
    for section_values in answer_values_by_section.values():
        all_values.extend(section_values)
    
    if not all_values:
        return 'unknown'
    
    # Normalize values to 0-1 scale
    max_val = max(all_values) if max(all_values) > 0 else 1
    normalized = [v / max_val for v in all_values]
    
    # Count extreme (0-0.3 or 0.7-1.0) vs middle (0.3-0.7) choices
    extreme_count = sum(1 for v in normalized if v < 0.3 or v > 0.7)
    middle_count = sum(1 for v in normalized if 0.3 <= v <= 0.7)
    
    extreme_ratio = extreme_count / len(normalized)
    middle_ratio = middle_count / len(normalized)
    
    # Calculate variance (low variance = consistent pattern)
    variance = statistics.variance(normalized) if len(normalized) > 1 else 0
    
    # Decision logic
    if extreme_ratio > 0.7:  # Mostly extreme choices
        return 'decisive'
    elif middle_ratio > 0.7:  # Mostly middle choices
        return 'ambivalent'
    elif variance < 0.1:  # Very low variance (picking same option repeatedly)
        return 'random'  # Likely not reading questions
    else:
        return 'balanced'

def check_consistency(test_result):
    """
    NEW: Check for contradictions across sections
    
    Returns: List of detected contradictions
    """
    contradictions = []
    
    # Check 1: High people-oriented interest vs low extraversion
    if test_result.people_oriented_score > 70 and test_result.extraversion_score < 20:
        contradictions.append({
            'type': 'interest_personality_mismatch',
            'description': 'High people-oriented interest but low extraversion scores',
            'sections': ['interest', 'personality']
        })
    
    # Check 2: High analytical interest but low conscientiousness
    if test_result.stem_tech_score > 70 and test_result.conscientiousness_score < 20:
        contradictions.append({
            'type': 'interest_trait_mismatch',
            'description': 'High STEM interest but low conscientiousness (needed for technical work)',
            'sections': ['interest', 'personality']
        })
    
    # Check 3: High leadership work style but low extraversion
    if test_result.leadership_score > 30 and test_result.extraversion_score < 15:
        contradictions.append({
            'type': 'workstyle_personality_mismatch',
            'description': 'High leadership tendency but low extraversion',
            'sections': ['work_style', 'personality']
        })
    
    # Check 4: High creative interest but low openness
    if test_result.creative_media_score > 70 and test_result.openness_score < 20:
        contradictions.append({
            'type': 'interest_personality_mismatch',
            'description': 'High creative interest but low openness to experience',
            'sections': ['interest', 'personality']
        })
    
    # Check 5: High teamwork but low agreeableness
    if test_result.teamwork_score > 30 and test_result.agreeableness_score < 15:
        contradictions.append({
            'type': 'workstyle_personality_mismatch',
            'description': 'High teamwork preference but low agreeableness',
            'sections': ['work_style', 'personality']
        })
    
    return contradictions

def calculate_confidence_level(test_result, answer_values, pattern_flag, contradictions):
    """
    NEW: Calculate overall confidence level in the results
    
    Returns: 'HIGH', 'MODERATE', 'LOW', or 'UNRELIABLE'
    """
    confidence_factors = []
    
    # Factor 1: Answer pattern (30% weight)
    if pattern_flag == 'random':
        confidence_factors.append(0)  # Very low confidence
    elif pattern_flag == 'ambivalent':
        confidence_factors.append(0.5)  # Moderate confidence
    elif pattern_flag == 'decisive' or pattern_flag == 'balanced':
        confidence_factors.append(1.0)  # High confidence
    else:
        confidence_factors.append(0.7)  # Default moderate-high
    
    # Factor 2: Number of contradictions (30% weight)
    contradiction_penalty = min(len(contradictions) * 0.2, 1.0)
    confidence_factors.append(1.0 - contradiction_penalty)
    
    # Factor 3: Score distribution - are scores at decision boundaries? (20% weight)
    # Scores near thresholds (50, 70) indicate less certainty
    boundary_scores = 0
    total_scores = 6  # 6 main sections
    
    for score in [test_result.orientation_score, test_result.interest_score,
                  test_result.personality_score, test_result.aptitude_score,
                  test_result.eq_score, test_result.work_style_score]:
        # Check if within 10 points of common boundaries
        if abs(score - 50) < 10 or abs(score - 70) < 10:
            boundary_scores += 1
    
    boundary_ratio = boundary_scores / total_scores
    confidence_factors.append(1.0 - boundary_ratio)
    
    # Factor 4: Answer completeness (20% weight)
    # Check if all major sections have answers
    completeness_score = 0
    section_counts = {}
    for section, values in answer_values.items():
        section_counts[section] = len(values)
        if len(values) >= 10:  # At least 10 questions answered
            completeness_score += 1
    
    completeness_ratio = completeness_score / len(answer_values)
    confidence_factors.append(completeness_ratio)
    
    # Calculate weighted average
    weights = [0.30, 0.30, 0.20, 0.20]
    overall_confidence = sum(f * w for f, w in zip(confidence_factors, weights))
    
    # Map to confidence levels
    if overall_confidence >= 0.80:
        return 'HIGH'
    elif overall_confidence >= 0.60:
        return 'MODERATE'
    elif overall_confidence >= 0.40:
        return 'LOW'
    else:
        return 'UNRELIABLE'

def get_percentile(score, category=None):
    """
    Calculate the percentile of a score compared to all other test takers
    If category is provided, only compare within that category
    """
    if category:
        all_scores = TestResult.query.with_entities(
            getattr(TestResult, f"{category}_score")
        ).all()
        all_scores = [score[0] for score in all_scores]
    else:
        all_scores = TestResult.query.with_entities(TestResult.total_score).all()
        all_scores = [score[0] for score in all_scores]
    
    if not all_scores:
        return 0
    
    # Calculate percentile
    below_count = sum(1 for s in all_scores if s < score)
    equal_count = sum(1 for s in all_scores if s == score)
    
    # Use the standard percentile formula
    percentile = (below_count + 0.5 * equal_count) / len(all_scores) * 100
    
    return round(percentile, 1)

def get_trait_descriptions():
    """
    Get descriptions for personality traits and work attributes
    """
    return {
        'openness': {
            'title': 'Openness to Experience',
            'description': 'Reflects curiosity, creativity, and preference for variety and novelty.',
            'high': 'You are curious, imaginative, and open to new ideas and experiences.',
            'low': 'You prefer routine, practicality, and traditional approaches.'
        },
        'conscientiousness': {
            'title': 'Conscientiousness',
            'description': 'Reflects organization, responsibility, and goal-directed behavior.',
            'high': 'You are organized, reliable, and methodical in your approach to tasks.',
            'low': 'You are more flexible, spontaneous, and may prefer less structure.'
        },
        'extraversion': {
            'title': 'Extraversion',
            'description': 'Reflects sociability, assertiveness, and emotional expressiveness.',
            'high': 'You are outgoing, energetic, and draw energy from social interactions.',
            'low': 'You are more reserved, reflective, and may prefer solitary activities.'
        },
        'agreeableness': {
            'title': 'Agreeableness',
            'description': 'Reflects cooperation, compassion, and concern for social harmony.',
            'high': 'You are cooperative, empathetic, and prioritize getting along with others.',
            'low': 'You are more independent, competitive, and may prioritize self-interest.'
        },
        'neuroticism': {
            'title': 'Emotional Stability',
            'description': 'Reflects emotional regulation, resilience, and response to stress.',
            'high': 'You are more sensitive to stress and may experience stronger emotional reactions.',
            'low': 'You are emotionally stable, calm under pressure, and resilient to stress.'
        },
        'leadership': {
            'title': 'Leadership',
            'description': 'Reflects ability to guide, motivate, and influence others.',
            'high': 'You have strong leadership qualities and naturally take charge in group settings.',
            'low': 'You may prefer supporting roles rather than directing others.'
        },
        'teamwork': {
            'title': 'Teamwork',
            'description': 'Reflects ability to collaborate and work effectively in groups.',
            'high': 'You excel in collaborative environments and contribute positively to team dynamics.',
            'low': 'You may prefer working independently or in smaller groups.'
        },
        'creativity': {
            'title': 'Creativity',
            'description': 'Reflects innovative thinking and ability to generate novel ideas.',
            'high': 'You think outside the box and often come up with innovative solutions.',
            'low': 'You may prefer structured approaches and established methods.'
        },
        'analytical': {
            'title': 'Analytical Thinking',
            'description': 'Reflects logical reasoning and systematic problem-solving.',
            'high': 'You excel at logical analysis and breaking down complex problems.',
            'low': 'You may rely more on intuition or holistic approaches to problems.'
        },
        'communication': {
            'title': 'Communication',
            'description': 'Reflects ability to express ideas clearly and effectively.',
            'high': 'You communicate clearly and effectively across different contexts.',
            'low': 'You may prefer expressing yourself in more specific or limited contexts.'
        },
        'adaptability': {
            'title': 'Adaptability',
            'description': 'Reflects flexibility and ability to adjust to changing circumstances.',
            'high': 'You adapt quickly to new situations and embrace change.',
            'low': 'You may prefer stability and consistent environments.'
        }
    }

def get_interest_category_descriptions():
    """
    Get descriptions for interest categories with enhanced career matching
    """
    return {
        'stem_tech': {
            'title': 'STEM & Tech',
            'description': 'You have a strong aptitude for science, technology, engineering, and mathematics. You enjoy solving complex problems and working with cutting-edge technology.',
            'careers': [
                'Software Engineer',
                'Data Scientist',
                'Robotics Developer',
                'AI Researcher',
                'Network Engineer',
                'Cybersecurity Analyst',
                'Biomedical Engineer',
                'Quantum Computing Researcher',
                'Systems Architect',
                'Machine Learning Engineer'
            ],
            'skills': [
                'Problem-solving',
                'Analytical thinking',
                'Technical expertise',
                'Mathematical reasoning',
                'Programming',
                'Data analysis',
                'System design',
                'Research methodology'
            ]
        },
        'creative_media': {
            'title': 'Creative & Media',
            'description': 'You have a natural flair for creativity and expression. You enjoy bringing ideas to life through various forms of media and artistic expression.',
            'careers': [
                'Graphic Designer',
                'Content Creator',
                'Filmmaker',
                'UI/UX Designer',
                'Animator',
                'Digital Artist',
                'Creative Director',
                'Social Media Manager',
                'Game Designer',
                'Art Director'
            ],
            'skills': [
                'Visual thinking',
                'Creativity',
                'Storytelling',
                'Design skills',
                'Digital media',
                'Visual communication',
                'Brand development',
                'Content strategy'
            ]
        },
        'people_oriented': {
            'title': 'People-Oriented',
            'description': 'You excel at working with and helping others. You have strong interpersonal skills and enjoy making a positive impact on people\'s lives.',
            'careers': [
                'Teacher',
                'Psychologist',
                'HR Manager',
                'Social Worker',
                'Healthcare Professional',
                'Counselor',
                'Life Coach',
                'Community Manager',
                'Customer Success Manager',
                'Public Relations Specialist'
            ],
            'skills': [
                'Empathy',
                'Communication',
                'Interpersonal skills',
                'Active listening',
                'Conflict resolution',
                'Team building',
                'Emotional intelligence',
                'Mentoring'
            ]
        },
        'business_management': {
            'title': 'Business & Management',
            'description': 'You have a strong business acumen and leadership potential. You enjoy strategic thinking and driving organizational success.',
            'careers': [
                'Marketing Manager',
                'Financial Analyst',
                'Entrepreneur',
                'Business Consultant',
                'Sales Executive',
                'Project Manager',
                'Business Development Manager',
                'Operations Manager',
                'Strategy Consultant',
                'Product Manager'
            ],
            'skills': [
                'Leadership',
                'Strategic thinking',
                'Financial acumen',
                'Negotiation',
                'Project management',
                'Business analysis',
                'Market research',
                'Decision making'
            ]
        },
        'legal_governance': {
            'title': 'Legal & Governance',
            'description': 'You have a strong sense of justice and enjoy working with rules and regulations. You excel at critical analysis and ethical decision-making.',
            'careers': [
                'Lawyer',
                'Civil Servant',
                'Policy Advisor',
                'Compliance Officer',
                'Defense Personnel',
                'Legal Consultant',
                'Regulatory Affairs Manager',
                'Corporate Counsel',
                'Human Rights Advocate',
                'Government Relations Specialist'
            ],
            'skills': [
                'Critical thinking',
                'Attention to detail',
                'Regulatory knowledge',
                'Ethical reasoning',
                'Legal analysis',
                'Policy development',
                'Risk assessment',
                'Compliance management'
            ]
        },
        'logistics_distribution': {
            'title': 'Logistics & Distribution',
            'description': 'You excel at organizing and optimizing processes. You enjoy ensuring smooth operations and efficient resource management.',
            'careers': [
                'Supply Chain Manager',
                'Operations Executive',
                'Logistics Coordinator',
                'Inventory Manager',
                'Fleet Manager',
                'Procurement Specialist',
                'Distribution Manager',
                'Transportation Manager',
                'Warehouse Operations Manager',
                'Supply Chain Analyst'
            ],
            'skills': [
                'Organization',
                'Process optimization',
                'Resource management',
                'Coordination',
                'Supply chain management',
                'Inventory control',
                'Transportation planning',
                'Quality assurance'
            ]
        }
    }

def get_orientation_style(test_result_id):
    """
    Get the dominant orientation style and all style scores from a test result
    
    Args:
        test_result_id: ID of the TestResult to get orientation style for
        
    Returns:
        Dictionary containing orientation style information
    """
    test_result = TestResult.query.get_or_404(test_result_id)
    return get_orientation_styles(test_result) 