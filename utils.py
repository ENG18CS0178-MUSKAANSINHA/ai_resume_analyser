import io
import re
import pdfplumber
import docx
import numpy as np
import pandas as pd
from typing import Tuple, List, Dict
from unidecode import unidecode
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from skills_db import ALL_SKILLS

# ---------------------------
# File -> Text extractors
# ---------------------------
def read_pdf(file_bytes: bytes) -> str:
    text_chunks = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            text_chunks.append(text)
    return "\n".join(text_chunks)

def read_docx(file_bytes: bytes) -> str:
    f = io.BytesIO(file_bytes)
    document = docx.Document(f)
    return "\n".join(p.text for p in document.paragraphs)

def read_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")

def load_resume_text(uploaded_file) -> str:
    suffix = uploaded_file.name.lower().split(".")[-1]
    data = uploaded_file.read()
    if suffix == "pdf":
        return read_pdf(data)
    elif suffix in ("docx", "doc"):
        return read_docx(data)
    elif suffix in ("txt",):
        return read_txt(data)
    else:
        raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")

# ---------------------------
# Cleaning & normalization
# ---------------------------
PUNCT_RE = re.compile(r"[^a-z0-9\s\.\-\+/#]")

def clean_text(text: str) -> str:
    text = unidecode(text or "")
    text = text.lower()
    text = PUNCT_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ---------------------------
# Skill extraction (simple)
# ---------------------------
def extract_skills(text: str) -> List[str]:
    text_lc = " " + clean_text(text) + " "
    found = set()
    # Match whole-word or token skill substrings
    for sk in ALL_SKILLS:
        # allow symbols like c++, ci/cd via simple contains after cleaning
        if f" {sk} " in text_lc:
            found.add(sk)
        else:
            # minor heuristic for symbols inside words (c++, ci/cd)
            if sk in text_lc:
                found.add(sk)
    return sorted(found)

# ---------------------------
# TF-IDF similarity
# ---------------------------
def match_score(resume_text: str, job_text: str) -> float:
    docs = [clean_text(job_text), clean_text(resume_text)]
    tfidf = TfidfVectorizer(ngram_range=(1,2), min_df=1, stop_words="english")
    mat = tfidf.fit_transform(docs)
    sim = cosine_similarity(mat[0:1], mat[1:2])[0,0]
    return float(sim) * 100.0  # percentage

# ---------------------------
# Gap analysis & suggestions
# ---------------------------
def skill_gap(resume_skills: List[str], job_text: str) -> Tuple[List[str], List[str]]:
    job_text_clean = clean_text(job_text)
    job_skills = [s for s in ALL_SKILLS if s in job_text_clean]
    missing = sorted(set(job_skills) - set(resume_skills))
    overlapping = sorted(set(job_skills) & set(resume_skills))
    return overlapping, missing

def generate_bullets(role: str, company: str, resume_text: str, job_text: str, top_n: int = 4) -> List[str]:
    # Heuristic bullets using action + impact + metric templates
    # (You can swap this out for an LLM later if you want.)
    verbs = ["Built", "Led", "Optimized", "Automated", "Deployed", "Scaled", "Improved"]
    impacts = [
        "reduced processing time by {x}%", "cut costs by {x}%", "increased accuracy by {x}%",
        "boosted throughput by {x}x", "improved reliability to {x}% uptime",
        "shortened lead time by {x}%"
    ]
    examples = []
    rng = np.random.default_rng(42)
    for _ in range(top_n):
        v = rng.choice(verbs)
        im = rng.choice(impacts).format(x=rng.integers(10, 80))
        examples.append(f"{v} a solution relevant to {role or 'the role'} at {company or 'the company'} and {im}.")
    return examples

def summarize_sections(resume_text: str) -> Dict[str, str]:
    # Extremely simple section splitter to help ATS hints
    txt = clean_text(resume_text)
    sections = {
        "summary": "",
        "experience": "",
        "projects": "",
        "skills": "",
        "education": ""
    }
    # naive splits
    for key in sections.keys():
        m = re.search(rf"{key}\s*[:\-]?", txt)
        if m:
            start = m.start()
            sections[key] = txt[start:start+1000]
    return sections
