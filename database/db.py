import sqlite3
from datetime import datetime


connection = sqlite3.connect(
    "jobs.db",
    check_same_thread=False
)

cursor = connection.cursor()


# ==================================
# JOBS TABLE
# ==================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT,
    role TEXT,
    location TEXT,
    job_link TEXT,
    fit_score INTEGER,
    status TEXT,
    date_discovered TEXT
)
""")


# ==================================
# CONNECTIONS TABLE
# ==================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    name TEXT,
    linkedin_url TEXT,
    company TEXT,
    relationship_type TEXT,
    priority_score INTEGER,
    status TEXT,
    FOREIGN KEY(job_id) REFERENCES jobs(id)
)
""")


# ==================================
# OUTREACH TABLE
# ==================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS outreach (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    connection_id INTEGER,
    request_sent INTEGER,
    request_sent_date TEXT,
    accepted INTEGER,
    accepted_date TEXT,
    referral_requested INTEGER,
    referral_requested_date TEXT,
    followup_count INTEGER,
    last_followup_date TEXT,
    status TEXT,
    FOREIGN KEY(connection_id) REFERENCES connections(id)
)
""")


connection.commit()


# ==================================
# JOB FUNCTIONS
# ==================================

def save_job(
    company,
    role,
    location,
    job_link,
    fit_score,
    status,
    date_discovered
):

    saved_at = datetime.now().isoformat(
        timespec="seconds"
    )

    cursor.execute("""
    INSERT INTO jobs (
        company,
        role,
        location,
        job_link,
        fit_score,
        status,
        date_discovered
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        company,
        role,
        location,
        job_link,
        fit_score,
        status,
        saved_at
    ))

    connection.commit()


def get_jobs():

    cursor.execute("""
    SELECT * FROM jobs
    ORDER BY datetime(date_discovered) DESC
    """)

    rows = cursor.fetchall()

    jobs = []

    for row in rows:

        jobs.append({
            "id": row[0],
            "company": row[1],
            "role": row[2],
            "location": row[3],
            "job_link": row[4],
            "fit_score": row[5],
            "status": row[6],
            "date_discovered": row[7]
        })

    return jobs


def delete_job(job_id):

    cursor.execute("""
    DELETE FROM jobs
    WHERE id = ?
    """, (job_id,))

    connection.commit()


def job_exists(
    company,
    role
):

    cursor.execute("""
    SELECT id
    FROM jobs
    WHERE company = ?
    AND role = ?
    """, (
        company,
        role
    ))

    return cursor.fetchone() is not None