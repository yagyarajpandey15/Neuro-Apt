from datetime import datetime
from flask_login import UserMixin
from neuroapt.app import db, login_manager
import json

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    test_results = db.relationship('TestResult', backref='user_account', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
        
    @property
    def full_name(self):
        """Return username as full_name since we don't have separate first and last name fields"""
        return self.username
        
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # 'orientation', 'interest', 'personality', 'aptitude', 'eq'
    content = db.Column(db.Text, nullable=False)
    is_high_diagnostic = db.Column(db.Boolean, default=False)  # Flag for questions with higher predictive value
    options = db.relationship('QuestionOption', backref='question', lazy=True)
    
    def __repr__(self):
        return f"Question('{self.id}', '{self.category}')"
        
    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'content': self.content,
            'is_high_diagnostic': self.is_high_diagnostic,
            'options': [option.to_dict() for option in self.options]
        }

class QuestionOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    score_value = db.Column(db.Integer, default=0)
    trait_impact = db.Column(db.String(100))  # Which personality trait this option impacts
    trait_value = db.Column(db.Integer, default=0)  # How much it impacts that trait
    
    def __repr__(self):
        return f"QuestionOption('{self.content}', correct={self.is_correct})"
        
    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'content': self.content,
            'is_correct': self.is_correct,
            'score_value': self.score_value,
            'trait_impact': self.trait_impact,
            'trait_value': self.trait_value
        }

