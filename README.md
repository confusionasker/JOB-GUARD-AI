# JobGuard AI 🛡️
### AI-Powered Real Job Finder, Fraud Detection & Resume-Based Job Recommendation Platform

> **"Find Jobs You Can Actually Trust"**
> An end-to-end production-grade platform that protects tech job seekers from upfront fee scams, ghost listings, and identity theft, while calculating deep semantic match scores between candidate resumes and legitimate job opportunities.

---

## 📌 Problem Statement

1. **Job Board Scam Epidemic**: Fraudulent job listings have skyrocketed across online platforms. Scammers impersonate established companies, demanding "refundable registration fees", "training deposits", or conducting interviews solely on WhatsApp to extract personal financial data.
2. **Hidden Risk in Recommendations**: Traditional job boards rank opportunities purely on keywords. A candidate might be a 95% match for a role that is actually a scam. JobGuard AI **never hides safety risk behind match scores**.
3. **Ghost Listings & Duplicates**: The same vacancy is repeatedly posted across multiple platforms, cluttering search results. JobGuard AI normalizes and deduplicates listings automatically.

---

## ✨ Core Features

- **🛡️ Hybrid Fraud Detection Engine**:
  - Deterministic heuristics for upfront payment demands (UPI, registration fees, security deposits).
  - Corporate recruiter email vs. free webmail verification (`@gmail.com` claiming to represent MNCs).
  - Recruiter domain mismatch detection (`recruiter@fake-company.com` vs. `company.com`).
  - Unrealistic salary-to-experience anomaly detection.
  - Trained Machine Learning classifier (**TF-IDF + Balanced Logistic Regression**) outputting probabilistic fraud confidence.
  - Transparent risk breakdown (0–100 score: Low Risk, Moderate Risk, Suspicious, High Risk).
- **📄 Multi-Format Resume Parser & Canonical Skill Taxonomy**:
  - Direct extraction from `.pdf` and `.docx` using **PyMuPDF** and **python-docx**.
  - Hybrid skill extractor with boundary-sensitive matching and alias normalization (e.g. `"Postgres"` → `"PostgreSQL"`, `"k8s"` → `"Kubernetes"`, `"sklearn"` → `"scikit-learn"`).
  - Career gap analysis identifying high-demand industry skills missing from candidate resumes.
- **⚡ Resume ↔ Job Matching Engine**:
  - Multi-dimensional weighted match:
    - **Skill Overlap (45%)**
    - **Experience Fit (20%)**
    - **Semantic Similarity (15%)** via **Sentence Transformers** (`all-MiniLM-L6-v2`) with cosine similarity
    - **Education Compatibility (10%)**
    - **Work Mode / Location Alignment (10%)**
- **🔍 Safe Job Recommendation & Quarantine**:
  - Jobs with high fraud risk (`risk_score >= 70`) are quarantined out of standard recommendations into a dedicated review section.
  - Factual AI explanations outlining exact matching skills and missing requirements without hallucinations.
- **🌐 SSRF-Protected External Job URL Verifier**:
  - Paste any job posting link or manual job description to perform on-the-fly safety audits.
  - Robust SSRF protection blocking localhost, internal IP subnets (`10.x`, `192.168.x`, `172.x`), and cloud instance metadata services (`169.254.169.254`).
  - Honors platform access restrictions: if an external site restricts automated access (e.g. login walls), clean fallback instructions allow users to paste the text directly.
