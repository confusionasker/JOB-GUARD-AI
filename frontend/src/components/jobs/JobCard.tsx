import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  AlertTriangle, 
  Bookmark, 
  ExternalLink, 
  MapPin, 
  Briefcase, 
  Sparkles,
  CheckCircle,
  Building2
} from 'lucide-react';
import { Job } from '../../types';

interface JobCardProps {
  job: Job;
  onToggleSave?: (jobId: string, currentSaved: boolean) => void;
}

export const JobCard: React.FC<JobCardProps> = ({ job, onToggleSave }) => {
  const riskScore = job.risk?.risk_score ?? 15;
  const riskLevel = job.risk?.risk_level ?? 'Low Risk';
  const matchScore = job.match?.match_score ?? null;

  // Determine risk styling
  const getRiskBadge = () => {
    if (riskScore <= 20) {
      return {
        bg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
        dot: 'bg-emerald-500',
        label: 'Low Risk',
      };
    } else if (riskScore <= 50) {
      return {
        bg: 'bg-amber-50 text-amber-700 border-amber-200',
        dot: 'bg-amber-500',
        label: 'Moderate Risk',
      };
    } else if (riskScore <= 75) {
      return {
        bg: 'bg-orange-50 text-orange-700 border-orange-200',
        dot: 'bg-orange-500',
        label: 'Suspicious',
      };
    } else {
      return {
        bg: 'bg-red-50 text-red-700 border-red-200',
        dot: 'bg-red-500',
        label: 'High Risk / Scam',
      };
    }
  };

  const riskBadge = getRiskBadge();

  return (
    <div className={`bg-white rounded-2xl border p-6 transition-all hover:shadow-md flex flex-col justify-between space-y-5 ${
      riskScore >= 76 ? 'border-red-200/90 bg-red-50/20' : 'border-slate-200/80'
    }`}>
      <div className="space-y-4">
        {/* Top Badges: Risk Score & Resume Match */}
        <div className="flex items-center justify-between gap-2">
          {/* Risk Badge */}
          <div className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${riskBadge.bg}`}>
            <span className={`w-2 h-2 rounded-full ${riskBadge.dot}`}></span>
            <span>{riskBadge.label} ({riskScore}/100)</span>
          </div>

          {/* Match Score Badge (Kept strictly separate from risk) */}
          {matchScore !== null ? (
            <div className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold border ${
              matchScore >= 80 
                ? 'bg-indigo-50 text-brand-700 border-indigo-200' 
                : matchScore >= 60 
                ? 'bg-blue-50 text-blue-700 border-blue-200' 
                : 'bg-slate-100 text-slate-600 border-slate-200'
            }`}>
              <Sparkles className="w-3 h-3 text-brand-600" />
              <span>Match: {Math.round(matchScore)}%</span>
            </div>
          ) : (
            <span className="text-[11px] text-slate-400">Match pending</span>
          )}
        </div>

        {/* Job Title & Company */}
        <div>
          <Link to={`/jobs/${job.id}`}>
            <h3 className="text-lg font-bold text-slate-900 hover:text-brand-600 transition-colors line-clamp-1">
              {job.title}
            </h3>
          </Link>
          <div className="flex items-center space-x-2 text-sm text-slate-600 mt-1">
            <Building2 className="w-4 h-4 text-slate-400 flex-shrink-0" />
            <span className="font-semibold text-slate-800">{job.company}</span>
            <span>•</span>
            <span className="text-slate-500 flex items-center space-x-1">
              <MapPin className="w-3.5 h-3.5 text-slate-400 inline" />
              <span>{job.location || 'Remote'}</span>
            </span>
          </div>
        </div>

        {/* Location & Remote Mode Pill */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 font-medium">
            {job.remote_type || 'Onsite'}
          </span>
          <span className="px-2.5 py-1 rounded-md bg-indigo-50/70 text-indigo-700 font-medium border border-indigo-100">
            {job.source || 'Direct'}
          </span>
          {job.salary_min && (
            <span className="px-2.5 py-1 rounded-md bg-emerald-50 text-emerald-700 font-semibold border border-emerald-200">
              {job.currency === 'INR'
                ? `₹${(job.salary_min / 100000).toFixed(1).replace('.0', '')}L - ₹${((job.salary_max || job.salary_min) / 100000).toFixed(1).replace('.0', '')}L PA`
                : `$${Math.round(job.salary_min / 1000)}k - $${Math.round((job.salary_max || job.salary_min) / 1000)}k`}
            </span>
          )}
        </div>

        {/* Skills Preview */}
        <div className="flex flex-wrap gap-1.5 pt-1">
          {job.skills?.slice(0, 5).map((skill) => (
            <span
              key={skill}
              className="text-xs bg-slate-50 border border-slate-200/80 text-slate-700 px-2.5 py-0.5 rounded-md font-medium"
            >
              {skill}
            </span>
          ))}
          {job.skills?.length > 5 && (
            <span className="text-xs text-slate-400 self-center">
              +{job.skills.length - 5} more
            </span>
          )}
        </div>

        {/* Risk Warning Notice if High Risk */}
        {riskScore >= 70 && (
          <div className="p-3 rounded-xl bg-red-100/70 border border-red-200 text-red-800 text-xs flex items-start space-x-2">
            <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span className="line-clamp-2">
              {job.risk?.signals?.[0]?.message || 'Flagged by fraud detection engine for suspicious conditions.'}
            </span>
          </div>
        )}
      </div>

      {/* Card Action Buttons */}
      <div className="pt-4 border-t border-slate-100 flex items-center justify-between gap-3">
        <Link
          to={`/jobs/${job.id}`}
          className="flex-1 py-2 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold text-center transition"
        >
          View Details
        </Link>

        {onToggleSave && (
          <button
            onClick={() => onToggleSave(job.id, !!job.is_saved)}
            title={job.is_saved ? 'Remove Bookmark' : 'Save Job'}
            className={`p-2 rounded-xl border transition ${
              job.is_saved
                ? 'bg-indigo-50 border-brand-200 text-brand-600'
                : 'bg-white border-slate-200 text-slate-400 hover:text-slate-700 hover:bg-slate-50'
            }`}
          >
            <Bookmark className={`w-4 h-4 ${job.is_saved ? 'fill-brand-600' : ''}`} />
          </button>
        )}

        {job.job_url ? (
          <a
            href={job.job_url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 rounded-xl bg-white border border-slate-200 text-slate-600 hover:text-brand-600 hover:bg-slate-50 transition"
            title="Open Original Listing"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        ) : null}
      </div>
    </div>
  );
};