class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_score = db.Column(db.Integer, default=0)
    
    # Basic test scores
    verbal_score = db.Column(db.Integer, default=0)
    numerical_score = db.Column(db.Integer, default=0)
    abstract_score = db.Column(db.Integer, default=0)
    orientation_score = db.Column(db.Integer, default=0)
    interest_score = db.Column(db.Integer, default=0)
    personality_score = db.Column(db.Integer, default=0)
    aptitude_score = db.Column(db.Integer, default=0)
    eq_score = db.Column(db.Integer, default=0)
    work_style_score = db.Column(db.Integer, default=0)
    
    # Personality trait scores
    openness_score = db.Column(db.Integer, default=0)
    conscientiousness_score = db.Column(db.Integer, default=0)
    extraversion_score = db.Column(db.Integer, default=0)
    agreeableness_score = db.Column(db.Integer, default=0)
    neuroticism_score = db.Column(db.Integer, default=0)
    
    # Work attribute scores
    leadership_score = db.Column(db.Integer, default=0)
    teamwork_score = db.Column(db.Integer, default=0)
    creativity_score = db.Column(db.Integer, default=0)
    analytical_score = db.Column(db.Integer, default=0)
    communication_score = db.Column(db.Integer, default=0)
    adaptability_score = db.Column(db.Integer, default=0)
    
    # Interest category scores
    stem_tech_score = db.Column(db.Integer, default=0)
    creative_media_score = db.Column(db.Integer, default=0)
    people_oriented_score = db.Column(db.Integer, default=0)
    business_management_score = db.Column(db.Integer, default=0)
    legal_governance_score = db.Column(db.Integer, default=0)
    logistics_distribution_score = db.Column(db.Integer, default=0)
    
    # AI-powered fields (Phase 1 additions)
    ai_analysis = db.Column(db.Text, nullable=True)  # Cached JSON from GPT-4o analysis
    confidence_level = db.Column(db.String(20), nullable=True)  # HIGH/MODERATE/LOW/UNRELIABLE
    answer_pattern_flag = db.Column(db.String(20), nullable=True)  # decisive/ambivalent/random
    contradictions_detected = db.Column(db.Text, nullable=True)  # JSON list of detected contradictions
    interest_intersection = db.Column(db.String(50), nullable=True)  # e.g., "STEM+Creative"
    
    # Answer patterns for career matching
    _answer_patterns = db.Column('answer_patterns', db.Text, default='{}')
    
    # Define relationships
    answers = db.relationship('UserAnswer', backref='test_result', lazy=True)
    retake_history = db.relationship('TestRetakeHistory', backref='test_result', lazy=True)
    
    # Access the user through the user_account backref defined in User class
    
    @property
    def answer_patterns(self):
        """Get the answer patterns as a dictionary"""
        try:
            return json.loads(self._answer_patterns)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @answer_patterns.setter
    def answer_patterns(self, value):
        """Set the answer patterns from a dictionary"""
        if isinstance(value, dict):
            self._answer_patterns = json.dumps(value)
        else:
            self._answer_patterns = '{}'
    
    @property
    def ai_analysis_dict(self):
        """Get AI analysis as dictionary"""
        if not self.ai_analysis:
            return None
        try:
            return json.loads(self.ai_analysis)
        except (json.JSONDecodeError, TypeError):
            return None
    
    @ai_analysis_dict.setter
    def ai_analysis_dict(self, value):
        """Set AI analysis from dictionary"""
        if value is None:
            self.ai_analysis = None
        elif isinstance(value, dict):
            self.ai_analysis = json.dumps(value)
        else:
            self.ai_analysis = str(value)
    
    @property
    def contradictions_list(self):
        """Get contradictions as list"""
        if not self.contradictions_detected:
            return []
        try:
            return json.loads(self.contradictions_detected)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @contradictions_list.setter
    def contradictions_list(self, value):
        """Set contradictions from list"""
        if value is None or value == []:
            self.contradictions_detected = None
        elif isinstance(value, list):
            self.contradictions_detected = json.dumps(value)
        else:
            self.contradictions_detected = str(value)
    
    def get_ai_analysis_dict(self):
        """Get AI analysis as dictionary (compatibility method)"""
        return self.ai_analysis_dict
    
    def set_ai_analysis_dict(self, value):
        """Set AI analysis from dictionary (compatibility method)"""
        self.ai_analysis_dict = value
    
    def get_top_categories(self, limit=2):
        """Get the top interest categories based on scores"""
        categories = [
            ('stem_tech', self.stem_tech_score),
            ('creative_media', self.creative_media_score),
            ('people_oriented', self.people_oriented_score),
            ('business_management', self.business_management_score),
            ('legal_governance', self.legal_governance_score),
            ('logistics_distribution', self.logistics_distribution_score)
        ]
        return sorted(categories, key=lambda x: x[1], reverse=True)[:limit]
    
    def get_career_recommendations(self):
        """Get career recommendations based on interest categories and answer patterns"""
        from .utils.scoring import get_interest_category_descriptions
        
        top_categories = self.get_top_categories()
        interest_descriptions = get_interest_category_descriptions()
        
        recommendations = []
        for category, score in top_categories:
            if category in interest_descriptions:
                recommendations.extend(interest_descriptions[category]['careers'])
        
        # Remove duplicates while preserving order
        seen = set()
        return [x for x in recommendations if not (x in seen or seen.add(x))]

    def __repr__(self):
        return f"TestResult(User: {self.user_id}, Total: {self.total_score})"
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'test_date': self.test_date.strftime('%Y-%m-%d %H:%M:%S') if self.test_date else None,
            'orientation_score': self.orientation_score,
            'interest_score': self.interest_score,
            'personality_score': self.personality_score,
            'aptitude_score': self.aptitude_score,
            'eq_score': self.eq_score,
            'total_score': self.total_score,
            'openness_score': self.openness_score,
            'conscientiousness_score': self.conscientiousness_score,
            'extraversion_score': self.extraversion_score,
            'agreeableness_score': self.agreeableness_score,
            'neuroticism_score': self.neuroticism_score,
            'leadership_score': self.leadership_score,
            'teamwork_score': self.teamwork_score,
            'creativity_score': self.creativity_score,
            'analytical_score': self.analytical_score,
            'communication_score': self.communication_score,
            'adaptability_score': self.adaptability_score,
            'verbal_score': self.verbal_score,
            'numerical_score': self.numerical_score,
            'abstract_score': self.abstract_score,
            'work_style_score': self.work_style_score,
            'stem_tech_score': self.stem_tech_score,
            'creative_media_score': self.creative_media_score,
            'people_oriented_score': self.people_oriented_score,
            'business_management_score': self.business_management_score,
            'legal_governance_score': self.legal_governance_score,
            'logistics_distribution_score': self.logistics_distribution_score,
            'answer_patterns': self.answer_patterns,
            'answers': [answer.to_dict() for answer in self.answers]
        }

class UserAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey('test_result.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('question_option.id'), nullable=False)
    
    question = db.relationship('Question')
    selected_option = db.relationship('QuestionOption')
    
    def __repr__(self):
        return f"UserAnswer(Question: {self.question_id}, Answer: {self.selected_option_id})"
        
    def to_dict(self):
        return {
            'id': self.id,
            'test_result_id': self.test_result_id,
            'question_id': self.question_id,
            'selected_option_id': self.selected_option_id
        }

class Career(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    work_environment = db.Column(db.Text)
    job_outlook = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skills = db.relationship('CareerSkill', backref='career', lazy=True, cascade="all, delete-orphan")
    education_paths = db.relationship('CareerEducation', backref='career', lazy=True, cascade="all, delete-orphan")
    salary_info = db.relationship('CareerSalary', backref='career', lazy=True, cascade="all, delete-orphan", uselist=False)
    
    def __repr__(self):
        return f"Career('{self.title}', '{self.category}')"
        
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'work_environment': self.work_environment,
            'job_outlook': self.job_outlook,
            'skills': [skill.to_dict() for skill in self.skills],
            'education_paths': [edu.to_dict() for edu in self.education_paths],
            'salary_info': self.salary_info.to_dict() if self.salary_info else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class CareerSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey('career.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f"CareerSkill('{self.name}')"
        
    def to_dict(self):
        return {
            'id': self.id,
            'career_id': self.career_id,
            'name': self.name,
            'description': self.description
        }

class CareerEducation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey('career.id'), nullable=False)
    level = db.Column(db.String(100), nullable=False)
    field = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f"CareerEducation('{self.level}', '{self.field}')"
        
    def to_dict(self):
        return {
            'id': self.id,
            'career_id': self.career_id,
            'level': self.level,
            'field': self.field,
            'description': self.description
        }

class CareerSalary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey('career.id'), nullable=False)
    entry_level = db.Column(db.String(50))
    mid_level = db.Column(db.String(50))
    senior_level = db.Column(db.String(50))
    currency = db.Column(db.String(10), default="USD")
    
    def __repr__(self):
        return f"CareerSalary(Entry: {self.entry_level}, Mid: {self.mid_level}, Senior: {self.senior_level})"
        
    def to_dict(self):
        return {
            'id': self.id,
            'career_id': self.career_id,
            'entry_level': self.entry_level,
            'mid_level': self.mid_level,
            'senior_level': self.senior_level,
            'currency': self.currency
        } 


# ============================================================================
# NEW AI-POWERED MODELS (Phase 1)
# ============================================================================

class TestRetakeHistory(db.Model):
    """Track when users retake tests to analyze growth over time"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    result_id = db.Column(db.Integer, db.ForeignKey('test_result.id'), nullable=False)
    retake_number = db.Column(db.Integer, nullable=False)  # 1, 2, 3, etc.
    taken_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    _score_snapshot = db.Column('score_snapshot', db.Text)  # JSON snapshot of all scores
    
    # Relationships
    user = db.relationship('User', backref='retake_history')
    
    @property
    def score_snapshot(self):
        """Get score snapshot as dictionary"""
        if not self._score_snapshot:
            return {}
        try:
            return json.loads(self._score_snapshot)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @score_snapshot.setter
    def score_snapshot(self, value):
        """Set score snapshot from dictionary"""
        if isinstance(value, dict):
            self._score_snapshot = json.dumps(value)
        else:
            self._score_snapshot = '{}'
    
    def __repr__(self):
        return f"TestRetakeHistory(User: {self.user_id}, Attempt: {self.retake_number})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'result_id': self.result_id,
            'retake_number': self.retake_number,
            'taken_at': self.taken_at.strftime('%Y-%m-%d %H:%M:%S') if self.taken_at else None,
            'score_snapshot': self.score_snapshot
        }

class MicroAssessment(db.Model):
    """Pre-built focused assessments for comparing two specific careers"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    career_a = db.Column(db.String(100), nullable=False)
    career_b = db.Column(db.String(100), nullable=False)
    _questions = db.Column('questions', db.Text, nullable=False)  # JSON array of questions
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    results = db.relationship('MicroAssessmentResult', backref='assessment', lazy=True)
    
    @property
    def questions(self):
        """Get questions as list"""
        if not self._questions:
            return []
        try:
            return json.loads(self._questions)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @questions.setter
    def questions(self, value):
        """Set questions from list"""
        if isinstance(value, list):
            self._questions = json.dumps(value)
        else:
            self._questions = '[]'
    
    def __repr__(self):
        return f"MicroAssessment('{self.title}': {self.career_a} vs {self.career_b})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'career_a': self.career_a,
            'career_b': self.career_b,
            'questions': self.questions,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class MicroAssessmentResult(db.Model):
    """Store individual user results from micro assessments"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('micro_assessment.id'), nullable=False)
    _answers = db.Column('answers', db.Text)  # JSON of user answers
    _ai_result = db.Column('ai_result', db.Text)  # Cached AI analysis JSON
    taken_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='micro_assessment_results')
    
    @property
    def answers(self):
        """Get answers as dictionary"""
        if not self._answers:
            return {}
        try:
            return json.loads(self._answers)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @answers.setter
    def answers(self, value):
        """Set answers from dictionary"""
        if isinstance(value, dict):
            self._answers = json.dumps(value)
        else:
            self._answers = '{}'
    
    @property
    def ai_result(self):
        """Get AI result as dictionary"""
        if not self._ai_result:
            return None
        try:
            return json.loads(self._ai_result)
        except (json.JSONDecodeError, TypeError):
            return None
    
    @ai_result.setter
    def ai_result(self, value):
        """Set AI result from dictionary"""
        if value is None:
            self._ai_result = None
        elif isinstance(value, dict):
            self._ai_result = json.dumps(value)
        else:
            self._ai_result = str(value)
    
    def __repr__(self):
        return f"MicroAssessmentResult(User: {self.user_id}, Assessment: {self.assessment_id})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'assessment_id': self.assessment_id,
            'answers': self.answers,
            'ai_result': self.ai_result,
            'taken_at': self.taken_at.strftime('%Y-%m-%d %H:%M:%S') if self.taken_at else None
        }
