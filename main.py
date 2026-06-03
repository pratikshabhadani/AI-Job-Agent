from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
import fitz

from agents.career_tools import (
    analyze_resume,
    generate_referral_message,
    search_jobs,
    rank_jobs,
    job_search_agent
)

from database.db import (
    get_jobs
)

app = FastAPI()


class CareerAnalysis(BaseModel):
    match_score: int
    strengths: List[str]
    missing_skills: List[str]


@app.get("/")
def home():

    return {
        "message": "AI Job Agent Running"
    }


@app.post("/career-agent")
async def career_agent(
    resume: UploadFile = File(...),
    target_role: str = Form(...)
):

    pdf_text = ""

    pdf_bytes = await resume.read()

    pdf_document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    for page in pdf_document:
        pdf_text += page.get_text()

    analysis = analyze_resume(
        pdf_text,
        target_role
    )

    validated_response = CareerAnalysis(
        **analysis
    )

    return validated_response


@app.get("/generate-referral")
def generate_referral():

    message = generate_referral_message(
        "Google",
        "Backend Software Engineer"
    )

    return {
        "referral_message": message
    }


@app.get("/search-jobs")
def search_jobs_endpoint():

    jobs = search_jobs(
        "Backend",
        "Bangalore",
        "Hybrid"
    )

    return {
        "jobs": jobs
    }


@app.post("/job-search-agent")
async def run_job_search_agent(
    resume: UploadFile = File(...),
    target_role: str = Form(...),
    location: str = Form(...),
    work_type: str = Form(...),
    experience_level: str = Form(...)
):

    pdf_text = ""

    pdf_bytes = await resume.read()

    pdf_document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    for page in pdf_document:
        pdf_text += page.get_text()

    result = job_search_agent(
        pdf_text,
        target_role,
        location,
        work_type,
        experience_level
    )

    return result


@app.get("/jobs")
def get_saved_jobs():

    jobs = get_jobs()

    return {
        "jobs": jobs
    }