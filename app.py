import streamlit as st
import pandas as pd
import numpy as np
from utils import (
    load_resume_text, clean_text, match_score, extract_skills,
    skill_gap, generate_bullets, summarize_sections
)

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

st.title("🧠 AI-Powered Resume Analyzer")
st.caption("Upload your resume and paste a job description to get a match score, skill gap analysis, and tailored bullet suggestions.")

with st.sidebar:
    st.header("Inputs")
    uploaded_resume = st.file_uploader("Upload Resume (PDF, DOCX, TXT)", type=["pdf", "docx", "doc", "txt"])
    role = st.text_input("Target Role (optional)", placeholder="e.g., Senior ML Engineer")
    company = st.text_input("Company (optional)", placeholder="e.g., Acme Corp")
    st.markdown("---")
    st.caption("Paste the job description below:")
    job_desc = st.text_area("Job Description", height=280, placeholder="Paste the full JD here...")

process = st.button("Analyze Resume", use_container_width=True)

if process:
    if not uploaded_resume or not job_desc.strip():
        st.error("Please upload a resume and paste a job description.")
        st.stop()

    # Read resume text
    try:
        resume_raw = load_resume_text(uploaded_resume)
    except Exception as e:
        st.error(f"Failed to read resume: {e}")
        st.stop()

    # Compute match score
    score = match_score(resume_raw, job_desc)

    # Extract skills
    resume_sk = extract_skills(resume_raw)
    overlap, missing = skill_gap(resume_sk, job_desc)

    # Bullets
    bullets = generate_bullets(role, company, resume_raw, job_desc, top_n=5)

    # Layout
    col1, col2 = st.columns([1,1])

    with col1:
        st.subheader("🎯 Match Score")
        st.metric("Resume ↔ JD similarity", f"{score:.1f}%")
        st.progress(min(100, max(0, int(score))))

        st.subheader("🧩 Skill Coverage")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Matched Skills**")
            if overlap:
                st.success(", ".join(overlap))
            else:
                st.info("No explicit matches found.")
        with c2:
            st.markdown("**Missing (Mention These)**")
            if missing:
                st.warning(", ".join(missing))
            else:
                st.success("No obvious gaps detected.")

        st.subheader("📝 Tailored Bullet Suggestions")
        for b in bullets:
            st.write(f"- {b}")

    with col2:
        st.subheader("🔍 Readability & ATS Tips")
        sections = summarize_sections(resume_raw)
        tips = []
        if len(resume_raw) < 800:
            tips.append("Your resume looks short; consider adding impact bullets with metrics (2–4 per role).")
        if "summary" not in sections or not sections["summary"]:
            tips.append("Add a 2–3 line professional summary tailored to the role/company.")
        if not overlap:
            tips.append("Mirror exact phrasing of key skills from the JD (where true) to improve ATS matching.")
        if "python" in (s.lower() for s in missing):
            tips.append("If you have Python experience, explicitly mention versions/libraries to pass keyword scans.")
        if not tips:
            tips.append("Overall structure looks fine. Tighten bullets to show measurable impact and scale.")
        for t in tips:
            st.write("• " + t)

        st.subheader("📄 Extracted Resume Text (preview)")
        with st.expander("Show/Hide"):
            st.text(resume_raw[:6000])

    # Downloadable analysis (CSV)
    result_df = pd.DataFrame({
        "metric": ["match_score_pct", "matched_skills", "missing_skills"],
        "value": [
            f"{score:.2f}",
            ", ".join(overlap) if overlap else "",
            ", ".join(missing) if missing else ""
        ]
    })
    st.download_button(
        "⬇️ Download analysis (CSV)",
        data=result_df.to_csv(index=False).encode("utf-8"),
        file_name="resume_analysis.csv",
        mime="text/csv",
        use_container_width=True
    )

else:
    st.info("Upload a resume and paste a job description, then click **Analyze Resume**.")
    st.write("Tip: fine-tune `skills_db.py` to match the roles you’re targeting (e.g., GenAI, MLOps, etc.).")
