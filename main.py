from fastapi import FastAPI, Form

from agents.career_tools import job_search_agent

from database.db import (
    get_jobs,
    save_job,
    job_exists,
    delete_job
)

app = FastAPI()


@app.get("/")
def home():

    return {
        "message": "AI Career Agent Running"
    }


@app.post("/job-search-agent")
async def run_job_search_agent(
    target_role: str = Form(...),
    experience_level: str = Form(...),
    location: str = Form("")
):

    result = job_search_agent(
        target_role,
        "",
        experience_level,
        "",
        location
    )

    return result


@app.post("/save-job")
async def save_job_endpoint(
    company: str = Form(...),
    role: str = Form(...),
    location: str = Form(""),
    job_link: str = Form(...)
):

    if job_exists(
        company,
        role
    ):

        return {
            "success": False,
            "message": "Job already saved."
        }

    save_job(
        company=company,
        role=role,
        location=location,
        job_link=job_link,
        fit_score=0,
        status="SAVED",
        date_discovered=""
    )

    return {
        "success": True,
        "message": "Job saved successfully."
    }


@app.delete("/jobs/{job_id}")
async def delete_saved_job(
    job_id: int
):

    delete_job(
        job_id
    )

    return {
        "success": True,
        "message": "Job deleted successfully."
    }


@app.get("/jobs")
def get_saved_jobs():

    jobs = get_jobs()

    return {
        "jobs": jobs
    }
