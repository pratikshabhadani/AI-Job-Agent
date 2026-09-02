# AI Job Agent

AI-powered job search and career analysis assistant built with **FastAPI, Streamlit, SQLite, PyMuPDF, and Ollama/Phi-3**.

## Overview

AI Job Agent helps job seekers analyze their resumes, discover startup opportunities, evaluate job descriptions against their profiles, and save relevant opportunities for later tracking.

The application combines a Streamlit frontend with a FastAPI backend and a local Ollama LLM for resume and job analysis.

## Features

### Resume Analysis

* Upload a PDF resume
* Extract resume text using PyMuPDF
* Generate a structured candidate profile using Phi-3
* Extract:

  * Skills
  * Work experience
  * Projects
  * Education
  * Relevant job titles
* Identify technologies and responsibilities from the resume

### Job Description Matching

Users can paste a job description directly into the resume analysis section and compare it against their analyzed resume.

The generated match report includes:

* Overall match score
* Summary
* Strong matches
* Partial matches
* Missing skills
* Experience match
* Project match
* Technical skills match
* Responsibility match
* Seniority match

The matching system evaluates the candidate based on actual experience and responsibilities rather than relying only on keyword overlap.

### YC Startup Job Search

* Fetches startup job listings from Y Combinator's job board
* Role-based filtering
* Experience-based filtering
* Location filtering
* Salary information when available
* Direct application links
* Duplicate job prevention

### Saved Jobs Dashboard

* Save interesting opportunities
* Persistent SQLite storage
* View saved jobs
* Delete saved jobs
* Track discovered opportunities

### Web Application

* Streamlit frontend
* FastAPI backend
* Local LLM inference through Ollama
* Interactive resume analysis and job matching interface

---

## Tech Stack

### Frontend

* Streamlit

### Backend

* FastAPI
* Python

### AI / LLM

* Ollama
* Phi-3

### Resume Processing

* PyMuPDF

### Job Data

* Requests
* HTML parsing
* Y Combinator Jobs

### Database

* SQLite

### Other Technologies

* JSON
* REST APIs
* Git

---

## Architecture

```text
                    ┌──────────────────────┐
                    │     Streamlit UI     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
      Resume Analysis    Job Description     Job Search
             │              Matching              │
             ▼                 │                  ▼
          PyMuPDF              │            YC Job Board
             │                 │
             ▼                 ▼
        Ollama / Phi-3 ────────────────┐
                                       │
                                       ▼
                              SQLite Database
```

---

## API Endpoints

### Resume Analysis

```text
POST /analyze-resume
```

Accepts a PDF resume and returns a structured candidate profile.

### Job Description Analysis

```text
POST /analyze-job
```

Analyzes a pasted job description.

### Resume–Job Matching

```text
POST /analyze-job-match
```

Compares a job description against the analyzed resume profile and generates a match report.

### Job Search

```text
POST /job-search-agent
```

Searches for relevant startup jobs.

### Saved Jobs

```text
POST /save-job
GET  /jobs
DELETE /jobs/{job_id}
```

Provides persistent saved-job management.

---

## Project Structure

```text
AI-Job-Agent/
│
├── agents/
│   ├── career_tools.py
│   ├── yc_jobs.py
│   ├── job_analyzer.py
│   ├── linkedin_jobs.py
│   └── resume_analyzer.py
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

### 1. Clone Repository

```bash
git clone https://github.com/pratikshabhadani/AI-Job-Agent.git

cd AI-Job-Agent
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

**macOS / Linux**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

Install Ollama and make sure it is running.

Pull the Phi-3 model:

```bash
ollama pull phi3
```

Verify:

```bash
ollama list
```

You should see the Phi-3 model available.

### 5. Start FastAPI Backend

```bash
uvicorn main:app --reload
```

The backend runs locally on:

```text
http://127.0.0.1:8000
```

### 6. Start Streamlit Frontend

Open another terminal with the virtual environment activated:

```bash
streamlit run streamlit_app.py
```

The Streamlit application will provide the web interface.

---

## Example Workflow

```text
1. Upload Resume
        ↓
2. Analyze Resume
        ↓
3. Generate Candidate Profile
        ↓
4. View Skills, Experience, Projects and Education
        ↓
5. Search Startup Jobs
        ↓
6. View Job Opportunities
        ↓
7. Save Relevant Jobs
        ↓
8. Paste a Job Description
        ↓
9. Compare Job Against Resume
        ↓
10. View Match Score and Detailed Report
```

---

## Job Matching Example

A candidate can paste a job description such as:

```text
We are looking for a Software Engineer with experience
in Python, REST APIs, databases, and backend development.
Experience with FastAPI and cloud technologies is preferred.
```

The system compares these requirements against the candidate's analyzed resume and produces:

```text
Overall Match Score

Strong Matches
- Python
- REST APIs
- Backend Development

Partial Matches
- Database technologies

Missing Skills
- FastAPI
- Cloud technologies

Experience Match
Project Match
Technical Match
Responsibility Match
Seniority Match
```

---

## Performance Benchmarking

The application can be benchmarked locally by measuring API response times across multiple requests.

For example, the `/jobs` endpoint can be tested repeatedly and the arithmetic mean of the measured response times can be calculated.

Performance figures should be reported only from actual benchmark measurements.

---

## Current Scope

The current implementation focuses on:

* Resume analysis
* Candidate profile extraction
* Startup job discovery
* Job filtering
* Saved-job management
* Job description analysis
* Resume-to-job matching

LinkedIn-related functionality is present in the project structure but should only be considered a completed feature if the corresponding workflow is fully operational.

---

## Future Roadmap

* Multi-source job aggregation
* LinkedIn job integration
* Alumni discovery
* Referral tracking
* Outreach management
* Connection tracking
* Follow-up automation
* Personalized application assistance
* Improved job ranking
* More advanced resume-job matching


---

## Author

**Pratiksha Bhadani**

GitHub:
[https://github.com/pratikshabhadani](https://github.com/pratikshabhadani)
