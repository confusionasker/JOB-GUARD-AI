export interface User {
  id: string;
  name: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  profile?: Profile;
}

export interface Profile {
  id: string;
  user_id: string;
  full_name?: string;
  preferred_titles?: string;
  preferred_locations?: string;
  remote_preference?: 'Remote' | 'Hybrid' | 'Onsite' | 'Any';
  expected_salary?: number;
  experience_level?: 'Entry' | 'Mid-Level' | 'Senior' | 'Lead';
  key_skills?: string;
  education?: string;
  updated_at: string;
}

export interface RiskSignal {
  type: string;
  severity: 'low' | 'medium' | 'high';
  message: string;
}

export interface VerificationSignals {
  domain_valid?: boolean;
  career_page_found?: boolean;
  free_email?: boolean;
  domain_match?: boolean;
  payment_demanded?: boolean;
  whatsapp_only?: boolean;
  salary_realistic?: boolean;
}

export interface RiskAnalysis {
  risk_score: number;
  risk_level: 'Low Risk' | 'Moderate Risk' | 'Suspicious' | 'High Risk';
  signals: RiskSignal[];
  verification_signals: VerificationSignals;
  ml_confidence?: number;
  rule_score?: number;
  explanation?: string;
  analyzed_at?: string;
}

export interface JobMatch {
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  experience_match: boolean;
  education_match: boolean;
  semantic_score: number;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  location?: string;
  remote_type?: string;
  description: string;
  skills: string[];
  experience_min?: number;
  experience_max?: number;
  salary_min?: number;
  salary_max?: number;
  currency?: string;
  source: string;
  source_job_id?: string;
  job_url?: string;
  posted_date?: string;
  recruiter_email?: string;
  company_domain?: string;
  is_seed?: boolean;
  risk?: RiskAnalysis;
  match?: JobMatch;
  recommendation_label?: 'HIGHLY RECOMMENDED' | 'GOOD MATCH' | 'POSSIBLE MATCH' | 'LOW MATCH' | 'REVIEW RISK';
  is_saved?: boolean;
}

export interface Application {
  id: string;
  job_id: string;
  status: 'Not Applied' | 'Applied' | 'Assessment' | 'Interview' | 'Offer' | 'Rejected';
  applied_date?: string;
  notes?: string;
  updated_at: string;
  job?: Job;
}

export interface ParsedResume {
  id: string;
  file_name: string;
  file_type: string;
  total_experience_years: number;
  raw_text?: string;
  structured_data: {
    skills: string[];
    education: Array<{ degree?: string; institution?: string; year?: string; score?: string; raw_degree?: string }>;
    experience: Array<{ role?: string; company?: string; duration?: string; description?: string }>;
    projects: Array<{ title?: string; tech?: string; description?: string }>;
    certifications: string[];
    job_titles: string[];
    total_experience_years: number;
  };
  created_at: string;
}
