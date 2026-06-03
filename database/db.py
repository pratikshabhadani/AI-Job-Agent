import sqlite3


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
        date_discovered
    ))

    connection.commit()


def get_jobs():

    cursor.execute("""
    SELECT * FROM jobs
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


# ==================================
# CONNECTION FUNCTIONS
# ==================================

def save_connection(
    job_id,
    name,
    linkedin_url,
    company,
    relationship_type,
    priority_score,
    status="IDENTIFIED"
):

    cursor.execute("""
    INSERT INTO connections (
        job_id,
        name,
        linkedin_url,
        company,
        relationship_type,
        priority_score,
        status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        job_id,
        name,
        linkedin_url,
        company,
        relationship_type,
        priority_score,
        status
    ))

    connection.commit()


def get_connections_for_job(
    job_id
):

    cursor.execute("""
    SELECT *
    FROM connections
    WHERE job_id = ?
    ORDER BY priority_score DESC
    """, (job_id,))

    rows = cursor.fetchall()

    connections = []

    for row in rows:

        connections.append({
            "id": row[0],
            "job_id": row[1],
            "name": row[2],
            "linkedin_url": row[3],
            "company": row[4],
            "relationship_type": row[5],
            "priority_score": row[6],
            "status": row[7]
        })

    return connections


# ==================================
# OUTREACH FUNCTIONS
# ==================================

def save_outreach(
    connection_id,
    request_sent=0,
    request_sent_date="",
    accepted=0,
    accepted_date="",
    referral_requested=0,
    referral_requested_date="",
    followup_count=0,
    last_followup_date="",
    status="IDENTIFIED"
):

    cursor.execute("""
    INSERT INTO outreach (
        connection_id,
        request_sent,
        request_sent_date,
        accepted,
        accepted_date,
        referral_requested,
        referral_requested_date,
        followup_count,
        last_followup_date,
        status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        connection_id,
        request_sent,
        request_sent_date,
        accepted,
        accepted_date,
        referral_requested,
        referral_requested_date,
        followup_count,
        last_followup_date,
        status
    ))

    connection.commit()


def get_outreach():

    cursor.execute("""
    SELECT * FROM outreach
    """)

    rows = cursor.fetchall()

    outreach_records = []

    for row in rows:

        outreach_records.append({
            "id": row[0],
            "connection_id": row[1],
            "request_sent": row[2],
            "request_sent_date": row[3],
            "accepted": row[4],
            "accepted_date": row[5],
            "referral_requested": row[6],
            "referral_requested_date": row[7],
            "followup_count": row[8],
            "last_followup_date": row[9],
            "status": row[10]
        })

    return outreach_records