import streamlit as st
import requests
import json

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

if "resume_profile" not in st.session_state:
    st.session_state.resume_profile = None

if "job_match" not in st.session_state:
    st.session_state.job_match = None


# ==================================
# NAVIGATION
# ==================================

page = st.sidebar.radio(
    "Navigation",
    [
        "Job Search",
        "Resume Analysis",
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

    if st.button(
        "Search Jobs"
    ):

        data = {
            "target_role": target_role,
            "experience_level": experience_level,
            "location": location
        }

        try:

            response = requests.post(
                "http://127.0.0.1:8000/job-search-agent",
                data=data,
                timeout=60
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
                    result.get(
                        "top_jobs",
                        []
                    )
                )

                st.session_state.saved_job_links = set()

        except Exception as e:

            st.error(
                f"Unable to search jobs: {str(e)}"
            )


    # ==================================
    # DISPLAY SEARCH RESULTS
    # ==================================

    if st.session_state.search_results:

        st.subheader(
            "Top Jobs"
        )

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

                if job_link:

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

                        try:

                            save_response = requests.post(
                                "http://127.0.0.1:8000/save-job",
                                data=save_data,
                                timeout=30
                            )

                            if save_response.status_code == 200:

                                save_result = (
                                    save_response.json()
                                )

                                if save_result.get(
                                    "success"
                                ):

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
                                        save_result.get(
                                            "message",
                                            "Job already saved."
                                        )
                                    )

                            else:

                                st.error(
                                    f"Unable to save job: "
                                    f"{save_response.status_code}"
                                )

                        except Exception as e:

                            st.error(
                                f"Unable to save job: {str(e)}"
                            )


# ==================================
# RESUME ANALYSIS PAGE
# ==================================

elif page == "Resume Analysis":

    st.title(
        "📄 Resume Analysis"
    )

    st.write(
        "Upload your resume and analyze your skills, experience, projects, and job fit."
    )

    uploaded_file = st.file_uploader(
        "Upload Resume",
        type=["pdf"],
        key="resume_upload"
    )

    if uploaded_file is not None:

        if st.button(
            "Analyze Resume",
            use_container_width=True,
            key="analyze_resume"
        ):

            with st.spinner(
                "Analyzing your resume..."
            ):

                try:

                    response = requests.post(
                        "http://127.0.0.1:8000/analyze-resume",
                        files={
                                "resume": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                uploaded_file.type
                            )
                        },
                        timeout=300
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

                        if result.get(
                            "success"
                        ):

                            st.session_state.resume_profile = result.get(
                                                                            "result",
                                                                            result
                                                                        )

                            # Clear previous job match
                            # when a new resume is analyzed.
                            st.session_state.job_match = None

                            st.success(
                                "Resume analyzed successfully."
                            )

                        else:

                            st.error(
                                result.get(
                                    "error",
                                    "Resume analysis failed."
                                )
                            )

                except requests.exceptions.Timeout:

                    st.error(
                        "Resume analysis timed out."
                    )

                except Exception as e:

                    st.error(
                        f"Unable to analyze resume: {str(e)}"
                    )


    # ==================================
    # DISPLAY RESUME ANALYSIS
    # ==================================

    if st.session_state.resume_profile:

        result = st.session_state.resume_profile

        profile = result.get(
            "profile",
            result
        )

        st.divider()

        st.subheader(
            "Candidate Profile"
        )

        # ==================================
        # CONTACT
        # ==================================

        if profile.get(
            "email"
        ):

            st.write(
                f"**Email:** {profile['email']}"
            )

        if profile.get(
            "phone"
        ):

            st.write(
                f"**Phone:** {profile['phone']}"
            )


        # ==================================
        # SUMMARY
        # ==================================

        if profile.get(
            "summary"
        ):

            st.subheader(
                "Professional Summary"
            )

            st.write(
                profile["summary"]
            )


        # ==================================
        # SKILLS
        # ==================================

        skills = profile.get(
            "skills",
            []
        )

        st.subheader(
            f"Skills ({len(skills)})"
        )

        if skills:

            cols = st.columns(3)

            for index, skill in enumerate(
                skills
            ):

                with cols[
                    index % 3
                ]:

                    st.markdown(
                        f"**{skill}**"
                    )

        else:

            st.info(
                "No skills were extracted."
            )


        # ==================================
        # EXPERIENCE
        # ==================================

        experience = profile.get(
            "experience",
            []
        )

        st.subheader(
            "Experience"
        )

        if experience:

            for item in experience:

                st.markdown(
                    f"### {item.get('title', '')}"
                )

                if item.get(
                    "company"
                ):

                    st.write(
                        f"**{item['company']}**"
                    )

                if item.get(
                    "duration"
                ):

                    st.caption(
                        item["duration"]
                    )

                if item.get(
                    "description"
                ):

                    st.write(
                        item["description"]
                    )

                st.divider()

        else:

            st.info(
                "No experience found."
            )


        # ==================================
        # PROJECTS
        # ==================================

        projects = profile.get(
            "projects",
            []
        )

        st.subheader(
            "Projects"
        )

        if projects:

            for project in projects:

                st.markdown(
                    f"### {project.get('name', '')}"
                )

                if project.get(
                    "description"
                ):

                    st.write(
                        project["description"]
                    )

                technologies = project.get(
                    "technologies",
                    []
                )

                if technologies:

                    st.caption(
                        "Technologies: "
                        + ", ".join(
                            technologies
                        )
                    )

                st.divider()

        else:

            st.info(
                "No projects found."
            )


        # ==================================
        # EDUCATION
        # ==================================

        education = profile.get(
            "education",
            []
        )

        st.subheader(
            "Education"
        )

        if education:

            for item in education:

                st.markdown(
                    f"### {item.get('degree', '')}"
                )

                institution = item.get(
                    "institution",
                    ""
                )

                if institution:

                    st.write(
                        institution
                    )

                if item.get(
                    "duration"
                ):

                    st.caption(
                        item["duration"]
                    )

        else:

            st.info(
                "No education information found."
            )


        # ==================================
        # JOB DESCRIPTION MATCH
        # ==================================

        st.divider()

        st.subheader(
            "🎯 Job Description Match"
        )

        st.write(
            "Paste a job description below to compare it against your analyzed resume."
        )

        job_description = st.text_area(
            "Job Description",
            height=300,
            placeholder=(
                "Paste the complete job description here..."
            ),
            key="job_description_input"
        )

        if st.button(
            "Analyze Match",
            use_container_width=True,
            key="analyze_job_match"
        ):

            if not job_description.strip():

                st.warning(
                    "Please paste a job description first."
                )

            else:

                with st.spinner(
                    "Analyzing your resume against the job description..."
                ):

                    try:

                        response = requests.post(
                            "http://127.0.0.1:8000/analyze-job-match",
                            data={
                                "job_description":
                                    job_description,

                                "resume_profile":
                                    json.dumps(
                                        st.session_state.resume_profile
                                    )
                            },
                            timeout=300
                        )

                        if response.status_code != 200:

                            st.error(
                                f"Backend Error: "
                                f"{response.status_code}"
                            )

                            st.text(
                                response.text
                            )

                        else:

                            match_result = response.json()

                            if match_result.get(
                                "success"
                            ):

                                st.session_state.job_match = (
                                    match_result.get(
                                        "match",
                                        {}
                                    )
                                )

                            else:

                                st.error(
                                    match_result.get(
                                        "error",
                                        "Unable to analyze the job."
                                    )
                                )

                    except requests.exceptions.Timeout:

                        st.error(
                            "The job match analysis took too long. "
                            "Please try again."
                        )

                    except Exception as e:

                        st.error(
                            f"Unable to analyze job: {str(e)}"
                        )


        # ==================================
        # MATCH REPORT
        # ==================================

        if st.session_state.job_match:

            match = st.session_state.job_match

            st.divider()

            st.subheader(
                "📊 Match Report"
            )

            # ==================================
            # OVERALL SCORE
            # ==================================

            score = match.get(
                "match_score",
                0
            )

            st.metric(
                "Overall Match",
                f"{score}%"
            )


            # ==================================
            # SUMMARY
            # ==================================

            summary = match.get(
                "summary",
                ""
            )

            if summary:

                st.info(
                    summary
                )


            # ==================================
            # MATCH BREAKDOWN
            # ==================================

            st.subheader(
                "Match Breakdown"
            )

            breakdown = [
                (
                    "Experience",
                    "experience_match"
                ),
                (
                    "Projects",
                    "project_match"
                ),
                (
                    "Technical Skills",
                    "technical_match"
                ),
                (
                    "Responsibilities",
                    "responsibility_match"
                ),
                (
                    "Seniority",
                    "seniority_match"
                )
            ]

            cols = st.columns(
                len(breakdown)
            )

            for index, (
                label,
                key
            ) in enumerate(
                breakdown
            ):

                data = match.get(
                    key,
                    {}
                )

                if not isinstance(
                    data,
                    dict
                ):

                    continue

                sub_score = data.get(
                    "score",
                    0
                )

                with cols[index]:

                    st.metric(
                        label,
                        f"{sub_score}%"
                    )

            # ==================================
            # STRONG MATCHES
            # ==================================

            strong_matches = match.get(
                "strong_matches",
                []
            )

            if strong_matches:

                st.subheader(
                    "Strong Matches"
                )

                for item in strong_matches:

                    if isinstance(
                        item,
                        dict
                    ):

                        skill = item.get(
                            "skill",
                            ""
                        )

                        reason = item.get(
                            "reason",
                            ""
                        )

                        st.success(
                            f"**{skill}** — {reason}"
                        )


            # ==================================
            # PARTIAL MATCHES
            # ==================================

            partial_matches = match.get(
                "partial_matches",
                []
            )

            if partial_matches:

                st.subheader(
                    "Partial Matches"
                )

                for item in partial_matches:

                    if isinstance(
                        item,
                        dict
                    ):

                        skill = item.get(
                            "skill",
                            ""
                        )

                        reason = item.get(
                            "reason",
                            ""
                        )

                        st.warning(
                            f"**{skill}** — {reason}"
                        )


            # ==================================
            # MISSING SKILLS
            # ==================================

            missing_skills = match.get(
                "missing_skills",
                []
            )

            if missing_skills:

                st.subheader(
                    "Missing Skills"
                )

                for item in missing_skills:

                    if isinstance(
                        item,
                        dict
                    ):

                        skill = item.get(
                            "skill",
                            ""
                        )

                        reason = item.get(
                            "reason",
                            ""
                        )

                        st.error(
                            f"**{skill}** — {reason}"
                        )


# ==================================
# SAVED JOBS PAGE
# ==================================

elif page == "Saved Jobs":

    st.title(
        "💼 Saved Jobs"
    )

    try:

        response = requests.get(
            "http://127.0.0.1:8000/jobs",
            timeout=30
        )

        if response.status_code != 200:

            st.error(
                f"Unable to load jobs: "
                f"{response.status_code}"
            )

        else:

            jobs_data = response.json()

            jobs = jobs_data.get(
                "jobs",
                []
            )

            if len(jobs) == 0:

                st.info(
                    "No jobs saved yet."
                )

            else:

                for job in jobs:

                    st.subheader(
                        f"{job['company']} - {job['role']}"
                    )

                    st.write(
                        f"📍 Location: {job['location']}"
                    )

                    st.write(
                        f"📌 Status: {job['status']}"
                    )

                    if job.get(
                        "date_discovered"
                    ):

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
                                f"http://127.0.0.1:8000/jobs/{job['id']}",
                                timeout=30
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

    st.title(
        "👥 Connections"
    )

    st.info(
        "Connections module coming soon."
    )


# ==================================
# OUTREACH PAGE
# ==================================

elif page == "Outreach":

    st.title(
        "📨 Outreach"
    )

    st.info(
        "Outreach module coming soon."
    )