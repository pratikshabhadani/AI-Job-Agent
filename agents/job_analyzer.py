import json
import re

import ollama


MODEL_NAME = "phi3"


def _extract_json(text: str) -> dict:
    """
    Extract a JSON object from the model response.
    Handles responses where the model adds extra text
    around the JSON.
    """

    text = text.strip()

    # Remove markdown code fences if present.
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        pass

    # Find the first JSON object in the response.
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            "Phi-3 did not return valid JSON."
        )

    try:
        return json.loads(
            text[start:end + 1]
        )

    except json.JSONDecodeError as exc:

        raise ValueError(
            "Could not parse the job analysis returned by Phi-3."
        ) from exc


def analyze_job_description(
    job_description: str
) -> dict:

    if not job_description or not job_description.strip():

        raise ValueError(
            "Job description cannot be empty."
        )

    prompt = f"""
You are an expert technical recruiter and job-description analyst.

Analyze the following job description semantically.

Do NOT merely extract words.
Infer the actual capabilities, technologies, responsibilities,
seniority expectations, and qualifications required for the role.

Separate requirements into:

1. Core technical skills
   Skills that are fundamental to performing the job.

2. Supporting technical skills
   Useful technical capabilities that strengthen the candidate.

3. Soft skills
   Communication, leadership, collaboration, problem solving, etc.

4. Tools and technologies
   Specific frameworks, programming languages, databases,
   cloud platforms, developer tools, and other technologies.

5. Responsibilities
   What the person is expected to actually do.

6. Experience requirements
   Years of experience, domain experience, or level of responsibility.

7. Education requirements
   Degrees, fields of study, certifications, or equivalent requirements.

8. Domain knowledge
   Industry or subject-matter knowledge required by the role.

9. Seniority
   Infer the likely seniority level from the description.

10. Required vs preferred
    Clearly distinguish mandatory requirements from preferred
    or nice-to-have qualifications.

For every important skill or capability, provide a short explanation
of WHY it appears to be required based on the job description.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "job_title": "",
    "seniority": "",
    "summary": "",

    "required_skills": [
        {{
            "skill": "",
            "importance": "critical|high|medium",
            "reason": ""
        }}
    ],

    "preferred_skills": [
        {{
            "skill": "",
            "importance": "high|medium|low",
            "reason": ""
        }}
    ],

    "technologies": [
        {{
            "name": "",
            "category": "",
            "required": true,
            "reason": ""
        }}
    ],

    "soft_skills": [],

    "responsibilities": [],

    "experience_requirements": [],

    "education_requirements": [],

    "domain_knowledge": [],

    "keywords": []
}}

JOB DESCRIPTION:

{job_description}
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0.1
        }
    )

    content = response["message"]["content"]

    result = _extract_json(content)

    # Ensure expected top-level fields exist.
    result.setdefault("job_title", "")
    result.setdefault("seniority", "")
    result.setdefault("summary", "")
    result.setdefault("required_skills", [])
    result.setdefault("preferred_skills", [])
    result.setdefault("technologies", [])
    result.setdefault("soft_skills", [])
    result.setdefault("responsibilities", [])
    result.setdefault("experience_requirements", [])
    result.setdefault("education_requirements", [])
    result.setdefault("domain_knowledge", [])
    result.setdefault("keywords", [])

    result["inference"] = MODEL_NAME

    return result