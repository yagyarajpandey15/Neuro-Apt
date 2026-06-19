# Neuro Apt

AI-powered psychometric assessment platform for career guidance and personality analysis.

## Setup

### 1. Clone and Install

```bash
git clone <repo-url>
cd Neuro-Apt-main
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///neuroapt.db
OPENAI_API_KEY=your-openai-api-key
```

### 3. Database

```bash
flask db upgrade
```

### 4. Run

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Key Features

- Multi-section psychometric testing (orientation, interest, personality, aptitude, emotional quotient, work style)
- AI-powered career recommendations using OpenAI GPT-4o and GPT-4o-mini models
- Comprehensive personality profiling with Big Five traits analysis
- PDF report generation with detailed test results and career insights
- Admin dashboard for user management, question management, and test monitoring
- Career insights and recommendations based on test performance
- Authentication system with role-based access control (admin/regular users)

## Running Tests

```bash
# Run all tests
pytest neuroapt/tests/

# Run property-based tests only
pytest neuroapt/tests/ -k "property"

# Run with verbose output
pytest neuroapt/tests/ -v
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| SECRET_KEY | Yes | Flask secret key for session management |
| DATABASE_URL | No | Database connection string (defaults to sqlite:///neuroapt.db) |
| OPENAI_API_KEY | Yes | OpenAI API key for AI-powered career analysis and insights |
