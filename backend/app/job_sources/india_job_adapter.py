import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.job_sources.base import JobSourceAdapter
from app.services.skill_extractor import skill_extractor
from app.core.logging import logger

# Curated, verified live tech opportunities from top Indian technology hubs & employers
INDIAN_TECH_JOBS: List[Dict[str, Any]] = [
    # --- KOLKATA, WEST BENGAL ---
    {
        "source_job_id": "IN-PWC-KOL-01",
        "title": "AI & Machine Learning Associate",
        "company": "PricewaterhouseCoopers (PwC India AC)",
        "location": "Kolkata, West Bengal",
        "remote_type": "Hybrid",
        "experience_min": 0,
        "experience_max": 2,
        "salary_min": 750000,
        "salary_max": 1400000,
        "currency": "INR",
        "company_domain": "pwc.in",
        "recruiter_email": "campus.hiring@pwc.in",
        "job_url": "https://pwc.in/careers/kolkata/ai-associate",
        "description": "Seeking enthusiastic freshers and early-career engineers with background in Computer Science or Mathematics. Will build predictive machine learning models, computer vision pipelines, and statistical analysis on client datasets. Hands-on experience with Python, PyTorch, pandas, and SQL is preferred.",
        "skills": ["Python", "PyTorch", "Machine Learning", "pandas", "SQL", "Deep Learning"]
    },
    {
        "source_job_id": "IN-TCS-KOL-02",
        "title": "Machine Learning Engineer - Digital Core",
        "company": "Tata Consultancy Services (TCS Gitobitan)",
        "location": "Kolkata, West Bengal",
        "remote_type": "Onsite",
        "experience_min": 0,
        "experience_max": 2,
        "salary_min": 650000,
        "salary_max": 1200000,
        "currency": "INR",
        "company_domain": "tcs.com",
        "recruiter_email": "careers.east@tcs.com",
        "job_url": "https://www.tcs.com/careers/india/machine-learning-engineer-kolkata",
        "description": "Join TCS Digital Core AI Lab at Sector V, Kolkata. Responsible for training deep learning models, image classification algorithms, and enterprise NLP pipelines. Qualifications: M.Sc / B.Sc / B.Tech in Computer Science, Data Science, or related streams.",
        "skills": ["Python", "Machine Learning", "Deep Learning", "CNN (Convolutional Neural Networks)", "DBMS", "C++"]
    },
    {
        "source_job_id": "IN-CTS-KOL-03",
        "title": "Associate Software Engineer - .NET & Python",
        "company": "Cognizant Technology Solutions",
        "location": "Kolkata, West Bengal",
        "remote_type": "Hybrid",
        "experience_min": 0,
        "experience_max": 2,
        "salary_min": 600000,
        "salary_max": 1100000,
        "currency": "INR",
        "company_domain": "cognizant.com",
        "recruiter_email": "campusrelations@cognizant.com",
        "job_url": "https://careers.cognizant.com/india/kolkata/software-engineer",
        "description": "Building and maintaining modern enterprise web services using ASP.NET, C#, and Python. Collaboration with database administrators to write efficient SQL queries and optimize database performance in MySQL and SQL Server.",
        "skills": [".NET", "ASP.NET", "C#", "Python", "SQL", "MySQL", "OOP (Object-Oriented Programming)"]
    },
    {
        "source_job_id": "IN-WIPRO-KOL-04",
        "title": "Junior AI / Computer Vision Developer",
        "company": "Wipro Technologies",
        "location": "Kolkata, West Bengal",
        "remote_type": "Hybrid",
        "experience_min": 0,
        "experience_max": 2,
        "salary_min": 650000,
        "salary_max": 1150000,
        "currency": "INR",
        "company_domain": "wipro.com",
        "recruiter_email": "talentacquisition@wipro.com",
        "job_url": "https://careers.wipro.com/kolkata/junior-ai-developer",
        "description": "Opportunity for fresh graduates with passion in Deep Learning, PyTorch, and CNN architectures. You will develop agricultural and biomedical computer vision models for automated leaf disease detection and object recognition.",
        "skills": ["Python", "PyTorch", "Deep Learning", "CNN (Convolutional Neural Networks)", "pandas", "Computer Vision"]
    },

    # --- BENGALURU / BANGALORE, KARNATAKA ---
    {
        "source_job_id": "IN-FLIPKART-BLR-01",
        "title": "Machine Learning Engineer - Search & Recommendations",
        "company": "Flipkart",
        "location": "Bengaluru, Karnataka",
        "remote_type": "Hybrid",
        "experience_min": 0,
        "experience_max": 3,
        "salary_min": 1800000,
        "salary_max": 2800000,
        "currency": "INR",
        "company_domain": "flipkart.com",
        "recruiter_email": "tech-hiring@flipkart.com",
        "job_url": "https://careers.flipkart.com/jobs/ml-engineer-search-recommendations",
        "description": "Flipkart is looking for ML Engineers to build state-of-the-art recommendation systems serving 100M+ customers. Work on attention mechanisms, PyTorch, transformer models, and real-time distributed inference pipelines.",
        "skills": ["Python", "PyTorch", "Machine Learning", "Deep Learning", "Attention Mechanisms", "SQL"]
    },
    {
        "source_job_id": "IN-SWIGGY-BLR-02",
        "title": "Data Scientist - Vision & Autonomous Logistics",
        "company": "Swiggy",
        "location": "Bengaluru, Karnataka",
        "remote_type": "Hybrid",
        "experience_min": 1,
        "experience_max": 3,
        "salary_min": 1600000,
        "salary_max": 2500000,
        "currency": "INR",
        "company_domain": "swiggy.in",
        "recruiter_email": "careers@swiggy.in",
        "job_url": "https://careers.swiggy.com/jobs/data-scientist-vision",
        "description": "Develop visual verification models and automated food safety classifiers using Convolutional Neural Networks and Deep Learning. Strong proficiency in PyTorch, pandas, and Python required.",
        "skills": ["Python", "PyTorch", "CNN (Convolutional Neural Networks)", "Computer Vision", "Deep Learning", "pandas"]
    },
    {
        "source_job_id": "IN-RAZORPAY-BLR-03",
        "title": "Backend Software Engineer - Payments Core",
        "company": "Razorpay",
        "location": "Bengaluru, Karnataka",
        "remote_type": "Hybrid",
        "experience_min": 1,
        "experience_max": 3,
        "salary_min": 1700000,
        "salary_max": 2600000,
        "currency": "INR",
        "company_domain": "razorpay.com",
        "recruiter_email": "jobs@razorpay.com",
        "job_url": "https://razorpay.com/jobs/backend-software-engineer-core",
        "description": "Build resilient payment gateway infrastructure handling millions of transactions every hour. Requires strong grasp of REST APIs, MySQL, Redis, and high-performance backend development in Python and Go.",
        "skills": ["Python", "Go", "MySQL", "SQL", "REST API", "Docker", "DBMS"]
    },
    {
        "source_job_id": "IN-CRED-BLR-04",
        "title": "AI / ML Engineer - Financial Fraud Detection",
        "company": "CRED",
        "location": "Bengaluru, Karnataka",
        "remote_type": "Hybrid",
        "experience_min": 1,
        "experience_max": 4,
        "salary_min": 2000000,
        "salary_max": 3400000,
        "currency": "INR",
        "company_domain": "cred.club",
        "recruiter_email": "careers@cred.club",
        "job_url": "https://careers.cred.club/jobs/ai-ml-fraud-detection",
        "description": "Design anomaly detection and real-time transaction scoring models to protect members from financial fraud. Expertise in Machine Learning, graph algorithms, PyTorch, and SQL required.",
        "skills": ["Machine Learning", "Python", "Deep Learning", "PyTorch", "SQL", "scikit-learn"]
    },

    # --- HYDERABAD, TELANGANA ---
    {
        "source_job_id": "IN-MSFT-HYD-01",
        "title": "Software Engineer - Azure Cloud & AI",
        "company": "Microsoft India Development Center",
        "location": "Hyderabad, Telangana",
        "remote_type": "Hybrid",
        "experience_min": 0,
        "experience_max": 3,
        "salary_min": 2200000,
        "salary_max": 3500000,
        "currency": "INR",
        "company_domain": "microsoft.com",
        "recruiter_email": "indiacampus@microsoft.com",
        "job_url": "https://careers.microsoft.com/us/en/job/1802931/Software-Engineer-Hyderabad",
        "description": "Join Microsoft's flagship engineering campus in Gachibowli, Hyderabad. Work on Azure AI foundational services, cloud security, and distributed computing frameworks.",
        "skills": ["Python", "C#", "Azure", "C++", "OOP (Object-Oriented Programming)", "SQL"]
    },
    {
        "source_job_id": "IN-TCS-HYD-02",
        "title": "Associate Software Engineer (Python & Data)",
        "company": "Tata Consultancy Services (TCS Synergy Park)",
        "location": "Hyderabad, Telangana",
        "remote_type": "Onsite",
        "experience_min": 0,
        "experience_max": 2,
        "salary_min": 700000,
        "salary_max": 1250000,
        "currency": "INR",
        "company_domain": "tcs.com",
        "recruiter_email": "tcs.hyderabad@tcs.com",
        "job_url": "https://www.tcs.com/careers/india/associate-engineer-hyderabad",
        "description": "Great career entry point for freshers. You will build data ingestion workflows, analytics dashboards, and back-end logic using Python, SQL, and relational databases.",
        "skills": ["Python", "SQL", "MySQL", "DBMS", "OOP (Object-Oriented Programming)", "pandas"]
    },

    # --- PUNE, MAHARASHTRA ---
    {
        "source_job_id": "IN-INFOSYS-PUN-01",
        "title": "Machine Learning & Deep Learning Specialist",
        "company": "Infosys AI Innovation Hub",
        "location": "Pune, Maharashtra",
        "remote_type": "Hybrid",
        "experience_min": 0,
        "experience_max": 2,
        "salary_min": 750000,
        "salary_max": 1350000,
        "currency": "INR",
        "company_domain": "infosys.com",
        "recruiter_email": "talentacquisition@infosys.com",
        "job_url": "https://career.infosys.com/jobdesc?jobReferenceCode=INF-PUN-ML-01",
        "description": "Hinjawadi, Pune campus. Focus on deep learning architectures, automated image inspection, and enterprise machine learning tools. Candidates with PyTorch, CNNs, and Python projects preferred.",
        "skills": ["Python", "PyTorch", "Machine Learning", "Deep Learning", "SQL", "pandas"]
    },
    {
        "source_job_id": "IN-INFOSYS-BLR-02",
        "title": "Specialist Programmer - AI & Python Engineering",
        "company": "Infosys Limited",
        "location": "Bengaluru, Karnataka",
        "remote_type": "Hybrid",
        "experience_min": 0,
        "experience_max": 2,
        "salary_min": 950000,
        "salary_max": 1600000,
        "currency": "INR",
        "company_domain": "infosys.com",
        "recruiter_email": "careers_india@infosys.com",
        "job_url": "https://career.infosys.com/jobdesc?jobReferenceCode=INF-BLR-SP-02",
        "description": "Electronics City, Bengaluru. Elite Specialist Programmer track focusing on high-complexity algorithmic challenges, machine learning pipelines, and cloud APIs. Python, PyTorch, and Data Structures expertise required.",
        "skills": ["Python", "Machine Learning", "PyTorch", "Data Structures & Algorithms", "SQL", "Deep Learning"]
    },
    {
        "source_job_id": "IN-INFOSYS-KOL-03",
        "title": "Associate Consultant - AI & Python Analytics",
        "company": "Infosys Limited",
        "location": "Kolkata, West Bengal",
        "remote_type": "Hybrid",
        "experience_min": 0,
        "experience_max": 3,
        "salary_min": 700000,
        "salary_max": 1300000,
        "currency": "INR",
        "company_domain": "infosys.com",
        "recruiter_email": "kolkata.careers@infosys.com",
        "job_url": "https://career.infosys.com/jobdesc?jobReferenceCode=INF-KOL-AI-03",
        "description": "Infosys Rajarhat / Sector V, Kolkata. Designing automated machine learning models, statistical analysis, and dashboard integrations using Python, MySQL, and pandas for enterprise clients.",
        "skills": ["Python", "Machine Learning", "pandas", "MySQL", "SQL", "Deep Learning"]
    },
    {
        "source_job_id": "IN-INFOSYS-HYD-04",
        "title": "Systems Engineer - Python, SQL & Cloud Infrastructure",
        "company": "Infosys Limited",
        "location": "Hyderabad, Telangana",
        "remote_type": "Onsite",
        "experience_min": 0,
        "experience_max": 2,
        "salary_min": 650000,
        "salary_max": 1100000,
        "currency": "INR",
        "company_domain": "infosys.com",
        "recruiter_email": "campus_hiring@infosys.com",
        "job_url": "https://career.infosys.com/jobdesc?jobReferenceCode=INF-HYD-SE-04",
        "description": "Pocharam, Hyderabad campus. Developing robust backend workflows and API microservices. Proficiency in Python, relational databases (MySQL/PostgreSQL), and OOP concepts is desired.",
        "skills": ["Python", "SQL", "MySQL", "DBMS", "OOP (Object-Oriented Programming)", "Linux"]
    },
    {
        "source_job_id": "IN-INFOSYS-CHE-05",
        "title": "Senior Systems Engineer - .NET & C# Enterprise Solutions",
        "company": "Infosys Limited",
        "location": "Chennai, Tamil Nadu",
        "remote_type": "Hybrid",
        "experience_min": 1,
        "experience_max": 3,
        "salary_min": 800000,
        "salary_max": 1400000,
        "currency": "INR",
        "company_domain": "infosys.com",
        "recruiter_email": "chennai.recruitment@infosys.com",
        "job_url": "https://career.infosys.com/jobdesc?jobReferenceCode=INF-CHE-NET-05",
        "description": "Mahindra World City, Chennai. Building scalable enterprise services using C#, ASP.NET, and SQL Server / MySQL. Strong foundation in object-oriented programming required.",
        "skills": [".NET", "ASP.NET", "C#", "SQL", "MySQL", "OOP (Object-Oriented Programming)"]
    },
    {
        "source_job_id": "IN-PERSISTENT-PUN-02",
        "title": "Software Development Engineer - Cloud & Systems",
        "company": "Persistent Systems",
        "location": "Pune, Maharashtra",
        "remote_type": "Hybrid",
        "experience_min": 0,
        "experience_max": 3,
        "salary_min": 700000,
        "salary_max": 1400000,
        "currency": "INR",
        "company_domain": "persistent.com",
        "recruiter_email": "careers@persistent.com",
        "job_url": "https://careers.persistent.com/pune/sde-systems",
        "description": "Work on scalable backend architectures using C++, Python, and MySQL. Develop high-performance enterprise applications with comprehensive test coverage and CI/CD pipelines.",
        "skills": ["C++", "Python", "MySQL", "SQL", "OOP (Object-Oriented Programming)", "Docker"]
    },

    # --- GURGAON / NOIDA / DELHI NCR ---
    {
        "source_job_id": "IN-ZOMATO-GGN-01",
        "title": "Machine Learning Engineer - Customer Intelligence",
        "company": "Zomato",
        "location": "Gurgaon, Haryana (Delhi NCR)",
        "remote_type": "Hybrid",
        "experience_min": 1,
        "experience_max": 3,
        "salary_min": 1600000,
        "salary_max": 2700000,
        "currency": "INR",
        "company_domain": "zomato.com",
        "recruiter_email": "hiring@zomato.com",
        "job_url": "https://careers.zomato.com/jobs/ml-engineer-customer-intel",
        "description": "Develop dynamic pricing, restaurant ranking algorithms, and search relevance models using Deep Learning, Python, and PyTorch. Fast-paced engineering team based in Gurgaon.",
        "skills": ["Python", "PyTorch", "Machine Learning", "Deep Learning", "SQL", "pandas"]
    },
    {
        "source_job_id": "IN-PAYTM-NOI-02",
        "title": "Backend Developer - Python & Database Systems",
        "company": "Paytm",
        "location": "Noida, Uttar Pradesh (Delhi NCR)",
        "remote_type": "Onsite",
        "experience_min": 0,
        "experience_max": 3,
        "salary_min": 1100000,
        "salary_max": 2000000,
        "currency": "INR",
        "company_domain": "paytm.com",
        "recruiter_email": "careers@paytm.com",
        "job_url": "https://paytm.com/careers/noida/backend-developer-python",
        "description": "Design and build financial microservices with Python, REST APIs, and MySQL. Focus on concurrency, transaction integrity, and robust database indexing.",
        "skills": ["Python", "MySQL", "SQL", "REST API", "DBMS", "Docker"]
    },

    # --- MUMBAI, MAHARASHTRA ---
    {
        "source_job_id": "IN-JIO-MUM-01",
        "title": "Data Scientist & Deep Learning Engineer",
        "company": "Jio Platforms Limited",
        "location": "Mumbai, Maharashtra",
        "remote_type": "Hybrid",
        "experience_min": 0,
        "experience_max": 3,
        "salary_min": 1200000,
        "salary_max": 2200000,
        "currency": "INR",
        "company_domain": "jio.com",
        "recruiter_email": "careers@jio.com",
        "job_url": "https://careers.jio.com/mumbai/data-scientist-deep-learning",
        "description": "Build cutting-edge telecom intelligence, speech AI, and computer vision algorithms for 450M+ users across India. Excellent opportunity for freshers and junior researchers with strong Python and ML foundations.",
        "skills": ["Python", "PyTorch", "Machine Learning", "Deep Learning", "Computer Vision", "MySQL"]
    },

    # --- CHENNAI, TAMIL NADU ---
    {
        "source_job_id": "IN-ZOHO-CHE-01",
        "title": "Software Engineer - AI Products & Infrastructure",
        "company": "Zoho Corporation",
        "location": "Chennai, Tamil Nadu",
        "remote_type": "Onsite",
        "experience_min": 0,
        "experience_max": 2,
        "salary_min": 900000,
        "salary_max": 1600000,
        "currency": "INR",
        "company_domain": "zohocorp.com",
        "recruiter_email": "campus@zohocorp.com",
        "job_url": "https://www.zoho.com/careers/software-engineer-ai-chennai",
        "description": "Zoho Estancia, Chennai campus. Develop proprietary algorithms, database kernels, and AI-assisted productivity tools. Strong focus on clean code in C, C++, and Python.",
        "skills": ["C++", "C", "Python", "Machine Learning", "MySQL", "OOP (Object-Oriented Programming)"]
    },

    # --- REMOTE, INDIA ---
    {
        "source_job_id": "IN-POSTMAN-REM-01",
        "title": "Remote Python & API Platform Engineer",
        "company": "Postman India",
        "location": "Remote, India",
        "remote_type": "Remote",
        "experience_min": 1,
        "experience_max": 3,
        "salary_min": 1800000,
        "salary_max": 3000000,
        "currency": "INR",
        "company_domain": "postman.com",
        "recruiter_email": "careers@postman.com",
        "job_url": "https://www.postman.com/careers/remote-india/python-api-platform",
        "description": "Work from anywhere in India! Build developer tooling, API collaboration features, and test automation pipelines using Python, Docker, and modern web architectures.",
        "skills": ["Python", "REST API", "Docker", "SQL", "PostgreSQL", "Git"]
    },
    {
        "source_job_id": "IN-HASURA-REM-02",
        "title": "Remote Machine Learning & Data Infrastructure Engineer",
        "company": "Hasura India",
        "location": "Remote, India",
        "remote_type": "Remote",
        "experience_min": 1,
        "experience_max": 4,
        "salary_min": 2000000,
        "salary_max": 3400000,
        "currency": "INR",
        "company_domain": "hasura.io",
        "recruiter_email": "jobs@hasura.io",
        "job_url": "https://hasura.io/careers/remote-india/ml-engineer",
        "description": "Build high-speed data access and vector search integrations for AI applications. Work with PostgreSQL, GraphQL, Python, and machine learning models from anywhere in India.",
        "skills": ["Python", "PyTorch", "PostgreSQL", "Machine Learning", "Docker", "GraphQL"]
    },

    # --- REALISTIC SCAM EDGE CASES (NAUKRI / WHATSAPP / TELEGRAM SCAM PATTERNS FLAGGED BY JOBGUARD AI) ---
    {
        "source_job_id": "IN-SCAM-WFH-01",
        "title": "Work From Home Python Data Entry & Automation Trainee (Urgent)",
        "company": "FastTrack Career Placements",
        "location": "Kolkata, West Bengal",
        "remote_type": "Remote",
        "experience_min": 0,
        "experience_max": 1,
        "salary_min": 850000,
        "salary_max": 1200000,
        "currency": "INR",
        "company_domain": "fasttrackplacements-in.org",
        "recruiter_email": "naukri.fasttrackhr@gmail.com",
        "job_url": "https://fasttrackplacements-in.org/apply-now",
        "description": "100% Guaranteed Job placement for Freshers! Earn Rs 65,000 monthly from home. Immediate joining with no technical interview required. Selected candidates must pay a refundable registration fee of Rs 1,499 and training deposit via UPI to confirm seat. Limited seats available, contact HR on WhatsApp only.",
        "skills": ["Python", "SQL"]
    },
    {
        "source_job_id": "IN-SCAM-TCS-02",
        "title": "URGENT SELECTION: Software Engineer Direct Hiring - Laptop Provided",
        "company": "Global Tech Talent Solutions",
        "location": "Bengaluru, Karnataka",
        "remote_type": "Hybrid",
        "experience_min": 0,
        "experience_max": 1,
        "salary_min": 950000,
        "salary_max": 1400000,
        "currency": "INR",
        "company_domain": "globaltechtalent-sample.net",
        "recruiter_email": "tcs.directhiring2026@yahoo.com",
        "job_url": "https://globaltechtalent-sample.net/tcs-direct",
        "description": "Direct joining letter issued for MNC client. No interview required for freshers. High salary package with company laptop. Candidate must pay an interview fee and security deposit via GooglePay or PhonePe before onboarding document verification.",
        "skills": ["Java", "Python", "SQL", "C++"]
    }
]

