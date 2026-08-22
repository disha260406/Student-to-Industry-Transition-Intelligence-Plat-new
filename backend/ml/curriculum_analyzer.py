"""
Curriculum Analyzer
Extracts subjects/topics from a college program PDF and compares with industry job requirements.
"""
import re
import io

# Industry skill requirements by domain
INDUSTRY_REQUIREMENTS = {
    "Web Development": {
        "skills": ["html", "css", "javascript", "react", "nodejs", "rest api", "sql", "git", "typescript", "docker"],
        "levels": {"html": "Basic", "css": "Basic", "javascript": "Intermediate", "react": "Intermediate",
                   "nodejs": "Intermediate", "rest api": "Intermediate", "sql": "Basic", "git": "Basic",
                   "typescript": "Advanced", "docker": "Advanced"}
    },
    "Data Science": {
        "skills": ["python", "machine learning", "statistics", "pandas", "numpy", "sql", "data visualization",
                   "deep learning", "nlp", "big data"],
        "levels": {"python": "Intermediate", "machine learning": "Advanced", "statistics": "Intermediate",
                   "pandas": "Intermediate", "numpy": "Intermediate", "sql": "Basic",
                   "data visualization": "Intermediate", "deep learning": "Advanced",
                   "nlp": "Advanced", "big data": "Advanced"}
    },
    "Software Engineering": {
        "skills": ["data structures", "algorithms", "object oriented programming", "design patterns",
                   "system design", "git", "testing", "agile", "sql", "cloud"],
        "levels": {"data structures": "Intermediate", "algorithms": "Intermediate",
                   "object oriented programming": "Intermediate", "design patterns": "Advanced",
                   "system design": "Advanced", "git": "Basic", "testing": "Intermediate",
                   "agile": "Basic", "sql": "Basic", "cloud": "Intermediate"}
    },
    "DevOps / Cloud": {
        "skills": ["linux", "docker", "kubernetes", "ci/cd", "aws", "git", "networking", "scripting",
                   "monitoring", "security"],
        "levels": {"linux": "Intermediate", "docker": "Intermediate", "kubernetes": "Advanced",
                   "ci/cd": "Intermediate", "aws": "Intermediate", "git": "Basic",
                   "networking": "Intermediate", "scripting": "Intermediate",
                   "monitoring": "Intermediate", "security": "Advanced"}
    }
}

# Keyword → topic mapping for curriculum extraction
TOPIC_KEYWORDS = {
    "python": ["python", "py programming"],
    "java": ["java", "core java", "advanced java"],
    "c++": ["c++", "cpp", "c plus plus"],
    "c": [" c ", "c language", "c programming"],
    "javascript": ["javascript", "js", "ecmascript"],
    "html": ["html", "hypertext markup"],
    "css": ["css", "cascading style"],
    "sql": ["sql", "mysql", "database query", "rdbms", "relational database"],
    "data structures": ["data structure", "linked list", "stack", "queue", "tree", "graph", "heap"],
    "algorithms": ["algorithm", "sorting", "searching", "complexity", "dynamic programming"],
    "object oriented programming": ["oop", "object oriented", "class", "inheritance", "polymorphism", "encapsulation"],
    "machine learning": ["machine learning", "ml", "supervised", "unsupervised", "classification", "regression"],
    "deep learning": ["deep learning", "neural network", "cnn", "rnn", "lstm"],
    "statistics": ["statistics", "probability", "distribution", "hypothesis", "regression analysis"],
    "operating systems": ["operating system", "os", "process", "thread", "memory management", "scheduling"],
    "networking": ["networking", "network", "tcp/ip", "osi model", "protocol", "socket"],
    "software engineering": ["software engineering", "sdlc", "software development", "requirement analysis"],
    "design patterns": ["design pattern", "creational", "structural", "behavioral", "singleton", "factory"],
    "system design": ["system design", "scalability", "load balancer", "microservice"],
    "cloud": ["cloud", "aws", "azure", "gcp", "cloud computing"],
    "docker": ["docker", "container", "containerization"],
    "kubernetes": ["kubernetes", "k8s", "orchestration"],
    "git": ["git", "version control", "github", "gitlab"],
    "agile": ["agile", "scrum", "sprint", "kanban"],
    "testing": ["testing", "unit test", "test case", "selenium", "junit"],
    "linux": ["linux", "unix", "shell", "bash"],
    "security": ["security", "cryptography", "cybersecurity", "encryption"],
    "big data": ["big data", "hadoop", "spark", "hive", "kafka"],
    "nlp": ["nlp", "natural language", "text processing", "sentiment"],
    "data visualization": ["visualization", "matplotlib", "tableau", "power bi", "seaborn"],
    "pandas": ["pandas", "dataframe"],
    "numpy": ["numpy", "numerical computing"],
    "rest api": ["rest", "api", "web service", "http methods"],
    "react": ["react", "reactjs", "jsx", "component"],
    "nodejs": ["node.js", "nodejs", "express"],
    "typescript": ["typescript", "ts"],
    "ci/cd": ["ci/cd", "continuous integration", "continuous deployment", "jenkins", "github actions"],
    "scripting": ["scripting", "bash script", "shell script", "automation"],
    "monitoring": ["monitoring", "logging", "prometheus", "grafana"],
}

