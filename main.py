from fastapi import (
    FastAPI,
    Form,
    UploadFile,
    File,
    HTTPException
)

import json
import ollama

from agents.career_tools import job_search_agent
from agents.resume_analyzer import analyze_resume
from agents.job_analyzer import analyze_job_description

from database.db import (
    get_jobs,
    save_job,
    job_exists,
    delete_job
)


app = FastAPI()


# ==================================
# HOME
# ==================================

@app.get("/")
def home():

    return {
        "message": "AI Career Agent Running"
    }


# ==================================
# RESUME ANALYSIS
# ==================================

@app.post("/analyze-resume")
async def analyze_resume_endpoint(
    resume: UploadFile = File(...)
):

    if resume.content_type != "application/pdf":

        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF resume."
        )

    pdf_bytes = await resume.read()

    if not pdf_bytes:

        raise HTTPException(
            status_code=400,
            detail="The uploaded resume is empty."
        )

    try:

        result = analyze_resume(
            pdf_bytes
        )

        result["filename"] = resume.filename

        return {
            "success": True,
            "result": result
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Resume analysis failed: {str(exc)}"
        )


# ==================================
# JOB DESCRIPTION ANALYSIS
# ==================================

@app.post("/analyze-job")
async def analyze_job_endpoint(
    job_description: str = Form(...)
):

    if not job_description.strip():

        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    try:

        result = analyze_job_description(
            job_description
        )

        return {
            "success": True,
            "result": result
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Job analysis failed: {str(exc)}"
        )


# ==================================
# JOB DESCRIPTION MATCH
# ==================================

