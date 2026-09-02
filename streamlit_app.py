import streamlit as st
import requests

st.set_page_config(
    page_title="AI Career Agent",
    layout="wide"
)

# ==================================
# SESSION STATE
# ==================================

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "saved_job_links" not in st.session_state:
    st.session_state.saved_job_links = set()


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

    st.title("🚀 AI Career Agent")

    st.write(
        "Search LinkedIn jobs across India."
    )

    target_role = st.text_input(
        "Role"
    )

    location = st.selectbox(
        "Location",
        [
            "All",
            "Remote",
            "India",
            "United States",
            "Canada",
            "United Kingdom"
        ]
    )

    experience_level = st.selectbox(
        "Years of Experience",
        [
            "0–1 years",
            "1–3 years",
            "3–6 years",
            "6–11 years",
            "11+ years"
        ]
    )

    if st.button("Search Jobs"):

        data = {
            "target_role": target_role,
            "experience_level": experience_level,
            "location": location
        }

        response = requests.post(
            "http://127.0.0.1:8000/job-search-agent",
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

            st.session_state.search_results = (
                result.get("top_jobs", [])
            )

            st.session_state.saved_job_links = set()


    # ==================================
    # DISPLAY SEARCH RESULTS
    # ==================================

    if st.session_state.search_results:

        st.subheader("Top Jobs")

        for job in st.session_state.search_results:

            job_link = job.get(
                "application_link",
                ""
            )

            st.write("---")

            st.subheader(
                job.get(
                    "role",
                    "Unknown Role"
                )
            )

            st.write(
                f"**{job.get('company', 'Unknown Company')}**"
            )

            details = []

            if job.get("location"):
                details.append(
                    job["location"]
                )

            if job.get("salary"):
                details.append(
                    job["salary"]
                )

            if job.get("experience"):
                details.append(
                    job["experience"]
                )

            if details:

                st.caption(
                    " • ".join(details)
                )

            col1, col2 = st.columns(2)

            with col1:

                st.link_button(
                    "View Job on YC",
                    job_link,
                    use_container_width=True
                )

            with col2:

                save_button_key = (
                    f"save_job_{job_link}"
                )

                if job_link in (
                    st.session_state.saved_job_links
                ):

                    st.success(
                        "Job Saved"
                    )

                else:

                    if st.button(
                        "Save Job",
                        key=save_button_key,
                        use_container_width=True
                    ):

                        save_data = {
                            "company": job.get(
                                "company",
                                ""
                            ),
                            "role": job.get(
                                "role",
                                ""
                            ),
                            "location": job.get(
                                "location",
                                ""
                            ),
                            "job_link": job_link
                        }

                        save_response = requests.post(
                            "http://127.0.0.1:8000/save-job",
                            data=save_data
                        )

                        if save_response.status_code == 200:

                            save_result = (
                                save_response.json()
                            )

                            if save_result["success"]:

                                st.session_state.saved_job_links.add(
                                    job_link
                                )

                                st.success(
                                    "Job saved successfully."
                                )

                            else:

                                st.session_state.saved_job_links.add(
                                    job_link
                                )

                                st.info(
                                    save_result["message"]
                                )

                        else:

                            st.error(
                                f"Unable to save job: "
                                f"{save_response.status_code}"
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

        if response.status_code != 200:

            st.error(
                f"Unable to load jobs: "
                f"{response.status_code}"
            )

        else:

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
                        f"📌 Status: {job['status']}"
                    )

                    if job.get("date_discovered"):

                        st.caption(
                            f"Saved: "
                            f"{job['date_discovered']}"
                        )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.link_button(
                            "View Job",
                            job["job_link"],
                            use_container_width=True
                        )

                    with col2:

                        if st.button(
                            "Delete",
                            key=f"delete_job_{job['id']}",
                            use_container_width=True
                        ):

                            delete_response = requests.delete(
                                f"http://127.0.0.1:8000/jobs/{job['id']}"
                            )

                            if delete_response.status_code == 200:

                                st.success(
                                    "Job deleted."
                                )

                                st.rerun()

                            else:

                                st.error(
                                    f"Unable to delete job: "
                                    f"{delete_response.status_code}"
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
