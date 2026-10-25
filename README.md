# AI Job Agent

An AI-powered career assistant built with **Python, FastAPI, Streamlit, SQLite, and Ollama**. It helps job seekers analyze resumes, discover startup opportunities from Y Combinator (YC), compare resumes against job descriptions, and manage saved jobs.

## Features

### Resume Analysis
- Upload PDF resumes.
- Extract resume text using PyMuPDF.
- Generate structured resume profiles using Phi-3 through Ollama.
- Identify skills, work experience, education, projects, and certifications.

### Job Description Analysis and Matching
- Analyze job descriptions to identify skills, technologies, responsibilities, and seniority.
- Compare a resume profile against a job description.
- Generate an AI-based match score and summary.
- Identify strong matches, partial matches, and missing skills.

### Y Combinator Job Search
- Fetch job listings from the YC startup jobs board.
- Extract job information from HTML.
- Filter jobs by role, location, and years of experience.
- Display available salary information and links to original job listings.

### Saved Jobs Dashboard
- Save selected job listings to SQLite.
- View previously saved jobs.
- Delete saved jobs when no longer needed.
- Persist saved jobs across application sessions.

### Web Interface
- Streamlit frontend for user interaction.
- FastAPI backend for processing requests.
- SQLite database for persistent storage.

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend API | FastAPI |
| Database | SQLite |
| LLM Runtime | Ollama |
| Language Model | Phi-3 |
| PDF Processing | PyMuPDF |
| HTTP Requests | Requests |
| HTML Parsing | BeautifulSoup |
| Programming Language | Python |

## Architecture

```text
                    Streamlit Frontend
                           |
                           v
                     FastAPI Backend
                           |
              +------------+------------+
              |            |            |
              v            v            v
        Resume Analysis  YC Job Search  Job Description
          (PyMuPDF +     (HTML Fetch   Analysis & Matching
           Ollama)       and Filtering)   (Ollama)
              |            |            |
              +------------+------------+
                           |
                           v
                      SQLite Database
                       (Saved Jobs)
```

## Project Structure

```text
AI-Job-Agent/
├── agents/
│   ├── career_tools.py
│   ├── job_analyzer.py
│   ├── resume_analyzer.py
│   ├── yc_jobs.py
│   └── linkedin_jobs.py
├── database/
│   └── db.py
├── main.py
├── streamlit_app.py
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/pratikshabhadani/AI-Job-Agent.git
cd AI-Job-Agent
```

### 2. Create a Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama and Download Phi-3

Install Ollama from [ollama.com](https://ollama.com/), then run:

```bash
ollama pull phi3
```

Ensure the Ollama service is running before using the AI-powered features.

### 5. Start the FastAPI Backend

```bash
uvicorn main:app --reload
```

The backend will typically run at:

`http://127.0.0.1:8000`

API documentation is available at:

`http://127.0.0.1:8000/docs`

### 6. Start the Streamlit Frontend

Open a second terminal, activate the virtual environment, and run:

```bash
streamlit run streamlit_app.py
```

## API Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /analyze-resume` | Analyze an uploaded resume |
| `POST /analyze-job` | Analyze a job description |
| `POST /analyze-job-match` | Compare a resume profile against a job description |
| `POST /job-search-agent` | Search YC jobs using specified constraints |
| `POST /save-job` | Save a selected job |
| `GET /jobs` | Retrieve saved jobs |
| `DELETE /jobs/{job_id}` | Delete a saved job |

## Example Workflow

1. Upload a PDF resume.
2. Analyze the resume to generate a structured profile.
3. Enter a target role, location, and experience level.
4. Search for relevant YC startup jobs.
5. Review job details and open the original listing.
6. Save interesting jobs to the dashboard.
7. Paste a job description to analyze it or compare it against the resume.
8. View or delete saved jobs.

## Limitations

- Resume analysis and match scores are AI-generated and may not always be accurate.
- Job availability depends on the YC jobs board and its current HTML structure.
- The current job search filters by role, location, and experience; it does not automatically rank every listing by resume-fit score.
- Jobs are saved when selected by the user, not automatically when search results appear.
- The current implementation uses Python; it does not use Node.js.

## Future Enhancements

- Integrate additional job boards.
- Add more advanced resume-to-job relevance ranking.
- Introduce application and referral tracking.
- Add outreach management and follow-up reminders.
- Support multi-source job aggregation.

## Author

**Pratiksha Bhadani**

[GitHub Profile](https://github.com/pratikshabhadani)