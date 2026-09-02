import requests
import html
import re
import json


YC_BASE_URL = "https://www.ycombinator.com"


def slugify(value):
    """
    Convert a filter value into the URL format used by YC.

    Example:
        Software Engineer -> software-engineer
        Remote -> remote
    """

    value = value.strip().lower()

    value = re.sub(
        r"[^a-z0-9\s-]",
        "",
        value
    )

    value = re.sub(
        r"\s+",
        "-",
        value
    )

    value = re.sub(
        r"-+",
        "-",
        value
    )

    return value.strip("-")


def build_yc_url(
    role,
    location=None
):
    """
    Build the YC Jobs URL using YC's
    public role/location URL structure.
    """

    if role:
        role_slug = slugify(role)
    else:
        role_slug = "all"

    url = (
        f"{YC_BASE_URL}/jobs/role/"
        f"{role_slug}"
    )

    if location and location != "All":
        location_slug = slugify(location)

        url += (
            f"/{location_slug}"
        )

    return url


def experience_matches_filter(
    experience,
    selected_filter
):
    """
    Check whether a YC job matches the
    selected experience range.

    Experience ranges:

        0–1 years
        1–3 years
        3–6 years
        6–11 years
        11+ years

    If YC says:
        Any
        Any (new grads ok)
        blank

    the job is included for every filter.
    """

    # No filter selected.
    if not selected_filter:
        return True

    # Blank experience on YC.
    if experience is None:
        return True

    experience_text = str(
        experience
    ).strip().lower()

    if not experience_text:
        return True

    # YC does not specify a minimum.
    if (
        experience_text == "any"
        or "any (new grads ok)" in experience_text
        or "new grad" in experience_text
    ):
        return True

    # Extract the first number from the
    # experience requirement.
    #
    # Examples:
    # 1+       -> 1
    # 2+       -> 2
    # 3+       -> 3
    # 6+       -> 6
    # 11+      -> 11

    match = re.search(
        r"\d+",
        experience_text
    )

    if not match:
        return False

    years = int(
        match.group()
    )

    if selected_filter == "0–1 years":
        return 0 <= years <= 1

    if selected_filter == "1–3 years":
        return 1 <= years <= 3

    if selected_filter == "3–6 years":
        return 3 <= years <= 6

    if selected_filter == "6–11 years":
        return 6 <= years <= 11

    if selected_filter == "11+ years":
        return years >= 11

    return True


def get_yc_jobs(
    role,
    posted,
    experience_level,
    work_type,
    location=None,
    limit=20
):

    url = build_yc_url(
        role,
        location
    )

    try:

        response = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/139.0 Safari/537.36"
                )
            },
            timeout=15
        )

        response.raise_for_status()

    except requests.RequestException as e:

        print(
            f"YC request failed: {e}"
        )

        return []

    decoded_html = html.unescape(
        response.text
    )

    pattern = (
        r'\{"id":.*?'
        r'"companyName":".*?"\}'
    )

    matches = re.findall(
        pattern,
        decoded_html
    )

    jobs = []

    seen_links = set()

    for match in matches:

        try:

            job = json.loads(
                match
            )

            application_link = (
                YC_BASE_URL
                + job.get("url", "")
            )

            if application_link in seen_links:
                continue

            seen_links.add(
                application_link
            )

            experience = job.get(
                "minExperience",
                ""
            )

            # ---------------------------------
            # EXPERIENCE FILTER
            # ---------------------------------

            if not experience_matches_filter(
                experience,
                experience_level
            ):
                continue

            # ---------------------------------
            # JOB DATA
            # ---------------------------------

            job_data = {

                "company": job.get(
                    "companyName",
                    ""
                ),

                "role": job.get(
                    "title",
                    ""
                ),

                "location": job.get(
                    "location",
                    ""
                ),

                "salary": job.get(
                    "salaryRange",
                    ""
                ),

                "experience": experience,

                "application_link":
                    application_link,

                "work_type": job.get(
                    "jobType",
                    ""
                )
            }

            if not job_data["role"]:
                continue

            jobs.append(
                job_data
            )

            # Keep top 20 matching jobs.
            if len(jobs) >= limit:
                break

        except (
            json.JSONDecodeError,
            TypeError
        ):

            continue

    return jobs