# AI Job Agent

AI-powered job search assistant built using FastAPI, Streamlit, SQLite, and Ollama.

## Features

- Resume Upload
- AI Resume Analysis
- Job Matching
- Job Ranking
- Saved Jobs Dashboard
- Referral Message Generation

## Tech Stack

- Python
- FastAPI
- Streamlit
- SQLite
- Ollama
- PyMuPDF

## Architecture

Streamlit UI
↓
FastAPI Backend
↓
Career Agent Layer
↓
Ollama LLM
↓
SQLite Database

## Setup

Clone repository:

```bash
git clone https://github.com/pratikshabhadani/AI-Job-Agent.git
cd AI-Job-Agent
```

Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn main:app --reload
```

Start Streamlit:

```bash
streamlit run streamlit_app.py
```

## Future Roadmap

- Real YC Job Search
- LinkedIn Job Search
- Connection Discovery
- Referral CRM
- Follow-up Tracking
- AI Outreach Assistant