LEVEL_KEYWORDS = {
    "Basic": ["introduction", "basic", "fundamentals", "overview", "beginner", "foundation", "intro"],
    "Intermediate": ["intermediate", "applied", "practical", "implementation", "advanced concepts"],
    "Advanced": ["advanced", "expert", "optimization", "research", "specialization", "deep dive"]
}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using pdfplumber."""
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except ImportError:
        raise ImportError("pdfplumber is required. Run: pip install pdfplumber")
    except Exception as e:
        raise Exception(f"PDF extraction failed: {str(e)}")


def detect_level(context: str) -> str:
    """Detect depth level from surrounding text."""
    context_lower = context.lower()
    for level, keywords in LEVEL_KEYWORDS.items():
        if any(kw in context_lower for kw in keywords):
            return level
    return "Basic"


def extract_curriculum(text: str) -> dict:
    """Extract subjects and topics from curriculum text."""
    text_lower = text.lower()
    found_topics = {}

    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            idx = text_lower.find(kw)
            if idx != -1:
                # Grab surrounding context (100 chars) to detect level
                context = text_lower[max(0, idx - 80):idx + 80]
                level = detect_level(context)
                if topic not in found_topics:
                    found_topics[topic] = level
                else:
                    # Upgrade level if a higher one is found
                    levels = ["Basic", "Intermediate", "Advanced"]
                    if levels.index(level) > levels.index(found_topics[topic]):
                        found_topics[topic] = level
                break

    return found_topics


def compare_with_industry(curriculum_topics: dict) -> dict:
    """Compare extracted curriculum with industry requirements."""
    results = {}

    for domain, req in INDUSTRY_REQUIREMENTS.items():
        required_skills = req["skills"]
        required_levels = req["levels"]

        taught = []
        gaps = []
        level_gaps = []

        for skill in required_skills:
            if skill in curriculum_topics:
                curr_level = curriculum_topics[skill]
                req_level = required_levels.get(skill, "Intermediate")
                levels = ["Basic", "Intermediate", "Advanced"]
                taught.append({"skill": skill, "college_level": curr_level, "industry_level": req_level})
                if levels.index(curr_level) < levels.index(req_level):
                    level_gaps.append({
                        "skill": skill,
                        "college_level": curr_level,
                        "industry_level": req_level,
                        "gap": f"Need to go from {curr_level} → {req_level}"
                    })
            else:
                gaps.append({"skill": skill, "industry_level": required_levels.get(skill, "Intermediate")})

        enriched_taught = [
            {
                "skill": t["skill"],
                "college_level": t["college_level"],
                "level": t["college_level"],
                "industry_level": t["industry_level"]
            } for t in taught
        ]
        enriched_gaps = [
            {
                "skill": g["skill"],
                "industry_level": g["industry_level"],
                "required_level": g["industry_level"]
            } for g in gaps
        ]

        results[domain] = {
            "coverage_percent": coverage,
            "coverage_percentage": coverage,
            "taught_in_college": enriched_taught,
            "taught_skills": enriched_taught,
            "skill_gaps": enriched_gaps,
            "missing_skills": enriched_gaps,
            "level_gaps": level_gaps,
            "total_required": len(required_skills),
            "total_covered": len(taught),
            "taught_count": len(taught)
        }

    return results


def analyze_curriculum_pdf(file_bytes: bytes) -> dict:
    """Full pipeline: PDF → extract → compare → return analysis."""
    text = extract_text_from_pdf(file_bytes)
    if not text.strip():
        raise ValueError("Could not extract text from PDF. Make sure it's not a scanned image.")

    curriculum_topics = extract_curriculum(text)
    industry_comparison = compare_with_industry(curriculum_topics)

    # Best matching domain
    best_domain = max(industry_comparison, key=lambda d: industry_comparison[d]["coverage_percent"])

    return {
        "success": True,
        "topics_found": len(curriculum_topics),
        "curriculum_topics": curriculum_topics,
        "industry_comparison": industry_comparison,
        "best_matching_domain": best_domain,
        "best_coverage": industry_comparison[best_domain]["coverage_percent"]
    }