- **💼 Application Pipeline & Bookmark Tracker**:
  - Track applications across stages: `Applied`, `Assessment`, `Interview`, `Offer`, `Rejected`.
  - Save opportunities to bookmarks with 1-click optimistic UI updates.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Client ["Frontend (React 18 + TypeScript + Vite + Tailwind CSS)"]
        UI_Dash["Dashboard & Analytics (Recharts)"]
        UI_Search["Job Search & Filters"]
        UI_Verify["Job URL / Text Verifier"]
        UI_Resume["Resume Upload & Insights"]
        UI_Tracker["Application Pipeline Tracker"]
    end

    subgraph Backend ["Backend (FastAPI + Pydantic v2 + SQLAlchemy 2.0)"]
        API_Auth["JWT Auth & Security Service"]
        API_Resume["Resume Parser (PyMuPDF / python-docx)"]
        API_Skills["Canonical Taxonomy Extractor"]
        API_Jobs["Job Normalizer & Deduplicator"]
        API_Fraud["Hybrid Fraud Engine (Rules + ML Classifier)"]
        API_Match["Semantic Match Engine (Embeddings + Cosine Sim)"]
        API_Recommend["Recommendation & Quarantine Engine"]
        API_SSRF["Job URL Verifier (SSRF Protected)"]
    end

    subgraph ML_Storage ["Data & Machine Learning Pipeline"]
        DB[(SQLAlchemy ORM - SQLite / PostgreSQL)]
        ML_Model["ML Fraud Model (TF-IDF + Logistic Regression)"]
        Embedder["Sentence Transformer (all-MiniLM-L6-v2)"]
    end

    subgraph Adapters ["Modular Job Source Adapters"]
        DemoSource["DemoJobAdapter (Curated Seed Listings)"]
        CareerSource["CompanyCareerAdapter (Public Career Feeds)"]
        CompliantStubs["LinkedIn / Indeed / Naukri Adapters (Safely Disabled)"]
    end

    Client <-->|REST API + Bearer JWT| Backend
    Backend --> DB
    API_Fraud --> ML_Model
    API_Match --> Embedder
    API_Jobs --> DemoSource
    API_Jobs --> CareerSource
    API_Jobs --> CompliantStubs
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, React Router v6, Axios, Lucide React, Recharts |
| **Backend** | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, PyJWT, bcrypt |
| **Database** | SQLite (zero-config local default), PostgreSQL compatible |
| **AI / ML** | scikit-learn, TF-IDF Vectorization, Sentence Transformers, NumPy, pandas |
| **Document Processing** | PyMuPDF (fitz), python-docx |
| **Testing** | pytest, pytest-asyncio, httpx |

---

## 📂 Project Structure

```text
jobguard-ai/
│
├── frontend/                   # React + TypeScript Vite Application
│   ├── src/
│   │   ├── components/         # Reusable UI (JobCard, Navbar, etc.)
│   │   ├── context/            # AuthContext (JWT management)
│   │   ├── pages/              # Dashboard, Jobs, JobDetail, VerifyJob, Resume, Saved, Applications, Login, Register, Profile
│   │   ├── services/           # Axios API Client with interceptors
│   │   ├── types/              # TypeScript interfaces matching backend models
│   │   ├── App.tsx             # Protected routes and navigation
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── backend/                    # FastAPI Backend Application
│   ├── app/
│   │   ├── api/v1/             # Endpoints (auth, profile, resumes, jobs, risk, match, saved, applications)
│   │   ├── core/               # Settings, DB session, JWT security, structured logging
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic v2 request & response schemas
│   │   ├── services/           # Resume parser, skill extractor, fraud engine, match engine, recommend engine, URL verifier
│   │   ├── job_sources/        # Modular JobSourceAdapter, DemoAdapter, CompanyCareerAdapter, Compliant stubs
│   │   ├── ml/                 # Model inference loader (fraud_model.py)
│   │   ├── utils/              # Deduplication similarity, SSRF protection
│   │   └── main.py             # FastAPI entrypoint, middleware, database initialization
│   ├── alembic/                # Alembic database migrations
│   ├── tests/                  # Automated pytest suite (14 test cases)
│   ├── requirements.txt
│   └── .env.example
│
├── ml/                         # Machine Learning Pipeline
│   ├── datasets/               # Benchmark job corpora (sample_jobs.csv)
│   ├── training/               # Training script (train_fraud_model.py)
│   └── models/                 # Serialized joblib artifacts
│
├── README.md
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** (Tested on Python 3.12)
- **Node.js 18+** (Tested on Node.js 24)
- **npm** or **pnpm**

---

### Step 1: Clone Repository & Backend Setup

```bash
# Clone the repository
git clone https://github.com/your-username/jobguard-ai.git
cd jobguard-ai

# Create Python virtual environment
python -m venv backend/venv

# Activate virtual environment
# Windows:
backend\venv\Scripts\activate
# macOS / Linux:
# source backend/venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

---

### Step 2: Environment Configuration

Create a `.env` file in `backend/`:

```bash
cp backend/.env.example backend/.env
```

Default settings in `backend/.env`:

