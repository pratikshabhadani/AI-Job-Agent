import streamlit as st
import requests

st.set_page_config(
    page_title="AI Job Agent",
    layout="wide"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Job Search",
        "Saved Jobs",
        "Connections",
        "Outreach"
    ]
)

# ==================================
# JOB SEARCH PAGE
# ==================================

if page == "Job Search":

    st.title("🚀 AI Job Agent")

    st.write(
        "Upload your resume and discover matching jobs."
    )

    resume = st.file_uploader(
        "Upload Resume",
        type=["pdf"]
    )

    target_role = st.text_input(
        "Target Role"
    )

    location = st.text_input(
        "Location"
    )

    work_type = st.selectbox(
        "Work Type",
        [
            "Hybrid",
            "Onsite",
            "Remote"
        ]
    )

    if st.button("Run Job Search"):

        if resume is None:

            st.error(
                "Please upload a resume."
            )

        else:

            files = {
                "resume": resume
            }

            data = {
                "target_role": target_role,
                "location": location,
                "work_type": work_type
            }

            response = requests.post(
                "http://127.0.0.1:8000/job-search-agent",
                files=files,
                data=data
            )

            if response.status_code != 200:

                st.error(
                    f"Backend Error: {response.status_code}"
                )

                st.text(
                    response.text
                )

            else:

                result = response.json()

                st.success(
                    "Analysis Complete"
                )

                st.subheader(
                    "Career Analysis"
                )

                st.metric(
                    "Match Score",
                    result["career_analysis"]["match_score"]
                )

                st.write("### Strengths")

                for skill in result["career_analysis"]["strengths"]:

                    st.write(
                        f"✅ {skill}"
                    )

                st.write("### Missing Skills")

                for skill in result["career_analysis"]["missing_skills"]:

                    st.write(
                        f"❌ {skill}"
                    )

                st.subheader(
                    "Top Jobs"
                )

                if len(result["top_jobs"]) == 0:

                    st.warning(
                        "No matching jobs found."
                    )

                else:

                    for job in result["top_jobs"]:

                        st.write("---")

                        st.write(
                            f"**Company:** {job['company']}"
                        )

                        st.write(
                            f"**Role:** {job['role']}"
                        )

                        st.write(
                            f"**Location:** {job['location']}"
                        )

                        st.write(
                            f"**Work Type:** {job['work_type']}"
                        )

                        st.write(
                            f"**Fit Score:** {job['fit_score']}"
                        )

                        st.write(
                            f"**Application Link:** {job['application_link']}"
                        )

                st.subheader(
                    "Referral Message"
                )

                st.write(
                    result["referral_message"]
                )

# ==================================
# SAVED JOBS PAGE
# ==================================

elif page == "Saved Jobs":

    st.title("💼 Saved Jobs")

    try:

        response = requests.get(
            "http://127.0.0.1:8000/jobs"
        )

        jobs_data = response.json()

        if len(jobs_data["jobs"]) == 0:

            st.info(
                "No jobs saved yet."
            )

        else:

            for job in jobs_data["jobs"]:

                st.subheader(
                    f"{job['company']} - {job['role']}"
                )

                st.write(
                    f"📍 Location: {job['location']}"
                )

                st.write(
                    f"🎯 Fit Score: {job['fit_score']}"
                )

                st.write(
                    f"📌 Status: {job['status']}"
                )

                st.write(
                    f"🔗 {job['job_link']}"
                )

                st.divider()

    except Exception as e:

        st.error(
            f"Unable to load jobs: {str(e)}"
        )

# ==================================
# CONNECTIONS PAGE
# ==================================

elif page == "Connections":

    st.title("👥 Connections")

    st.info(
        "Connections module coming soon."
    )

# ==================================
# OUTREACH PAGE
# ==================================

elif page == "Outreach":

    st.title("📨 Outreach")

    st.info(
        "Outreach module coming soon."
    )