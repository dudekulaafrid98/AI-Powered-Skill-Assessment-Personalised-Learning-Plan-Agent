import os
import re
import json
import tempfile
import random
from typing import List, Dict, Optional, Any
from uuid import uuid4
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

load_dotenv()

app = FastAPI(title="AI Skill Assessment & Learning Plan Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS: Dict[str, Dict[str, Any]] = {}

SKILL_BANK = {
    "python": ["python", "pandas", "numpy", "fastapi", "flask", "django"],
    "java": ["java", "spring boot", "spring", "hibernate", "jpa", "maven"],
    "javascript": ["javascript", "typescript", "react", "node", "express", "vite"],
    "sql": ["sql", "mysql", "postgresql", "database", "dbms", "queries"],
    "machine learning": ["machine learning", "ml", "classification", "regression", "model", "scikit"],
    "deep learning": ["deep learning", "pytorch", "tensorflow", "neural", "transformer"],
    "llm": ["llm", "rag", "openai", "gemini", "langchain", "embeddings", "vector database"],
    "docker": ["docker", "container", "dockerfile", "compose"],
    "cloud deployment": ["aws", "azure", "gcp", "render", "vercel", "netlify", "deployment"],
    "git": ["git", "github", "version control", "pull request"],
    "rest api": ["rest", "api", "restful", "endpoint", "http"],
    "data structures": ["data structures", "algorithms", "dsa", "arrays", "trees", "graphs"],
    "nlp": ["nlp", "natural language", "text classification", "tokenization"],
    "testing": ["testing", "unit test", "pytest", "junit", "mockito"],
}

QUESTION_BANK = {
    "python": [
        "Explain the difference between a list, tuple, and dictionary in Python with one use case each.",
        "How would you handle missing values in a Pandas DataFrame?",
        "Write the high-level steps to build a simple FastAPI endpoint.",
        "What is the difference between deep copy and shallow copy in Python?",
        "How do you handle exceptions in Python?",
        "What are Python virtual environments and why are they useful?"
    ],
    "java": [
        "Explain OOP concepts using a Java example.",
        "What is dependency injection in Spring Boot and why is it useful?",
        "How do Controller, Service, and Repository layers work together?",
        "What is the difference between interface and abstract class?",
        "Explain JPA Entity and Repository in simple terms.",
        "How would you handle exceptions globally in Spring Boot?"
    ],
    "javascript": [
        "Explain state and props in React.",
        "How does async/await work in JavaScript?",
        "What is the role of Vite in a React app?",
        "What is the difference between let, const, and var?",
        "Explain useEffect in React.",
        "How do you call a backend API from React?"
    ],
    "sql": [
        "Explain INNER JOIN vs LEFT JOIN with an example.",
        "How would you design tables for users and orders?",
        "What are indexes and when would you use them?",
        "What is the difference between primary key and foreign key?",
        "Explain GROUP BY and HAVING with an example.",
        "How would you avoid duplicate records in a table?"
    ],
    "machine learning": [
        "Explain train/validation/test split and why it matters.",
        "What is overfitting and how can you reduce it?",
        "Which metrics would you use for an imbalanced classification problem?",
        "What is the difference between classification and regression?",
        "Explain precision, recall, and F1-score.",
        "Why do we normalize or scale features before training?"
    ],
    "deep learning": [
        "Explain epochs, batch size, and learning rate.",
        "What is transfer learning and when is it useful?",
        "How would you debug a model whose validation accuracy is not improving?",
        "What is the role of activation functions?",
        "What is dropout and why is it used?",
        "What is the difference between CNN and Transformer at a high level?"
    ],
    "llm": [
        "Explain RAG in simple terms.",
        "What are embeddings and why are they useful?",
        "How would you evaluate the quality of an LLM-based answer?",
        "What is prompt engineering?",
        "Why can LLMs hallucinate?",
        "What is the role of vector databases in RAG?"
    ],
    "docker": [
        "What problem does Docker solve?",
        "What is the difference between an image and a container?",
        "What are the main parts of a Dockerfile?",
        "What is Docker Compose and when would you use it?",
        "How would you containerize a backend application?",
        "What is the difference between COPY and RUN in a Dockerfile?"
    ],
    "cloud deployment": [
        "What files/configuration are usually needed to deploy a backend?",
        "How do environment variables help in deployment?",
        "How would you debug a failed deployment?",
        "What is the difference between frontend and backend deployment?",
        "Why should secret keys not be hardcoded?",
        "How would you check logs after deployment?"
    ],
    "git": [
        "Explain git commit, branch, merge, and pull request.",
        "How would you resolve a merge conflict?",
        "Why should sensitive keys not be committed?",
        "What is the difference between git pull and git fetch?",
        "Why do teams use branches?",
        "How would you undo a wrong commit?"
    ],
    "rest api": [
        "Explain GET, POST, PUT, and DELETE.",
        "What status codes would you use for success, validation error, and not found?",
        "How would you secure an API endpoint?",
        "What is the difference between authentication and authorization?",
        "What is JWT and why is it used?",
        "How would you design CRUD APIs for a books table?"
    ],
    "data structures": [
        "When would you use a hash map instead of an array?",
        "Explain time complexity using binary search.",
        "Which data structure would you use for BFS and why?",
        "What is the difference between stack and queue?",
        "Explain linked list vs array.",
        "When would you use a tree data structure?"
    ],
    "nlp": [
        "What is tokenization?",
        "How would you preprocess text before model training?",
        "What is the difference between keyword search and semantic search?",
        "What are stop words?",
        "What is stemming or lemmatization?",
        "How are embeddings useful in NLP?"
    ],
    "testing": [
        "Why do we write unit tests?",
        "What is mocking in tests?",
        "What should you test in a REST API?",
        "What is the difference between unit testing and integration testing?",
        "How would you test a login API?",
        "Why is automated testing useful in real projects?"
    ],
}

RESOURCE_BANK = {
    "python": ["Python official tutorial", "freeCodeCamp Python crash course", "Build one FastAPI CRUD API"],
    "java": ["Spring Boot official guides", "Java OOP practice problems", "Build layered CRUD API"],
    "javascript": ["React official learn docs", "JavaScript.info async/await", "Build small React dashboard"],
    "sql": ["SQLBolt", "PostgreSQL SELECT/JOIN docs", "Design 3-table mini database"],
    "machine learning": ["Google Machine Learning Crash Course", "Kaggle intro to ML", "Train a classification model"],
    "deep learning": ["PyTorch beginner tutorials", "fast.ai practical deep learning", "Fine-tune a small model"],
    "llm": ["OpenAI prompting guide", "LangChain RAG tutorial", "Build PDF Q&A mini project"],
    "docker": ["Docker get started guide", "Dockerfile best practices", "Containerize one backend app"],
    "cloud deployment": ["Render deployment docs", "Vercel deployment docs", "Deploy backend + frontend demo"],
    "git": ["GitHub Git handbook", "Learn Git Branching", "Create branches and PRs"],
    "rest api": ["MDN HTTP methods", "REST API design guide", "Build CRUD endpoints"],
    "data structures": ["NeetCode roadmap", "Visualgo data structures", "Solve 10 easy DSA problems"],
    "nlp": ["Hugging Face NLP course", "Sentence Transformers docs", "Build text search demo"],
    "testing": ["Pytest docs", "JUnit 5 user guide", "Write tests for API endpoints"],
}

class StartRequest(BaseModel):
    jd: str
    resume: str

class Answer(BaseModel):
    skill: str
    question: str
    answer: str

class SubmitAssessmentRequest(BaseModel):
    session_id: str
    answers: List[Answer]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def extract_skills(text: str) -> List[str]:
    t = normalize(text)
    found = []
    for skill, aliases in SKILL_BANK.items():
        for alias in aliases:
            if re.search(r"\b" + re.escape(alias.lower()) + r"\b", t):
                found.append(skill)
                break
    # Also catch common comma separated skills after keywords
    extra_candidates = re.findall(r"(?:skills|required|requirements|tech stack)[:\-]?\s*([^\.\n]+)", text, flags=re.I)
    for chunk in extra_candidates:
        for part in re.split(r"[,/;|]", chunk):
            p = part.strip().lower()
            if 2 <= len(p) <= 30:
                for skill, aliases in SKILL_BANK.items():
                    if p == skill or p in aliases:
                        found.append(skill)
    return sorted(set(found))


def evidence_score(skill: str, resume: str) -> int:
    t = normalize(resume)
    aliases = SKILL_BANK.get(skill, [skill])
    mentions = sum(t.count(a) for a in aliases)
    project_bonus = 1 if re.search(r"project|built|developed|implemented|deployed|created", t) else 0
    if mentions == 0:
        return 0
    return min(5, 2 + mentions + project_bonus)


def score_answer(skill: str, answer: str) -> int:
    if not answer or len(answer.strip()) < 20:
        return 1

    ans = normalize(answer)

    CONCEPT_BANK = {
        "rest api": [
            "get", "post", "put", "delete", "http", "endpoint",
            "jwt", "token", "authentication", "authorization",
            "status code", "request", "response", "secure"
        ],
        "docker": [
            "dockerfile", "image", "container", "compose", "port",
            "dependencies", "build", "run", "environment"
        ],
        "git": [
            "commit", "branch", "merge", "pull request", "repository",
            "conflict", "github", "version control", "secret", "keys"
        ],
        "llm": [
            "rag", "embedding", "vector", "prompt", "context",
            "retrieval", "database", "hallucination", "llm"
        ],
        "machine learning": [
            "train", "validation", "test", "overfitting", "precision",
            "recall", "f1", "accuracy", "confusion matrix", "imbalanced"
        ],
        "python": [
            "list", "tuple", "dictionary", "pandas", "dataframe",
            "missing", "exception", "try", "except", "fillna", "dropna"
        ],
        "sql": [
            "join", "group by", "having", "primary key", "foreign key",
            "table", "query", "users", "orders", "index"
        ],
    }

    keywords = CONCEPT_BANK.get(skill, SKILL_BANK.get(skill, [skill]))

    hit = sum(1 for k in keywords if k in ans)

    explanation_bonus = 1 if any(
        w in ans for w in ["because", "example", "use", "when", "difference", "steps"]
    ) else 0

    length_bonus = 1 if len(ans.split()) >= 25 else 0

    if hit >= 4:
        base = 5
    elif hit == 3:
        base = 4
    elif hit == 2:
        base = 3
    elif hit == 1:
        base = 2
    else:
        base = 1

    return min(5, base + explanation_bonus + length_bonus)


def level(score: int) -> str:
    if score >= 8:
        return "Strong"
    if score >= 6:
        return "Intermediate"
    if score >= 4:
        return "Basic"
    return "Gap"


def create_questions(required_skills: List[str]) -> List[Dict[str, str]]:
    questions = []

    for skill in required_skills[:8]:
        skill_questions = QUESTION_BANK.get(
            skill,
            [f"Explain your practical experience with {skill}."]
        )

        # Pick random 2 questions from larger question bank
        selected = random.sample(skill_questions, min(2, len(skill_questions)))

        for q in selected:
            questions.append({
                "skill": skill,
                "question": q
            })

    return questions


def make_learning_plan(scores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    plan = []
    for item in scores:
        if item["score"] >= 7:
            continue
        skill = item["skill"]
        gap = 7 - item["score"]
        days = max(2, min(10, gap * 2))
        plan.append({
            "skill": skill,
            "current_level": item["level"],
            "target_level": "Job-ready intermediate",
            "estimated_time": f"{days} days",
            "focus": f"Build practical confidence in {skill} through one small project and revision of fundamentals.",
            "steps": [
                f"Day 1-{max(1, days//3)}: Learn/revise {skill} fundamentals",
                f"Day {max(2, days//3+1)}-{max(2, 2*days//3)}: Practice interview-style questions and examples",
                f"Final days: Build a mini project that proves {skill} proficiency"
            ],
            "resources": RESOURCE_BANK.get(skill, ["Official documentation", "Beginner crash course", "Mini project practice"])
        })
    return plan


def build_report(session: Dict[str, Any], answers: List[Answer]) -> Dict[str, Any]:
    ans_by_skill: Dict[str, List[Answer]] = {}
    for a in answers:
        ans_by_skill.setdefault(a.skill, []).append(a)

    scores = []
    for skill in session["required_skills"]:
        ev = evidence_score(skill, session["resume"])
        answer_scores = [score_answer(skill, a.answer) for a in ans_by_skill.get(skill, [])]
        avg_assessment = round(sum(answer_scores) / len(answer_scores), 1) if answer_scores else 0
        final = round((ev * 0.4) + (avg_assessment * 0.6))
        final = max(0, min(10, final * 2))  # convert rough 0-5 scale to 0-10
        scores.append({
            "skill": skill,
            "resume_evidence_score": ev * 2,
            "assessment_score": int(avg_assessment * 2),
            "score": final,
            "level": level(final),
            "gap": max(0, 7 - final)
        })
    job_fit = round(sum(s["score"] for s in scores) / (len(scores) * 10) * 100) if scores else 0
    gaps = [s for s in scores if s["score"] < 7]
    strengths = [s for s in scores if s["score"] >= 7]
    return {
        "candidate_summary": "Candidate assessed against JD-required skills using resume evidence and conversational answers.",
        "required_skills": session["required_skills"],
        "resume_skills": session["resume_skills"],
        "job_fit_percentage": job_fit,
        "scores": scores,
        "strengths": strengths,
        "gaps": gaps,
        "learning_plan": make_learning_plan(scores),
        "scoring_logic": "Final score combines 40% resume evidence and 60% assessment answer quality. Scores below 7/10 are treated as skill gaps."
    }


def read_upload(file: UploadFile) -> str:
    """Read uploaded resume safely on Windows/Linux. Supports PDF and TXT."""
    content = file.file.read()
    name = (file.filename or "").lower()

    if not content:
        return ""

    if name.endswith(".pdf"):
        if not PdfReader:
            raise ValueError("PDF support is not installed. Run: pip install pypdf")

        temp_path = None
        try:
            # tempfile works on Windows, Linux, Render, and avoids hardcoded /tmp issues.
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
                temp.write(content)
                temp_path = temp.name

            reader = PdfReader(temp_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text.strip()
        finally:
            if temp_path:
                Path(temp_path).unlink(missing_ok=True)

    return content.decode("utf-8", errors="ignore").strip()

@app.get("/")
def root():
    return {"message": "AI Skill Assessment Agent API is running"}

@app.post("/api/start")
def start(req: StartRequest):
    required = extract_skills(req.jd)
    resume_skills = extract_skills(req.resume)
    if not required:
        required = ["python", "sql", "rest api", "git"]
    sid = str(uuid4())
    SESSIONS[sid] = {"jd": req.jd, "resume": req.resume, "required_skills": required, "resume_skills": resume_skills}
    return {"session_id": sid, "required_skills": required, "resume_skills": resume_skills, "questions": create_questions(required)}

@app.post("/api/start-upload")
def start_upload(jd: str = Form(...), resume_file: UploadFile = File(...)):
    try:
        resume = read_upload(resume_file)
    except ValueError as e:
        return {"error": str(e)}

    if not resume:
        return {"error": "Could not extract text from the uploaded resume. Try uploading a text-based PDF or paste resume text manually."}

    return start(StartRequest(jd=jd, resume=resume))

@app.post("/api/submit")
def submit(req: SubmitAssessmentRequest):
    session = SESSIONS.get(req.session_id)
    if not session:
        return {"error": "Invalid session_id"}
    return build_report(session, req.answers)

@app.get("/api/sample")
def sample():
    return {
        "jd": "AI Engineer Intern required skills: Python, SQL, Machine Learning, LLM, RAG, Git, REST API, Docker.",
        "resume": "CSE student skilled in Python, Java, React and SQL. Built ML classification projects and REST APIs. Used GitHub for projects. Beginner in Docker and RAG."
    }