```env
PROJECT_NAME="JobGuard AI"
VERSION="1.0.0"
API_V1_STR="/api"

# Default to SQLite for instant out-of-the-box local runs:
DATABASE_URL="sqlite:///./jobguard.db"

# Or configure PostgreSQL:
# DATABASE_URL="postgresql://postgres:postgres@localhost:5432/jobguard_db"

SECRET_KEY="supersecret_jwt_key_jobguard_ai_development_only_change_in_production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

MAX_RESUME_SIZE_MB=10
ALLOWED_CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Optional LLM layer (application runs 100% offline without LLM)
LLM_PROVIDER="fallback"
```

---

### Step 3: Train the Machine Learning Fraud Classifier

Run the training pipeline script. It preprocesses the training dataset, performs a stratified train/test split, trains a TF-IDF Logistic Regression classifier with balanced class weighting, evaluates precision/recall/F1, and serializes the model binaries to `ml/models/`:

```bash
python ml/training/train_fraud_model.py
```

Expected output:
```text
JobGuard AI — Fraud Detection Model Training Pipeline
Loaded dataset: 18 samples
Training Logistic Regression classifier with balanced class weighting...
--- Model Evaluation Results ---
              precision    recall  f1-score   support
     Genuine       1.00      1.00      1.00         3
  Fraudulent       1.00      1.00      1.00         3
F1-Score: 1.0000
Model saved successfully to: ml/models/fraud_model.joblib
Vectorizer saved successfully to: ml/models/vectorizer.joblib
```

---

### Step 4: Run the Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

- API Base URL: `http://localhost:8000`
- Interactive Swagger API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

---

### Step 5: Frontend Setup & Run

Open a second terminal window:

```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

Open your browser at:
`http://localhost:5173`

---

## 🧪 Running Automated Tests

JobGuard AI includes 14 comprehensive backend automated tests covering authentication, resume parsing, skill normalization, fraud rules, resume matching, deduplication, and SSRF security:

```bash
# In repository root with virtual environment activated:
python -m pytest backend/tests -v
```

All 14 tests pass with 0 failures:
- `test_health_check`: API service health check
- `test_user_registration_and_login`: JWT authentication flow & profile updates
- `test_company_and_title_normalization`: Company suffixes & job title normalization
- `test_similarity_calculation`: Text Levenshtein / Jaccard similarity ratios
- `test_legitimate_job_low_risk`: Verified corporate job low-risk evaluation
- `test_scam_job_high_risk_payment_demand`: Upfront fee and UPI payment detection
- `test_recruiter_domain_mismatch_and_free_email`: Free webmail and recruiter domain discrepancy
- `test_resume_job_matching`: Multi-factor resume to job matching engine
- `test_resume_parser_structured_extraction`: Structured entities from resume text
- `test_resume_upload_endpoint`: Binary PDF upload and parsing endpoint
- `test_skill_extraction_and_normalization`: Canonical skill taxonomy
- `test_alias_normalization`: Alias normalization ("postgres" -> "PostgreSQL")
- `test_ssrf_protection_blocks_malicious_urls`: SSRF protection against loopbacks and cloud metadata
- `test_manual_text_verification_fallback`: Manual job description verification fallback

---

## 🛡️ Security & Privacy Practices

1. **Password Security**: Passwords hashed using standard `bcrypt` with unique cryptographic salts. Plaintext passwords are never persisted.
2. **SSRF Defense**: The Job URL Verifier validates hostnames using DNS resolution and strictly blocks loopbacks (`127.0.0.1`), private RFC1918 subnets, link-local IPs, and cloud metadata services (`169.254.169.254`). Maximum request timeout is 5.0 seconds with a 2MB response size limit.
3. **Resume Privacy**: Resumes are strictly isolated to the authenticated user account and are never made publicly accessible.
4. **Honest Platform Compliance**: JobGuard AI **does not conduct illicit scraping, login bypassing, or CAPTCHA circumvention**. When an external platform restricts automated access, JobGuard AI displays a transparent explanation and offers manual text verification.

---

## ⚠️ Important Limitations

- **Risk Score Interpretation**: A low risk score indicates that known fraud signatures were not detected; it does not constitute a legal guarantee that an employer is genuine.
- **Assistance Tool**: Recommendations and match scores are designed to assist job seekers in filtering opportunities and should not replace individual due diligence.

---

## 🔮 Future Roadmap

- Automated email alerts for newly verified low-risk jobs.
- Chrome Extension for verifying listings directly on job boards.
- Recruiter reputation scoring and peer-reviewed company verification signals.
- Automated cover letter generation tailored to verified job descriptions.

---

## 📄 License

MIT License. Free for educational and personal portfolio use.
