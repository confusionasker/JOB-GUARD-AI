import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  ShieldCheck, 
  AlertTriangle, 
  Bookmark, 
  ExternalLink, 
  CheckCircle, 
  XCircle, 
  Sparkles, 
  ArrowLeft,
  Building2,
  Calendar,
  DollarSign,
  Briefcase,
  Check,
  Plus
} from 'lucide-react';
import api from '../services/api';
import { Job } from '../types';

export const JobDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [job, setJob] = useState<Job | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [isSaved, setIsSaved] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [appliedStatus, setAppliedStatus] = useState<string | null>(null);

  useEffect(() => {
    const fetchJob = async () => {
      try {
        setIsLoading(true);
        const res = await api.get<Job>(`/jobs/${id}`);
        setJob(res.data);
        setIsSaved(!!res.data.is_saved);

        // Check if user is tracking this job in applications
        const appsRes = await api.get('/applications').catch(() => ({ data: [] }));
        const existingApp = (appsRes.data || []).find((a: any) => a.job_id === id);
        if (existingApp) {
          setAppliedStatus(existingApp.status);
        }
      } catch (err: any) {
        console.error(err);
        setErrorMsg('Job listing not found or could not be loaded.');
      } finally {
        setIsLoading(false);
      }
    };
    if (id) fetchJob();
  }, [id]);

  const handleToggleSave = async () => {
    if (!job) return;
    const nextSaved = !isSaved;
    setIsSaved(nextSaved);
    try {
      if (nextSaved) {
        await api.post(`/jobs/${job.id}/save`);
      } else {
        await api.delete(`/jobs/${job.id}/save`);
      }
    } catch (err) {
      setIsSaved(!nextSaved);
    }
  };

  const handleTrackApplication = async (status: string) => {
    if (!job) return;
    setIsApplying(true);
    try {
      await api.post('/applications', {
        job_id: job.id,
        status: status,
        notes: `Application recorded on ${new Date().toLocaleDateString()}`
      });
      setAppliedStatus(status);
    } catch (err) {
      console.error('Failed to update tracker:', err);
    } finally {
      setIsApplying(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 text-center text-slate-500">
        <div className="w-8 h-8 border-3 border-indigo-200 border-t-brand-600 rounded-full animate-spin mx-auto mb-3"></div>
        Loading verified job details...
      </div>
    );
  }

  if (errorMsg || !job) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-red-500 mx-auto" />
        <h2 className="text-xl font-bold text-slate-900">{errorMsg || 'Job Not Found'}</h2>
        <Link to="/jobs" className="text-brand-600 text-sm font-semibold hover:underline">
          Return to Job Search
        </Link>
      </div>
    );
  }

  const riskScore = job.risk?.risk_score ?? 15;
  const riskLevel = job.risk?.risk_level ?? 'Low Risk';
  const match = job.match;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Back button */}
      <button
        onClick={() => navigate(-1)}
        className="inline-flex items-center space-x-2 text-xs font-semibold text-slate-500 hover:text-slate-900 transition"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to listings</span>
      </button>

      {/* Hero Header */}
      <div className="bg-white rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-sm space-y-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b border-slate-100 pb-6">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <span className="text-xs px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 font-semibold">
                {job.remote_type || 'Onsite'}
              </span>
              <span className="text-xs text-slate-400">Source: {job.source}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              {job.title}
            </h1>
            <div className="flex flex-wrap items-center gap-3 text-sm text-slate-600">
              <span className="font-semibold text-slate-900 flex items-center space-x-1">
                <Building2 className="w-4 h-4 text-slate-400" />
                <span>{job.company}</span>
              </span>
              <span>•</span>
              <span>{job.location || 'Remote'}</span>
              {job.salary_min && (
                <>
                  <span>•</span>
                  <span className="font-semibold text-emerald-700">
                    ${Math.round(job.salary_min / 1000)}k - ${Math.round((job.salary_max || job.salary_min) / 1000)}k / year
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
            <button
              onClick={handleToggleSave}
              className={`flex-1 md:flex-none px-4 py-2.5 rounded-xl border font-semibold text-xs flex items-center justify-center space-x-2 transition ${
                isSaved
                  ? 'bg-indigo-50 border-brand-200 text-brand-700'
                  : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
              }`}
            >
              <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-brand-600 text-brand-600' : ''}`} />
              <span>{isSaved ? 'Saved' : 'Save Job'}</span>
            </button>

            {job.job_url && (
              <a
                href={job.job_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 md:flex-none px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs shadow-md shadow-brand-600/20 flex items-center justify-center space-x-2 transition"
              >
                <span>Apply on Source</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
          </div>
        </div>

        {/* Dual Badges: Match Rate vs Fraud Risk */}
        <div className="grid sm:grid-cols-2 gap-4">
          {/* Safety Risk Panel */}
          <div className={`p-5 rounded-2xl border ${
            riskScore <= 20
              ? 'bg-emerald-50/50 border-emerald-200'
              : riskScore <= 50
              ? 'bg-amber-50/50 border-amber-200'
              : 'bg-red-50/50 border-red-200'
          }`}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-600">Safety & Fraud Audit</span>
              <ShieldCheck className={`w-5 h-5 ${riskScore <= 20 ? 'text-emerald-600' : riskScore <= 50 ? 'text-amber-600' : 'text-red-600'}`} />
            </div>
            <div className="flex items-baseline space-x-2">
              <span className={`text-3xl font-extrabold ${riskScore <= 20 ? 'text-emerald-700' : riskScore <= 50 ? 'text-amber-700' : 'text-red-700'}`}>
                {riskScore}
              </span>
              <span className="text-xs font-semibold text-slate-500">/ 100</span>
              <span className="text-xs font-bold uppercase ml-2 text-slate-700">({riskLevel})</span>
            </div>
            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
              {job.risk?.explanation || 'Listing analyzed against known fraud heuristics and domain verification signals.'}
            </p>
          </div>

          {/* Resume Match Panel */}
          <div className="p-5 rounded-2xl border border-indigo-100 bg-indigo-50/40">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-brand-900">Resume Compatibility</span>
              <Sparkles className="w-5 h-5 text-brand-600" />
            </div>
            <div className="flex items-baseline space-x-2">
              <span className="text-3xl font-extrabold text-brand-700">
                {match ? Math.round(match.match_score) : 50}%
              </span>
              <span className="text-xs font-semibold text-slate-500">Skill alignment</span>
            </div>
            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
              {match
                ? `You possess ${match.matched_skills.length} of the ${job.skills?.length || 0} primary required skills.`
                : 'Upload your resume to calculate personalized match percentage.'}
            </p>
          </div>
        </div>
      </div>

      {/* Main Details Grid: Description vs Sidebar */}
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left Column: Job Description & Skills (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Job Description */}
          <div className="bg-white rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-sm space-y-4">
            <h2 className="text-lg font-bold text-slate-900">About the Role</h2>
            <div className="prose prose-slate max-w-none text-sm text-slate-700 leading-relaxed whitespace-pre-line">
              {job.description}
            </div>
          </div>

          {/* Skill Breakdown */}
          <div className="bg-white rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-sm space-y-4">
            <h2 className="text-lg font-bold text-slate-900">Required Skills & Fit</h2>

            {match ? (
              <div className="space-y-4">
                <div>
                  <div className="text-xs font-bold uppercase tracking-wider text-emerald-700 mb-2 flex items-center space-x-1.5">
                    <CheckCircle className="w-4 h-4 text-emerald-600" />
                    <span>Matched in your Resume ({match.matched_skills.length})</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {match.matched_skills.map((s) => (
                      <span key={s} className="px-3 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-medium">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                {match.missing_skills.length > 0 && (
                  <div>
                    <div className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-2 flex items-center space-x-1.5">
                      <XCircle className="w-4 h-4 text-slate-400" />
                      <span>Missing / Desired Skills ({match.missing_skills.length})</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {match.missing_skills.map((s) => (
                        <span key={s} className="px-3 py-1 rounded-lg bg-slate-100 text-slate-700 border border-slate-200 text-xs font-medium">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-wrap gap-2">
                {job.skills?.map((s) => (
                  <span key={s} className="px-3 py-1 rounded-lg bg-slate-100 text-slate-800 text-xs font-medium">
                    {s}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Signals & Application Pipeline (1 col) */}
        <div className="space-y-6">
          {/* Application Tracker Card */}
          <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-900">Application Status</h3>
            <p className="text-xs text-slate-500">
              Track your hiring stages for this opportunity:
            </p>

            <div className="grid grid-cols-2 gap-2">
              {['Applied', 'Assessment', 'Interview', 'Offer', 'Rejected'].map((status) => (
                <button
                  key={status}
                  onClick={() => handleTrackApplication(status)}
                  className={`py-2 px-3 rounded-xl text-xs font-semibold border transition ${
                    appliedStatus === status
                      ? 'bg-brand-600 text-white border-brand-600 shadow-sm'
                      : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {status}
                </button>
              ))}
            </div>
          </div>

          {/* Verification Audit Checklist */}
          <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-brand-600" />
              <span>Trust & Signal Checklist</span>
            </h3>

            <div className="space-y-2.5 text-xs">
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50">
                <span className="text-slate-600">Company Domain Match</span>
                <span className={`font-semibold ${job.risk?.verification_signals?.domain_match ? 'text-emerald-600' : 'text-amber-600'}`}>
                  {job.risk?.verification_signals?.domain_match ? 'Verified' : 'Check'}
                </span>
              </div>

              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50">
                <span className="text-slate-600">No Upfront Payment Demands</span>
                <span className={`font-semibold ${!job.risk?.verification_signals?.payment_demanded ? 'text-emerald-600' : 'text-red-600'}`}>
                  {!job.risk?.verification_signals?.payment_demanded ? 'Clean' : 'Demanded'}
                </span>
              </div>

              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50">
                <span className="text-slate-600">Corporate Recruiter Email</span>
                <span className={`font-semibold ${!job.risk?.verification_signals?.free_email ? 'text-emerald-600' : 'text-amber-600'}`}>
                  {!job.risk?.verification_signals?.free_email ? 'Corporate' : 'Free Provider'}
                </span>
              </div>
            </div>

            {/* List Flagged Signals if any */}
            {job.risk?.signals && job.risk.signals.length > 0 && (
              <div className="pt-2 border-t border-slate-100 space-y-2">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  Flagged Risk Signals:
                </span>
                {job.risk.signals.map((sig, idx) => (
                  <div
                    key={idx}
                    className={`p-2.5 rounded-xl text-xs border ${
                      sig.severity === 'high'
                        ? 'bg-red-50 text-red-800 border-red-200'
                        : 'bg-amber-50 text-amber-800 border-amber-200'
                    }`}
                  >
                    {sig.message}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

