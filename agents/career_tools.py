import ollama
import json

from datetime import datetime

from database.db import (
    save_job,
    job_exists
)


def analyze_resume(
    resume_text,
    target_role
):

    system_prompt = """
    You are an expert AI career agent.

    Return ONLY valid JSON.

    Required format:

    {
      "match_score": integer,
      "strengths": ["item1", "item2"],
      "missing_skills": ["item1", "item2"]
    }

    Do not include markdown.
    Do not include explanations.
    Only output raw JSON.
    """

    user_prompt = f"""
    Resume:
    {resume_text}

    Target Role:
    {target_role}
    """

    response = ollama.chat(
        model="phi3:mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    response_text = response["message"]["content"]

    print("\n====================")
    print("OLLAMA RESPONSE")
    print("====================")
    print(response_text)
    print("====================\n")

    try:

        parsed_json = json.loads(
            response_text
        )

        return parsed_json

    except Exception as e:

        print("JSON ERROR:")
        print(str(e))

        return {
            "match_score": 70,
            "strengths": [],
            "missing_skills": []
        }


def generate_referral_message(
    company,
    role
):

    system_prompt = """
    You generate short professional referral requests.

    Rules:
    - Maximum 80 words
    - Do not invent experience
    - Do not invent companies
    - Do not invent projects
    - Do not invent skills
    - Keep it concise
    - Output only the message
    """

    user_prompt = f"""
    Company: {company}

    Role: {role}

    Write a short LinkedIn referral request.
    """

    response = ollama.chat(
        model="phi3:mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response["message"]["content"]


from agents.yc_jobs import get_yc_jobs


def search_jobs(
    role,
    location,
    work_type,
    experience_level
):

    jobs = get_yc_jobs()

    filtered_jobs = []

    for job in jobs:

        if role.lower() not in job["role"].lower():
            continue

        experience = job.get(
            "experience",
            ""
        )

        if experience_level == "0-3":

            if (
                "5+" in experience
                or "6+" in experience
                or "7+" in experience
                or "10+" in experience
            ):
                continue

        filtered_jobs.append(job)

    return filtered_jobs


def rank_jobs(
    jobs,
    analysis
):

    ranked_jobs = []

    score = analysis["match_score"]

    for job in jobs:

        ranked_jobs.append({
            "company": job["company"],
            "role": job["role"],
            "location": job["location"],
            "salary": job.get(
                "salary",
                ""
            ),
            "experience": job.get(
                "experience",
                ""
            ),
            "application_link": job["application_link"],
            "fit_score": score
        })

    ranked_jobs.sort(
        key=lambda x: x["fit_score"],
        reverse=True
    )

    return ranked_jobs


def job_search_agent(
    resume_text,
    target_role,
    location,
    work_type,
    experience_level
):

    analysis = analyze_resume(
        resume_text,
        target_role
    )

    jobs = search_jobs(
        target_role,
        location,
        work_type,
        experience_level
    )

    ranked_jobs = rank_jobs(
        jobs,
        analysis
    )

    for job in ranked_jobs:

        if not job_exists(
            job["company"],
            job["role"]
        ):

            save_job(
                company=job["company"],
                role=job["role"],
                location=job["location"],
                job_link=job["application_link"],
                fit_score=job["fit_score"],
                status="DISCOVERED",
                date_discovered=str(
                    datetime.now()
                )
            )

    referral_message = ""

    if len(ranked_jobs) > 0:

        top_company = ranked_jobs[0]["company"]

        referral_message = generate_referral_message(
            top_company,
            target_role
        )

    return {
        "career_analysis": analysis,
        "top_jobs": ranked_jobs,
    }