@app.post("/analyze-job-match")
async def analyze_job_match(
    job_description: str = Form(...),
    resume_profile: str = Form(...)
):

    # ----------------------------------
    # VALIDATE INPUT
    # ----------------------------------

    if not job_description.strip():

        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    if not resume_profile.strip():

        raise HTTPException(
            status_code=400,
            detail="Resume profile cannot be empty."
        )

    # ----------------------------------
    # LOAD RESUME PROFILE
    # ----------------------------------

    try:

        profile = json.loads(
            resume_profile
        )

    except json.JSONDecodeError:

        raise HTTPException(
            status_code=400,
            detail="Invalid resume profile JSON."
        )

    # ----------------------------------
    # PROMPT
    # ----------------------------------

    prompt = f"""
You are an expert technical recruiter and resume-job matching system.

Compare the candidate resume against the job description.

Give a realistic match score from 0 to 100.

IMPORTANT RULES:

1. Use ONLY information present in the candidate resume profile.
2. Never invent candidate skills or experience.
3. Never assume the candidate knows a technology because it is common
   for software engineers.
4. Never assume cloud, DevOps, framework, database, or programming
   language experience unless it is actually present in the resume.
5. If a technology is required by the job but is not present in the
   resume, classify it as a missing skill.
6. A strong match requires clear evidence in the resume.
7. A partial match means related evidence exists but the match is
   incomplete or indirect.
8. Do not turn unrelated experience into a match.
9. Consider actual responsibilities, not just keywords.
10. Consider projects as evidence, but do not exaggerate their scope.
11. Consider actual professional experience.
12. Consider seniority requirements.
13. Do not invent job requirements.
14. Give realistic scores from 0 to 100.
15. All scores must be integers.
16. Do not use decimal scores.
17. Return ONLY valid JSON.
18. Do not return markdown.
19. Do not add any explanation outside the JSON.

CANDIDATE RESUME PROFILE:

{json.dumps(
    profile,
    ensure_ascii=False,
    indent=2
)}

JOB DESCRIPTION:

{job_description}

Return exactly this JSON structure:

{{
    "match_score": 0,

    "summary": "",

    "strong_matches": [
        {{
            "skill": "",
            "reason": ""
        }}
    ],

    "partial_matches": [
        {{
            "skill": "",
            "reason": ""
        }}
    ],

    "missing_skills": [
        {{
            "skill": "",
            "reason": ""
        }}
    ],

    "experience_match": {{
        "score": 0,
        "reason": ""
    }},

    "project_match": {{
        "score": 0,
        "reason": ""
    }},

    "technical_match": {{
        "score": 0,
        "reason": ""
    }},

    "responsibility_match": {{
        "score": 0,
        "reason": ""
    }},

    "seniority_match": {{
        "score": 0,
        "reason": ""
    }}
}}

SCORING:

match_score:
0 = no meaningful match
100 = exceptionally strong match

Individual category scores must also be between 0 and 100.

IMPORTANT:

If the model internally evaluates something as:

0.85

return:

85

If the model internally evaluates something as:

0.90

return:

90

Never return:

0.85
0.90
0.75

Only return integer values such as:

85
90
75

Return ONLY the JSON object.
"""

    # ----------------------------------
    # CALL PHI-3
    # ----------------------------------

    try:

        response = ollama.chat(
            model="phi3",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            format="json",
            options={
                "temperature": 0
            }
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"AI model failed: {str(exc)}"
        )

    # ----------------------------------
    # GET MODEL RESPONSE
    # ----------------------------------

    try:

        raw_result = response[
            "message"
        ][
            "content"
        ].strip()

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Invalid AI response: {str(exc)}"
        )

    # ----------------------------------
    # PARSE JSON
    # ----------------------------------

    try:

        result = json.loads(
            raw_result
        )

    except json.JSONDecodeError:

        start = raw_result.find("{")
        end = raw_result.rfind("}")

        if start == -1 or end == -1:

            return {
                "success": False,
                "error": "AI returned invalid JSON.",
                "raw_response": raw_result
            }

        try:

            result = json.loads(
                raw_result[
                    start:end + 1
                ]
            )

        except json.JSONDecodeError:

            return {
                "success": False,
                "error": "AI returned malformed JSON.",
                "raw_response": raw_result
            }

    # ----------------------------------
    # SCORE NORMALIZATION
    # ----------------------------------

    def normalize_score(value):

        try:

            score = float(value)

            # Handle Phi-3 returning
            # 0.85 instead of 85.

            if 0 < score <= 1:

                score = score * 100

            score = round(score)

            return max(
                0,
                min(
                    100,
                    score
                )
            )

        except (
            TypeError,
            ValueError
        ):

            return 0

    # ----------------------------------
    # NORMALIZE OVERALL SCORE
    # ----------------------------------

    result["match_score"] = normalize_score(
        result.get(
            "match_score",
            0
        )
    )

    # ----------------------------------
    # NORMALIZE BREAKDOWN SCORES
    # ----------------------------------

    breakdown_fields = [
        "experience_match",
        "project_match",
        "technical_match",
        "responsibility_match",
        "seniority_match"
    ]

    for field in breakdown_fields:

        if not isinstance(
            result.get(field),
            dict
        ):

            result[field] = {
                "score": 0,
                "reason": ""
            }

        result[field]["score"] = normalize_score(
            result[field].get(
                "score",
                0
            )
        )

    # ----------------------------------
    # ENSURE MATCH ARRAYS EXIST
    # ----------------------------------

    match_arrays = [
        "strong_matches",
        "partial_matches",
        "missing_skills"
    ]

    for field in match_arrays:

        if not isinstance(
            result.get(field),
            list
        ):

            result[field] = []

    # ----------------------------------
    # RETURN RESULT
    # ----------------------------------

    return {
        "success": True,
        "match": result
    }


# ==================================
# JOB SEARCH
# ==================================

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


# ==================================
# SAVE JOB
# ==================================

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


# ==================================
# DELETE SAVED JOB
# ==================================

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


# ==================================
# GET SAVED JOBS
# ==================================

@app.get("/jobs")
def get_saved_jobs():

    jobs = get_jobs()

    return {
        "jobs": jobs
    }