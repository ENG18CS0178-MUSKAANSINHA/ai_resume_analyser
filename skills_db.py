# A lightweight, editable skills dictionary.
# Add/remove items to fit your domain or target roles.

CORE_SKILLS = {
    "programming": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "sql",
        "bash", "shell", "powershell"
    ],
    "data_ai": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "pandas", "numpy", "scikit-learn", "pytorch", "tensorflow",
        "xgboost", "lightgbm", "transformers", "llm", "rag", "langchain"
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd", "github actions"
    ],
    "web_backend": [
        "react", "next.js", "node.js", "express", "fastapi", "flask", "django", "graphql", "rest"
    ],
    "analytics_bi": [
        "power bi", "tableau", "looker", "superset", "dbt", "airflow", "etl"
    ],
    "soft": [
        "stakeholder management", "communication", "mentorship",
        "team leadership", "agile", "scrum", "product thinking"
    ]
}

# Flatten to a set for quick membership checks
ALL_SKILLS = set(s.lower() for cat in CORE_SKILLS.values() for s in cat)
