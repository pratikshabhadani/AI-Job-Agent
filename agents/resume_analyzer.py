import json
import re
from typing import Any, Dict, List

import fitz
import ollama


MODEL_NAME = "phi3"
MAX_TEXT_CHARS = 18000


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_pdf_text(pdf_bytes: bytes) -> str:
    """
    Extract all readable text from a PDF using PyMuPDF.
    """

    if not pdf_bytes:
        raise ValueError("The uploaded PDF is empty.")

    try:
        document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )
    except Exception as exc:
        raise ValueError(
            "Could not open the uploaded PDF."
        ) from exc

    pages = []

    try:
        for page in document:
            text = page.get_text("text")

            if text and text.strip():
                pages.append(text)

    finally:
        document.close()

    full_text = "\n\n".join(pages)

    if not full_text.strip():
        raise ValueError(
            "No readable text was found in the PDF."
        )

    # Basic cleanup.
    full_text = full_text.replace(
        "\r\n",
        "\n"
    )

    full_text = full_text.replace(
        "\r",
        "\n"
    )

    full_text = re.sub(
        r"[ \t]+",
        " ",
        full_text
    )

    full_text = re.sub(
        r"\n{3,}",
        "\n\n",
        full_text
    )

    return full_text.strip()


# =========================================================
# SECTION DETECTION
# =========================================================

SECTION_ALIASES = {
    "summary": {
        "summary",
        "professional summary",
        "profile",
        "objective",
        "career objective",
        "about me",
    },

    "skills": {
        "skills",
        "technical skills",
        "technical expertise",
        "core skills",
        "technologies",
        "technical skills and technologies",
    },

    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
    },

    "projects": {
        "projects",
        "personal projects",
        "academic projects",
        "key projects",
    },

    "education": {
        "education",
        "academic background",
        "academic qualifications",
    },

    "certifications": {
        "certifications",
        "certificates",
    },
}


def normalize_heading(line: str) -> str:

    line = line.lower().strip()

    # Remove common PDF/markdown heading artifacts.
    line = re.sub(
        r"\[svg\].*$",
        "",
        line
    )

    line = re.sub(
        r"[^a-z0-9+#/& -]",
        "",
        line
    )

    line = re.sub(
        r"\s+",
        " ",
        line
    )

    return line.strip()


def detect_section(line: str):

    normalized = normalize_heading(
        line
    )

    for section, aliases in SECTION_ALIASES.items():

        if normalized in aliases:
            return section

    return None


def split_sections(
    text: str
) -> Dict[str, str]:

    sections = {
        name: []
        for name in SECTION_ALIASES
    }

    current_section = None

    for raw_line in text.splitlines():

        line = raw_line.strip()

        if not line:
            if current_section:
                sections[current_section].append("")
            continue

        detected = detect_section(
            line
        )

        if detected:

            current_section = detected
            continue

        if current_section:
            sections[current_section].append(
                line
            )

    return {
        key: "\n".join(value).strip()
        for key, value in sections.items()
        if "\n".join(value).strip()
    }


# =========================================================
# SKILL NORMALIZATION
# =========================================================

SKILL_ALIASES = {

    "python": "Python",
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",

    "javascript": "JavaScript",
    "java script": "JavaScript",

    "typescript": "TypeScript",
    "type script": "TypeScript",

    "kotlin": "Kotlin",

    "sql": "SQL",

    "sqlite": "SQLite",
    "sqlite3": "SQLite",

    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",

    "node.js": "Node.js",
    "nodejs": "Node.js",
    "node js": "Node.js",

    "fastapi": "FastAPI",
    "fast api": "FastAPI",

    "pymupdf": "PyMuPDF",
    "py mu pdf": "PyMuPDF",

    "ollama": "Ollama",

    "phi-3": "Phi-3",
    "phi3": "Phi-3",

    "jetpack compose": "Jetpack Compose",

    "android sdk": "Android SDK",

    "android": "Android",

    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",

    "git": "Git",
    "github": "GitHub",

    "gradle": "Gradle",

    "ci/cd": "CI/CD",
    "cicd": "CI/CD",

    "junit": "JUnit",
    "mockito": "Mockito",

    "mvvm": "MVVM",
    "viewmodel": "ViewModel",

    "websockets": "WebSockets",

    "linux": "Linux",

    "postgres": "PostgreSQL",
}


def normalize_skill(
    skill: str
) -> str:

    skill = str(
        skill
    ).strip()

    if not skill:
        return ""

    key = skill.lower()

    return SKILL_ALIASES.get(
        key,
        skill
    )


