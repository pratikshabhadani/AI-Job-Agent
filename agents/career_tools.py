from agents.yc_jobs import get_yc_jobs


def search_jobs(
    role,
    posted,
    experience_level,
    work_type,
    location=None
):

    jobs = get_yc_jobs(
        role=role,
        posted=posted,
        experience_level=experience_level,
        work_type=work_type,
        location=location,
        limit=20
    )

    return jobs


def job_search_agent(
    target_role,
    posted,
    experience_level,
    work_type,
    location=None
):

    jobs = search_jobs(
        target_role,
        posted,
        experience_level,
        work_type,
        location
    )

    return {
        "top_jobs": jobs[:20]
    }