import re
import os
from typing import Dict, Any, List
import pymupdf
import docx
from app.services.skill_extractor import skill_extractor
from app.core.logging import logger

COMMON_JOB_TITLES = [
    "Software Engineer",
    "Senior Software Engineer",
    "Staff Software Engineer",
    "Backend Developer",
    "Senior Backend Developer",
    "Frontend Developer",
    "Senior Frontend Developer",
    "Full Stack Developer",
    "Full Stack Engineer",
    "DevOps Engineer",
    "Site Reliability Engineer",
    "Cloud Architect",
    "Data Scientist",
    "Machine Learning Engineer",
    "AI Engineer",
    "Data Engineer",
    "Product Manager",
    "QA Engineer",
    "Security Engineer",
]

class ResumeParser:
    @staticmethod
    def extract_text_from_file(file_path: str, file_ext: str) -> str:
        """Extract plain text from PDF or DOCX file, with automatic OCR fallback for scanned/image PDFs."""
        ext = file_ext.lower().strip(".")
        if ext == "pdf":
            try:
                doc = pymupdf.open(file_path)
                text_parts = []
                for page in doc:
                    txt = page.get_text()
                    # Fallback to OCR if page has no or very sparse text (< 40 chars, e.g. scanned image PDF)
                    if not txt or len(txt.strip()) < 40:
                        try:
                            from rapidocr_onnxruntime import RapidOCR
                            ocr = RapidOCR()
                            pix = page.get_pixmap(dpi=150)
                            ocr_res, _ = ocr(pix.tobytes("png"))
                            if ocr_res:
                                ocr_lines = [item[1] for item in ocr_res if item and len(item) > 1]
                                txt = "\n".join(ocr_lines)
                        except Exception as ocr_err:
                            logger.warning(f"RapidOCR fallback error: {ocr_err}")
                    text_parts.append(txt or "")
                doc.close()
                return "\n".join(text_parts)
            except Exception as e:
                logger.error(f"Error reading PDF {file_path}: {e}")
                raise ValueError(f"Could not read PDF file: {str(e)}")

        elif ext in ["docx", "doc"]:
            try:
                document = docx.Document(file_path)
                text_parts = [p.text for p in document.paragraphs if p.text]
                for table in document.tables:
                    for row in table.rows:
                        row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                        if row_text:
                            text_parts.append(" | ".join(row_text))
                return "\n".join(text_parts)
            except Exception as e:
                logger.error(f"Error reading DOCX {file_path}: {e}")
                raise ValueError(f"Could not read DOCX file: {str(e)}")

        else:
            raise ValueError(f"Unsupported file format: .{ext}. Supported formats are .pdf and .docx")

    @classmethod
    def parse_structured_data(cls, raw_text: str) -> Dict[str, Any]:
        """
        Extract structured information from resume text:
        skills, education, experience, projects, certifications, job titles, and experience years.
        """
        if not raw_text:
            return {
                "skills": [],
                "education": [],
                "experience": [],
                "projects": [],
                "certifications": [],
                "job_titles": [],
                "total_experience_years": 0
            }

        # 1. Extract Skills
        skills = skill_extractor.extract_skills(raw_text)

        # 2. Extract Job Titles & Infer Candidates
        extracted_titles = []
        for title in COMMON_JOB_TITLES:
            pattern = rf"(?i)\b{re.escape(title)}\b"
            if re.search(pattern, raw_text):
                extracted_titles.append(title)

        # Infer initial target roles from skills if none explicitly mentioned
        if not extracted_titles:
            skills_lower = {s.lower() for s in skills}
            if any(k in skills_lower for k in ["machine learning", "deep learning", "pytorch", "tensorflow", "cnn (convolutional neural networks)"]):
                extracted_titles.append("Machine Learning Engineer")
            if any(k in skills_lower for k in ["python", "fastapi", "django", "flask"]):
                extracted_titles.append("Python Developer")
            if any(k in skills_lower for k in [".net", "asp.net", "c#"]):
                extracted_titles.append(".NET Developer")
            if any(k in skills_lower for k in ["react", "javascript", "typescript", "html5", "css3"]):
                extracted_titles.append("Frontend Developer")
            if not extracted_titles:
                extracted_titles.append("Software Engineer")

        # 3. Extract Total Experience Years
        exp_years = cls._estimate_experience_years(raw_text)

        # 4. Extract Education
        education = cls._extract_education(raw_text)

        # 5. Extract Certifications
        certifications = cls._extract_certifications(raw_text)

        # 6. Extract Projects
        projects = cls._extract_projects(raw_text)

        # 7. Extract Experience Entries
        experience_entries = cls._extract_experience_blocks(raw_text)

        return {
            "skills": skills,
            "education": education,
            "experience": experience_entries,
            "projects": projects,
            "certifications": certifications,
            "job_titles": extracted_titles,
            "total_experience_years": exp_years
        }

    @staticmethod
    def _estimate_experience_years(text: str) -> int:
        """Detect explicit mentions of experience or calculate from year spans."""
        # Check explicit: "5+ years of experience", "over 3 years"
        explicit_matches = re.findall(r"(?i)(\d{1,2})\+?\s*(?:years|yrs)(?:\s*of)?\s*(?:experience|exp)", text)
        if explicit_matches:
            try:
                numbers = [int(m) for m in explicit_matches if int(m) <= 40]
                if numbers:
                    return max(numbers)
            except ValueError:
                pass

        # Estimate from year ranges in work history: e.g. 2019 - 2024 or 2020 - Present
        year_ranges = re.findall(r"(?:19|20)\d{2}\s*[-–—to]+\s*(?:(?:19|20)\d{2}|Present|Current|Now)", text, re.IGNORECASE)
        total_span = 0
        current_year = 2026
        for span in year_ranges:
            years = re.findall(r"(?:19|20)\d{2}", span)
            if len(years) == 2:
                start, end = int(years[0]), int(years[1])
                if end >= start and (end - start) < 30:
                    total_span += (end - start)
            elif len(years) == 1 and any(w in span.lower() for w in ["present", "current", "now"]):
                start = int(years[0])
                if current_year >= start and (current_year - start) < 30:
                    total_span += (current_year - start)

        if total_span > 0:
            return min(total_span, 35)

        return 0  # 0 years if no explicit work experience or job span detected (Fresher)

    @staticmethod
    def _extract_education(text: str) -> List[Dict[str, Any]]:
        education = []
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        degree_map = [
            (r"(?i)\bM\.?Sc(?:\.|\b|\s|\()", "M.Sc (Master of Science)"),
            (r"(?i)\bB\.?Sc(?:\.|\b|\s|\()", "B.Sc (Bachelor of Science)"),
            (r"(?i)\bM\.?Tech(?:\.|\b|\s|\()", "M.Tech"),
            (r"(?i)\bB\.?Tech(?:\.|\b|\s|\()", "B.Tech"),
            (r"(?i)\bB\.?E(?:\.|\b|\s|\()", "B.E. (Bachelor of Engineering)"),
            (r"(?i)\bM\.?E(?:\.|\b|\s|\()", "M.E. (Master of Engineering)"),
            (r"(?i)\bMCA\b", "MCA (Master of Computer Applications)"),
            (r"(?i)\bBCA\b", "BCA (Bachelor of Computer Applications)"),
            (r"(?i)\bMBA\b", "MBA"),
            (r"(?i)\bBBA\b", "BBA"),
            (r"(?i)\bPh\.?D\b", "Ph.D"),
            (r"(?i)\bBachelor(?:\s+of\s+[A-Za-z]+)?\b", "Bachelor's Degree"),
            (r"(?i)\bMaster(?:\s+of\s+[A-Za-z]+)?\b", "Master's Degree"),
            (r"(?i)\b12th(?:\s+grade|\s+standard|\s+class|\b)", "Higher Secondary (12th)"),
            (r"(?i)\b10th(?:\s+grade|\s+standard|\s+class|\b)", "Secondary School (10th)"),
            (r"(?i)\bHigher\s+Secondary\b", "Higher Secondary (12th)"),
            (r"(?i)\bSecondary\s+School\b", "Secondary School (10th)"),
            (r"(?i)\bDiploma\b", "Diploma")
        ]

        found_degrees = []
        for idx, line in enumerate(lines):
            # Ignore headers
            if re.search(r"(?i)degree\s+of|examination|year\s+of|marks|cgpa|qualification", line):
                continue

            for pat, norm_name in degree_map:
                if re.search(pat, line):
                    found_degrees.append((idx, line, norm_name))
                    break

        if not found_degrees:
            # Fallback to general degree regex
            degree_patterns = [
                r"(?i)\b(?:Bachelor|Master|Doctorate|PhD|Ph\.D\.|B\.?S\.?|M\.?S\.?|B\.?Sc\.?|M\.?Sc\.?|B\.?Tech|M\.Tech|B\.?E\.?|BCA|MCA|BBA|MBA)\b[^\n\.\,]*",
            ]
            years = re.findall(r"\b(19\d{2}|20\d{2})\b", text)
            for pat in degree_patterns:
                matches = re.findall(pat, text)
                for m in matches[:4]:
                    clean_m = m.strip()
                    if len(clean_m) > 3 and not re.search(r"(?i)degree\s+of", clean_m):
                        entry = {"degree": clean_m, "institution": None, "year": years[-1] if years else None, "score": None}
                        education.append(entry)
            return education

        for k, (idx, line, norm_name) in enumerate(found_degrees):
            next_idx = found_degrees[k+1][0] if k + 1 < len(found_degrees) else min(idx + 8, len(lines))
            chunk = lines[idx:next_idx]
            chunk_text = " ".join(chunk)

            year_match = re.search(r"\b(19\d{2}|20\d{2})\b", chunk_text)
            year = year_match.group(1) if year_match else None

            score_match = re.search(r"(\d{1,2}(?:\.\d{1,2})?\s*(?:\([^\)]*\)\s*)*\(?(?:cgpa|sgpa|gpa|%)\)?)", chunk_text, re.IGNORECASE)
            if not score_match:
                score_match = re.search(r"(\d{1,2}(?:\.\d{1,2})?\s*(?:cgpa|sgpa|gpa|%))", chunk_text, re.IGNORECASE)
            score = score_match.group(1).strip().upper() if score_match else None

            inst_parts = []
            for cl in chunk[1:]:
                cl_clean = cl.strip().strip("-•|")
                # Insert space in camelCase joined words e.g. VidyasagarUniversity -> Vidyasagar University
                cl_clean = re.sub(r"([a-z])([A-Z])", r"\1 \2", cl_clean)
                if re.fullmatch(r"(?:19|20)\d{2}", cl_clean):
                    continue
                if re.search(r"^\d{1,2}(?:\.\d{1,2})?\s*(?:\([^\)]*\)\s*)*\(?(?:cgpa|sgpa|gpa|%)\)?$", cl_clean, re.IGNORECASE):
                    continue
                inst_keywords = [
                    "university", "college", "school", "vidyalaya", "institute", 
                    "autonomous", "board", "academy", "polytechnic", "campus",
                    "department", "faculty", "vidyapith", "vidyamandir", "shiksha",
                    "council", "education"
                ]
                boards = ["WBCHSE", "WBBSE", "CBSE", "ICSE", "CISCE", "NIOS", "BIE", "HSC", "SSLC"]
                if any(term in cl_clean.lower() for term in inst_keywords) or any(board in cl_clean for board in boards):
                    inst_parts.append(cl_clean)
                elif len(cl_clean) > 3 and not re.search(r"(?i)\b(?:grade|marks|cgpa|sgpa|passed|division|degree)\b", cl_clean):
                    # Multi-line institution name fragments within the same degree block
                    if any(term in chunk_text.lower() for term in ["college", "university", "institute", "school"]):
                        inst_parts.append(cl_clean)

            unique_inst = []
            for p in inst_parts:
                p_norm = " ".join(p.split())
                if p_norm and not any(p_norm in u or u in p_norm for u in unique_inst):
                    unique_inst.append(p_norm)

            inst_str = ", ".join(unique_inst) if unique_inst else None

            education.append({
                "degree": norm_name,
                "raw_degree": line,
                "institution": inst_str,
                "year": year,
                "score": score
            })

        return education

    @staticmethod
    def _extract_certifications(text: str) -> List[str]:
        cert_keywords = [
            "AWS Certified",
            "Azure Certified",
            "Google Cloud Certified",
            "Certified Kubernetes Administrator",
            "CKA",
            "CKAD",
            "PMP",
            "CompTIA",
            "Cisco Certified",
            "CCNA",
            "TensorFlow Developer",
            "Oracle Certified",
        ]
        found = []
        for cert in cert_keywords:
            if re.search(rf"(?i)\b{re.escape(cert)}\b", text):
                found.append(cert)
        return found

    @staticmethod
    def _extract_projects(text: str) -> List[Dict[str, str]]:
        projects = []
        # Find project bullet points or headers
        proj_matches = re.findall(r"(?i)project\s*:\s*([^\n]+)", text)
        for p in proj_matches[:5]:
            projects.append({"title": p.strip(), "description": ""})
        return projects

    @staticmethod
    def _extract_experience_blocks(text: str) -> List[Dict[str, str]]:
        experiences = []
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines:
            for title in COMMON_JOB_TITLES:
                if title.lower() in line.lower() and len(line) < 100:
                    experiences.append({"role": title, "raw": line})
                    break
        return experiences[:6]

resume_parser = ResumeParser()