def unique_skills(
    skills: List[Any]
) -> List[str]:

    result = []
    seen = set()

    for skill in skills:

        skill = normalize_skill(
            skill
        )

        if not skill:
            continue

        key = skill.lower()

        if key not in seen:

            seen.add(key)
            result.append(skill)

    return result


# =========================================================
# EXPLICIT SKILLS FROM RESUME
# =========================================================

def extract_explicit_skills(
    text: str
) -> List[str]:

    """
    Extract skills from the resume's Skills section.

    This is deliberately deterministic so that a good Skills
    section does not depend on Phi-3 producing perfect JSON.
    """

    if not text:
        return []

    skills = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Remove category prefixes.
        line = re.sub(
            r"^(languages?|programming languages?|"
            r"frameworks?|libraries?|tools?|databases?|"
            r"technologies?|technical skills?)\s*:\s*",
            "",
            line,
            flags=re.IGNORECASE
        )

        # Split common separators.
        parts = re.split(
            r",|•|\||;|\t",
            line
        )

        for part in parts:

            part = part.strip()

            if not part:
                continue

            # Do not treat entire sentences as skills.
            if len(part) > 60:
                continue

            # Ignore obvious prose.
            if len(part.split()) > 7:
                continue

            skills.append(
                part
            )

    return unique_skills(
        skills
    )


# =========================================================
# SKILLS FROM ENTIRE RESUME
# =========================================================

def extract_known_skills_from_resume(
    text: str
) -> List[str]:

    """
    Secondary deterministic pass.

    This catches technologies that appear in experience/project
    descriptions even if they were not placed in the Skills section.
    """

    if not text:
        return []

    found = []

    lowered = text.lower()

    for alias, canonical in SKILL_ALIASES.items():

        pattern = r"(?<![a-z0-9])" + re.escape(
            alias
        ) + r"(?![a-z0-9])"

        if re.search(
            pattern,
            lowered
        ):
            found.append(
                canonical
            )

    return unique_skills(
        found
    )


# =========================================================
# JSON EXTRACTION
# =========================================================

def parse_json(
    raw_response: str
) -> Dict[str, Any]:

    if not raw_response:
        raise ValueError(
            "Phi-3 returned an empty response."
        )

    text = raw_response.strip()

    # Remove markdown fences.
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Direct JSON.
    try:

        parsed = json.loads(
            text
        )

        if isinstance(
            parsed,
            dict
        ):
            return parsed

    except json.JSONDecodeError:
        pass

    # Find first JSON object.
    start = text.find("{")

    if start == -1:
        raise ValueError(
            "Phi-3 did not return JSON."
        )

    # Try progressively shorter endings.
    for end in range(
        len(text),
        start,
        -1
    ):

        if text[end - 1] != "}":
            continue

        candidate = text[
            start:end
        ]

        try:

            parsed = json.loads(
                candidate
            )

            if isinstance(
                parsed,
                dict
            ):
                return parsed

        except json.JSONDecodeError:
            continue

    raise ValueError(
        "Could not parse Phi-3 JSON response."
    )


# =========================================================
# PHI-3 ANALYSIS
# =========================================================

