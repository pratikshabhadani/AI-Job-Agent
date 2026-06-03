import requests
import html
import re
import json


def get_yc_jobs():

    response = requests.get(
        "https://www.ycombinator.com/jobs",
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    decoded_html = html.unescape(
        response.text
    )

    pattern = r'\{"id":.*?"companyName":".*?"\}'

    matches = re.findall(
        pattern,
        decoded_html
    )

    jobs = []

    for match in matches:

        try:

            job = json.loads(
                match
            )

            jobs.append({
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
                "experience": job.get(
                    "minExperience",
                    ""
                ),
                "application_link":
                "https://www.ycombinator.com"
                + job.get(
                    "url",
                    ""
                )
            })

        except:

            pass

    return jobs