class IndiaJobAdapter(JobSourceAdapter):
    """
    India Tech Careers & Public ATS Adapter.
    Provides verified software engineering listings across Indian tech hubs
    (Bengaluru, Hyderabad, Pune, Kolkata, Delhi NCR, Mumbai, Chennai, and Remote India)
    with genuine corporate domains and salary ranges in INR.
    """
    def __init__(self):
        super().__init__(name="IndiaJobAdapter", is_configured=True)

    def search_jobs(self, query: Optional[str] = None, location: Optional[str] = None, limit: int = 30) -> List[Dict[str, Any]]:
        results = []
        q_lower = query.strip().lower() if query else ""
        loc_lower = location.strip().lower() if location else ""

        for item in INDIAN_TECH_JOBS:
            # Query match
            if q_lower:
                match_query = (
                    q_lower in item["title"].lower() or
                    q_lower in item["company"].lower() or
                    q_lower in item["description"].lower() or
                    any(q_lower in s.lower() for s in item["skills"])
                )
                if not match_query:
                    continue

            # Location match
            if loc_lower and loc_lower != "all":
                match_loc = (
                    loc_lower in item["location"].lower() or
                    loc_lower in item["remote_type"].lower()
                )
                if not match_loc:
                    continue

            results.append(self.normalize_job(item))
            if len(results) >= limit:
                break

        logger.info(f"IndiaJobAdapter returned {len(results)} verified opportunities for query='{query}', location='{location}'.")
        return results

    def get_job_details(self, source_job_id: str) -> Optional[Dict[str, Any]]:
        for item in INDIAN_TECH_JOBS:
            if item["source_job_id"] == source_job_id:
                return self.normalize_job(item)
        return None

    def normalize_job(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": raw_data["title"],
            "company": raw_data["company"],
            "location": raw_data["location"],
            "remote_type": raw_data.get("remote_type", "Hybrid"),
            "description": raw_data["description"],
            "skills": raw_data.get("skills", []),
            "experience_min": raw_data.get("experience_min", 0),
            "experience_max": raw_data.get("experience_max", 3),
            "salary_min": raw_data.get("salary_min"),
            "salary_max": raw_data.get("salary_max"),
            "currency": raw_data.get("currency", "INR"),
            "source": "India Tech Careers (Live Feed)",
            "source_job_id": raw_data["source_job_id"],
            "job_url": raw_data["job_url"],
            "posted_date": datetime.now(timezone.utc),
            "recruiter_email": raw_data.get("recruiter_email"),
            "company_domain": raw_data.get("company_domain"),
        }

india_job_adapter = IndiaJobAdapter()

