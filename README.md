# NANY v0.1

**Decision-support tool for neurodivergent users**

NANY helps you decide what to do right now based on your cognitive tendencies, current environment, and stated goal. It optimizes for execution probability, not motivation.

## What NANY Does

1. **Collects a light cognitive profile** - 5 traits that affect how you start and sustain tasks
2. **Captures your current context** - time, energy, location, pressure
3. **Accepts your goal** - what you want to accomplish
4. **Generates ONE concrete action** - the smallest viable step you can take right now
5. **Records feedback** - whether you did it or not

## How to Run It

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# Navigate to project directory
cd /home/eyosimak37/Documents/nany

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running

```bash
# Start the server
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000 in your browser.

### API Documentation

FastAPI auto-generates docs at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users` | Create new user |
| GET | `/users/{id}` | Get user |
| POST | `/users/{id}/profile` | Save cognitive profile |
| GET | `/users/{id}/profile` | Get cognitive profile |
| POST | `/users/{id}/environment` | Save environment snapshot |
| POST | `/users/{id}/goal` | Save goal |
| GET | `/users/{id}/recommend` | Get recommendation |
| POST | `/users/{id}/feedback` | Record feedback |

## Recommendation Logic

The engine uses rule-based reasoning:

- **Friction minimization** - reduce barriers to starting
- **Energy matching** - match task difficulty to current energy
- **Continuation > initiation** - prefer continuing over starting new
- **Constraint dominance** - environment overrides ambition
- **Reversibility** - prefer actions that can be undone
- **When uncertain** - choose the smaller and safer action

## Known Limitations

1. **No authentication** - Uses simple user IDs stored in localStorage
2. **No persistence across browsers** - User data is tied to browser
3. **Rule-based only** - No ML/AI for personalization
4. **Limited goal parsing** - Pattern matches common goals (clean, study, work, etc.)
5. **Single action** - Only recommends one action at a time
6. **No history view** - Feedback is stored but not displayed to user

## What NANY Does NOT Do

- Act as a therapist, psychiatrist, doctor, or life coach
- Make medical or psychological diagnoses
- Mention brain chemistry or neurotransmitters
- Use motivational or emotional language
- Replace user agency

## Project Structure

```
nany/
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI routes
│   ├── models.py       # SQLAlchemy models
│   ├── schemas.py      # Pydantic schemas
│   ├── rules.py        # Recommendation engine
│   ├── database.py     # DB connection
│   └── crud.py         # CRUD operations
├── frontend/
│   ├── index.html      # Main page
│   ├── style.css       # Styling
│   └── app.js          # Frontend logic
├── requirements.txt
└── README.md
```

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic, SQLAlchemy
- **Database**: SQLite
- **Frontend**: Vanilla HTML/CSS/JS

## License

MIT
