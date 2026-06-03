# AI Job Agent

AI-powered job search assistant built using FastAPI, Streamlit, SQLite, and Ollama.

## Overview

AI Job Agent helps job seekers analyze resumes, discover startup opportunities from Y Combinator's startup job board, rank opportunities based on profile fit, and track jobs through a persistent dashboard.

## Features

### Resume Analysis
- Upload PDF resumes
- AI-powered resume evaluation using Ollama
- Match score generation
- Strengths identification
- Missing skills detection

### Real YC Startup Jobs
- Fetches live jobs from Y Combinator's startup job board
- Role-based filtering
- Experience-based filtering
- Salary visibility
- Direct application links

### Job Ranking
- Matches jobs against candidate profiles
- Ranks opportunities by fit score

### Saved Jobs Dashboard
- Automatically stores discovered jobs
- SQLite-backed persistence
- Track discovered opportunities

### Web Interface
- Streamlit frontend
- FastAPI backend
- Interactive dashboard

---

## Tech Stack

### Frontend
- Streamlit

### Backend
- FastAPI

### Database
- SQLite

### AI Layer
- Ollama
- Phi-3 Mini

### Data Processing
- PyMuPDF
- Requests
- BeautifulSoup

---

## Architecture

```text
Resume Upload
      │
      ▼
 Streamlit UI
      │
      ▼
 FastAPI Backend
      │
      ▼
 Career Agent
      │
      ├── Resume Analysis (Ollama)
      │
      ├── YC Job Search
      │
      └── Job Ranking
      │
      ▼
 SQLite Database
```

---

## Project Structure

```text
AI-Job-Agent/
│
├── agents/
│   ├── career_tools.py
│   └── yc_jobs.py
│
├── database/
│   └── db.py
│
├── main.py
├── streamlit_app.py
├── requirements.txt
└── README.md
```

---

## Setup

### Clone Repository

```bash
git clone https://github.com/pratikshabhadani/AI-Job-Agent.git
cd AI-Job-Agent
```

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Ollama

```bash
ollama pull phi3:mini
```

### Start Backend

```bash
uvicorn main:app --reload
```

### Start Frontend

```bash
streamlit run streamlit_app.py
```

---

## Example Workflow

1. Upload Resume
2. Enter Target Role
3. Select Experience Level
4. Run Job Search
5. View Resume Analysis
6. Discover YC Startup Jobs
7. Save Opportunities
8. Track Jobs Through Dashboard

---

## Future Roadmap

- LinkedIn Job Search
- Alumni Discovery
- Referral Tracking
- Outreach Management
- Connection Tracking
- Follow-up Automation
- Multi-source Job Aggregation

---

## Author

Pratiksha Bhadani

GitHub:
https://github.com/pratikshabhadani
