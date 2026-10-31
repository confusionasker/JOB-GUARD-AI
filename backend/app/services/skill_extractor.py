import re
from typing import List, Set, Dict

# Canonical Skill Taxonomy & Aliases
TECH_ALIASES: Dict[str, str] = {
    # Programming Languages
    "python": "Python",
    "python3": "Python",
    "py": "Python",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "ruby": "Ruby",
    "php": "PHP",
    "scala": "Scala",
    "kotlin": "Kotlin",
    "swift": "Swift",
    
    # Frontend Frameworks & Libraries
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "svelte": "Svelte",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "redux": "Redux",
    "html": "HTML5",
    "html5": "HTML5",
    "css": "CSS3",
    "css3": "CSS3",
    
    # Backend Frameworks
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "express": "Express.js",
    "expressjs": "Express.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "node": "Node.js",
    "nestjs": "NestJS",
    "spring": "Spring Boot",
    "springboot": "Spring Boot",
    "spring boot": "Spring Boot",
    "asp.net": "ASP.NET",
    ".net": ".NET",
    "rails": "Ruby on Rails",
    "laravel": "Laravel",

    # Databases & Storage
    "sql": "SQL",
    "mysql": "MySQL",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "psql": "PostgreSQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "sqlite": "SQLite",
    "cassandra": "Cassandra",
    "dynamodb": "DynamoDB",
    "elasticsearch": "Elasticsearch",
    "oracle": "Oracle DB",

    # Cloud, DevOps & Tools
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "jenkins": "Jenkins",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "linux": "Linux",
    "nginx": "Nginx",
    "rest": "REST API",
    "rest api": "REST API",
    "restful": "REST API",
    "graphql": "GraphQL",
    "kafka": "Apache Kafka",
    "rabbitmq": "RabbitMQ",

    # AI, ML & Data Science
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "keras": "Keras",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "pandas": "pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "opencv": "OpenCV",
    "llm": "LLMs",
    "llms": "LLMs",
    "langchain": "LangChain",
    "transformers": "Hugging Face Transformers",
    "huggingface": "Hugging Face Transformers",
    "cnn": "CNN (Convolutional Neural Networks)",
    "convolutional neural network": "CNN (Convolutional Neural Networks)",
    "cbam": "Attention Mechanisms (CBAM)",
    "attention module": "Attention Mechanisms",
    "attention mechanism": "Attention Mechanisms",
    "computer vision": "Computer Vision",
    "artificial intelligence": "Artificial Intelligence",
    "ai": "Artificial Intelligence",
    "neural network": "Neural Networks",
    "neural networks": "Neural Networks",
    "image processing": "Image Processing",
    "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",
    "data science": "Data Science",

    # Computer Science Fundamentals & Core Subjects
    "dbms": "DBMS",
    "rdbms": "RDBMS",
    "oops": "OOP (Object-Oriented Programming)",
    "oop": "OOP (Object-Oriented Programming)",
    "oops concept": "OOP (Object-Oriented Programming)",
    "object oriented programming": "OOP (Object-Oriented Programming)",
    "data structures": "Data Structures",
    "algorithms": "Algorithms",
    "dsa": "Data Structures & Algorithms",
    "operating system": "Operating Systems",
    "operating systems": "Operating Systems",
    "computer networks": "Computer Networks",
    "system design": "System Design",

    # Tools, IDEs & Platforms
    "google colab": "Google Colab",
    "colab": "Google Colab",
    "visual studio": "Visual Studio",
    "microsoft visual studio": "Visual Studio",
    "vscode": "VS Code",
    "vs code": "VS Code",
    "jupyter": "Jupyter Notebook",
    "jupyter notebook": "Jupyter Notebook",
    "postman": "Postman",
    "web development": "Web Development"
}

class SkillExtractor:
    def __init__(self):
        # Pre-compile regex patterns for boundary-sensitive matching
        self.patterns = {}
        for alias, canonical in TECH_ALIASES.items():
            # Escape symbols like ++ or #
            escaped = re.escape(alias)
            # Use word boundaries or specific symbol boundaries
            if alias in ["c++", "c#", ".net", "ci/cd"]:
                pattern = rf"(?i)(?:\b|(?<=\s)){escaped}(?=\s|[.,;:\)]|$)"
            else:
                pattern = rf"(?i)\b{escaped}\b"
            self.patterns[pattern] = canonical

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract and canonicalize technology skills from plain text.
        """
        if not text:
            return []

        found_skills: Set[str] = set()

        # Match all canonical patterns
        for pattern_str, canonical in self.patterns.items():
            if re.search(pattern_str, text):
                found_skills.add(canonical)

        # Precise boundary check for programming language C
        if (
            re.search(r"(?i)\bLanguage[s]?\b[^\n]*\bC\b", text) or
            re.search(r"(?i)\bC\s*,\s*C\+\+", text) or
            re.search(r"(?i)(?:^|[\s,;/])C[\s,;/]+(?:C\+\+|Java|Python|SQL|C#)", text) or
            re.search(r"(?i)\b(?:C|C\+\+)\s+programming\b", text)
        ):
            found_skills.add("C")

        # Sort alphabetically for consistent deterministic output
        return sorted(list(found_skills))

    def normalize_skill_name(self, raw_skill: str) -> str:
        """Normalize an individual skill string (e.g. 'postgres' -> 'PostgreSQL')."""
        cleaned = raw_skill.strip().lower()
        return TECH_ALIASES.get(cleaned, raw_skill.strip())

skill_extractor = SkillExtractor()