def analyze_with_phi3(
    resume_text: str
) -> Dict[str, Any]:

    prompt = f"""
You are an expert technical resume analyst.

Analyze the resume below.

Use ONLY information supported by the resume.
Never invent companies, dates, technologies, projects,
degrees, certifications, or responsibilities.

Your task is to extract:

1. candidate name
2. professional summary
3. work experience
4. projects
5. education
6. certifications
7. relevant job titles
8. technical skills demonstrated by experience/projects

For skills, understand the meaning of the work.
For example, if the resume says someone built a backend
using FastAPI, recognize FastAPI and backend development.
Do not simply copy arbitrary nouns.

Return ONLY valid JSON.
No markdown.
No explanation.

Use exactly this structure:

{{
  "candidate": {{
    "name": "",
    "email": "",
    "phone": ""
  }},

  "summary": "",

  "experience": [
    {{
      "title": "",
      "company": "",
      "duration": "",
      "description": "",
      "skills_used": []
    }}
  ],

  "projects": [
    {{
      "name": "",
      "description": "",
      "technologies": []
    }}
  ],

  "education": [
    {{
      "degree": "",
      "field": "",
      "institution": "",
      "duration": ""
    }}
  ],

  "certifications": [],

  "job_titles": [],

  "skills": []
}}

RESUME:

{resume_text[:MAX_TEXT_CHARS]}
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
            "temperature": 0,
            "num_predict": 2500
        }
    )

    raw = response["message"]["content"]

    return parse_json(
        raw
    )


# =========================================================
# CLEAN LLM RESULT
# =========================================================

def clean_experience(
    items: Any
) -> List[Dict[str, Any]]:

    if not isinstance(
        items,
        list
    ):
        return []

    result = []

    for item in items:

        if not isinstance(
            item,
            dict
        ):
            continue

        result.append({

            "title": str(
                item.get(
                    "title",
                    ""
                )
            ).strip(),

            "company": str(
                item.get(
                    "company",
                    ""
                )
            ).strip(),

            "duration": str(
                item.get(
                    "duration",
                    ""
                )
            ).strip(),

            "description": str(
                item.get(
                    "description",
                    ""
                )
            ).strip(),

            "skills_used": unique_skills(
                item.get(
                    "skills_used",
                    []
                )
                if isinstance(
                    item.get(
                        "skills_used",
                        []
                    ),
                    list
                )
                else []
            )
        })

    return result


def clean_projects(
    items: Any
) -> List[Dict[str, Any]]:

    if not isinstance(
        items,
        list
    ):
        return []

    result = []

    for item in items:

        if not isinstance(
            item,
            dict
        ):
            continue

        result.append({

            "name": str(
                item.get(
                    "name",
                    ""
                )
            ).strip(),

            "description": str(
                item.get(
                    "description",
                    ""
                )
            ).strip(),

            "technologies": unique_skills(
                item.get(
                    "technologies",
                    []
                )
                if isinstance(
                    item.get(
                        "technologies",
                        []
                    ),
                    list
                )
                else []
            )
        })

    return result


def clean_education(
    items: Any
) -> List[Dict[str, str]]:

    if not isinstance(
        items,
        list
    ):
        return []

    result = []

    for item in items:

        if not isinstance(
            item,
            dict
        ):
            continue

        result.append({

            "degree": str(
                item.get(
                    "degree",
                    ""
                )
            ).strip(),

            "field": str(
                item.get(
                    "field",
                    ""
                )
            ).strip(),

            "institution": str(
                item.get(
                    "institution",
                    ""
                )
            ).strip(),

            "duration": str(
                item.get(
                    "duration",
                    ""
                )
            ).strip()
        })

    return result


# =========================================================
# CONTACT EXTRACTION
# =========================================================

def extract_email(
    text: str
) -> str:

    match = re.search(
        r"[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    return (
        match.group(0)
        if match
        else ""
    )


def extract_phone(
    text: str
) -> str:

    match = re.search(
        r"(?:\+?\d[\d\s().-]{8,}\d)",
        text
    )

    if not match:
        return ""

    return match.group(0).strip()


# =========================================================
# NAME EXTRACTION
# =========================================================

def extract_candidate_name(
    text: str
) -> str:

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return ""

    # Usually the first meaningful line of a resume.
    first_line = lines[0]

    if (
        len(first_line) <= 80
        and "@" not in first_line
        and not re.search(
            r"\d{3,}",
            first_line
        )
    ):
        return first_line

    return ""


# =========================================================
# MAIN RESUME ANALYZER
# =========================================================

def analyze_resume(
    pdf_bytes: bytes
) -> Dict[str, Any]:

    # -----------------------------------------------------
    # 1. PDF → TEXT
    # -----------------------------------------------------

    text = extract_pdf_text(
        pdf_bytes
    )

    # -----------------------------------------------------
    # 2. DETECT SECTIONS
    # -----------------------------------------------------

    sections = split_sections(
        text
    )

    # -----------------------------------------------------
    # 3. DETERMINISTIC SKILL EXTRACTION
    # -----------------------------------------------------

    explicit_skills = extract_explicit_skills(
        sections.get(
            "skills",
            ""
        )
    )

    resume_skills = extract_known_skills_from_resume(
        text
    )

    all_skills = unique_skills(
        explicit_skills + resume_skills
    )

    # -----------------------------------------------------
    # 4. PHI-3 ANALYSIS
    # -----------------------------------------------------

    try:

        ai_result = analyze_with_phi3(
            text
        )

    except Exception as exc:

        # Do NOT silently return an empty resume.
        raise RuntimeError(
            f"Phi-3 resume analysis failed: {exc}"
        ) from exc

    # -----------------------------------------------------
    # 5. CLEAN AI DATA
    # -----------------------------------------------------

    candidate_data = ai_result.get(
        "candidate",
        {}
    )

    if not isinstance(
        candidate_data,
        dict
    ):
        candidate_data = {}

    candidate = {

        "name": (
            str(
                candidate_data.get(
                    "name",
                    ""
                )
            ).strip()
            or extract_candidate_name(
                text
            )
        ),

        "email": (
            str(
                candidate_data.get(
                    "email",
                    ""
                )
            ).strip()
            or extract_email(
                text
            )
        ),

        "phone": (
            str(
                candidate_data.get(
                    "phone",
                    ""
                )
            ).strip()
            or extract_phone(
                text
            )
        )
    }

    summary = str(
        ai_result.get(
            "summary",
            ""
        )
    ).strip()

    experience = clean_experience(
        ai_result.get(
            "experience",
            []
        )
    )

    projects = clean_projects(
        ai_result.get(
            "projects",
            []
        )
    )

    education = clean_education(
        ai_result.get(
            "education",
            []
        )
    )

    certifications = ai_result.get(
        "certifications",
        []
    )

    if not isinstance(
        certifications,
        list
    ):
        certifications = []

    job_titles = ai_result.get(
        "job_titles",
        []
    )

    if not isinstance(
        job_titles,
        list
    ):
        job_titles = []

    job_titles = [
        str(title).strip()
        for title in job_titles
        if str(title).strip()
    ]

    # -----------------------------------------------------
    # 6. MERGE AI SKILLS
    # -----------------------------------------------------

    ai_skills = ai_result.get(
        "skills",
        []
    )

    if not isinstance(
        ai_skills,
        list
    ):
        ai_skills = []

    all_skills = unique_skills(
        all_skills + ai_skills
    )

    # Skills from experience.
    for job in experience:

        all_skills = unique_skills(
            all_skills
            + job.get(
                "skills_used",
                []
            )
        )

    # Skills from projects.
    for project in projects:

        all_skills = unique_skills(
            all_skills
            + project.get(
                "technologies",
                []
            )
        )

    # -----------------------------------------------------
    # 7. SKILL EVIDENCE
    # -----------------------------------------------------

    skill_evidence = []

    for skill in all_skills:

        source = "resume"

        evidence = (
            "Detected in the resume."
        )

        if skill.lower() in {
            s.lower()
            for s in explicit_skills
        }:

            source = "skills_section"

            evidence = (
                "Explicitly listed in the "
                "resume Skills section."
            )

        else:

            for job in experience:

                if skill.lower() in {
                    s.lower()
                    for s in job.get(
                        "skills_used",
                        []
                    )
                }:

                    source = "experience"

                    evidence = job.get(
                        "description",
                        ""
                    )

                    break

            for project in projects:

                if skill.lower() in {
                    s.lower()
                    for s in project.get(
                        "technologies",
                        []
                    )
                }:

                    source = "project"

                    evidence = project.get(
                        "description",
                        ""
                    )

                    break

        skill_evidence.append({

            "skill": skill,

            "evidence": evidence,

            "source": source,

            "confidence": (
                1.0
                if source == "skills_section"
                else 0.85
            )
        })

    # -----------------------------------------------------
    # 8. JOB TITLES FALLBACK
    # -----------------------------------------------------

    if not job_titles:

        job_titles = [

            job.get(
                "title",
                ""
            )

            for job in experience

            if job.get(
                "title"
            )
        ]

    # -----------------------------------------------------
    # 9. FINAL PROFILE
    # -----------------------------------------------------

    profile = {

        "candidate": candidate,

        "summary": summary,

        "skills": all_skills,

        "skill_evidence": skill_evidence,

        "experience": experience,

        "projects": projects,

        "education": education,

        "certifications": certifications,

        "domains": [],

        "job_titles": job_titles,

        "experience_years": None
    }

    # -----------------------------------------------------
    # 10. RESPONSE
    # -----------------------------------------------------

    return {

        "filename": "resume.pdf",

        "text": text,

        "profile": profile,

        "candidate": candidate,

        "summary": summary,

        "skills": all_skills,

        "skill_count": len(
            all_skills
        ),

        "experience": experience,

        "projects": projects,

        "education": education,

        "certifications": certifications,

        "domains": [],

        "job_titles": job_titles,

        "experience_years": None,

        "skill_evidence": skill_evidence,

        "inference": MODEL_NAME
    }