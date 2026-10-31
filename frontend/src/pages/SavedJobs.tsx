import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Bookmark, ShieldCheck, Trash2, ExternalLink, Sparkles, AlertCircle, RefreshCw } from 'lucide-react';
import api from '../services/api';
import { Job } from '../types';

export const SavedJobsPage: React.FC = () => {
  const [savedJobs, setSavedJobs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchSaved = async () => {
    try {
      setIsLoading(true);
      const res = await api.get('/jobs/saved');
      setSavedJobs(res.data || []);
    } catch (err) {
      console.error('Failed to load saved jobs:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSaved();
  }, []);

  const handleRemove = async (jobId: string) => {
    setSavedJobs((prev) => prev.filter((s) => s.job_id !== jobId));
    try {
      await api.delete(`/jobs/${jobId}/save`);
    } catch (err) {
      console.error('Failed to delete bookmark:', err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-200 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Saved Opportunities</h1>
          <p className="text-sm text-slate-500 mt-1">
            Keep track of verified listings you are preparing to apply for.
          </p>
        </div>
        <div className="text-xs text-slate-600 bg-indigo-50 border border-indigo-200 px-3 py-1.5 rounded-full font-semibold">
          {savedJobs.length} Bookmarks Stored
        </div>
      </div>

      {isLoading ? (
        <div className="p-16 text-center text-slate-500">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-3 text-brand-600" />
          <p className="font-medium text-sm">Loading your bookmarked jobs...</p>
        </div>
      ) : savedJobs.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
          <Bookmark className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-900">No saved jobs yet</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            When browsing opportunities, click the bookmark icon on any job card to save it here.
          </p>
          <Link
            to="/jobs"
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-brand-600 text-white font-medium text-xs hover:bg-brand-700 transition"
          >
            <span>Explore Jobs</span>
          </Link>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {savedJobs.map((item) => {
            const job = item.job;
            if (!job) return null;
            const riskScore = job.risk?.risk_score ?? 15;

            return (
              <div
                key={item.id}
                className="bg-white rounded-2xl border border-slate-200/80 p-6 flex flex-col justify-between space-y-4 hover:shadow-md transition"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${
                      riskScore <= 20
                        ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                        : 'bg-amber-50 text-amber-700 border-amber-200'
                    }`}>
                      Risk: {riskScore}/100
                    </span>

                    <button
                      onClick={() => handleRemove(job.id)}
                      className="p-1.5 text-slate-400 hover:text-red-600 rounded-lg transition"
                      title="Remove Bookmark"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <div>
                    <Link to={`/jobs/${job.id}`}>
                      <h3 className="font-bold text-slate-900 hover:text-brand-600 transition line-clamp-1">
                        {job.title}
                      </h3>
                    </Link>
                    <p className="text-xs font-semibold text-slate-600">{job.company} • {job.location || 'Remote'}</p>
                  </div>

                  <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
                    {job.description}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <Link
                    to={`/jobs/${job.id}`}
                    className="flex-1 py-2 text-center rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-semibold border border-slate-200 transition"
                  >
                    View Details
                  </Link>
                  {job.job_url && (
                    <a
                      href={job.job_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2 rounded-xl border border-slate-200 text-slate-500 hover:text-brand-600 hover:bg-slate-50 transition"
                      title="Apply on Source"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

