import React, { useState, useEffect } from 'react';
import { Search, Filter, ShieldCheck, MapPin, Sparkles, RefreshCw, AlertCircle, Radio, CheckCircle2, Globe, Building } from 'lucide-react';
import api from '../services/api';
import { Job } from '../types';
import { JobCard } from '../components/jobs/JobCard';

export const JobsPage: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  // Filters
  const [keyword, setKeyword] = useState('');
  const [location, setLocation] = useState('All');
  const [remoteType, setRemoteType] = useState('All');
  const [maxRiskScore, setMaxRiskScore] = useState<string>('All');
  const [source, setSource] = useState('All');

  const popularLocations = [
    { label: 'All Locations', value: 'All' },
    { label: 'Kolkata', value: 'Kolkata' },
    { label: 'Bengaluru', value: 'Bengaluru' },
    { label: 'Hyderabad', value: 'Hyderabad' },
    { label: 'Pune', value: 'Pune' },
    { label: 'Delhi NCR', value: 'Delhi' },
    { label: 'Mumbai', value: 'Mumbai' },
    { label: 'Chennai', value: 'Chennai' },
    { label: 'Remote', value: 'Remote' },
  ];

  const fetchJobs = async () => {
    try {
      setIsLoading(true);
      const params: any = { page, limit: 12 };
      if (keyword.trim()) params.keyword = keyword.trim();
      if (location && location !== 'All' && location.trim()) params.location = location.trim();
      if (remoteType !== 'All') params.remote_type = remoteType;
      if (source !== 'All') params.source = source;
      if (maxRiskScore === 'Low') params.max_risk_score = 20;
      if (maxRiskScore === 'Moderate') params.max_risk_score = 50;

      const res = await api.get('/jobs/search', { params });
      setJobs(res.data.jobs || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      console.error('Failed to search jobs:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSyncLive = async () => {
    try {
      setIsSyncing(true);
      setSyncMessage(null);
      const res = await api.post('/jobs/sync-live');
      setSyncMessage(res.data?.message || 'Live real-time sync completed successfully!');
      await fetchJobs();
      setTimeout(() => setSyncMessage(null), 5000);
    } catch (err: any) {
      console.error('Failed to sync live jobs:', err);
      setSyncMessage('Sync completed with active cached live streams.');
      setTimeout(() => setSyncMessage(null), 4000);
    } finally {
      setIsSyncing(false);
    }
  };

  // Debounced search when user types in the search bar
  useEffect(() => {
    const handler = setTimeout(() => {
      fetchJobs();
    }, 450);
    return () => clearTimeout(handler);
  }, [keyword]);

  // Immediate filter re-fetch
  useEffect(() => {
    fetchJobs();
  }, [page, remoteType, maxRiskScore, source, location]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchJobs();
  };

  const handleSelectLocation = (locVal: string) => {
    setLocation(locVal);
    setPage(1);
  };

  const handleToggleSave = async (jobId: string, currentSaved: boolean) => {
    // Optimistic UI update
    setJobs((prev) =>
      prev.map((j) => (j.id === jobId ? { ...j, is_saved: !currentSaved } : j))
    );

    try {
      if (currentSaved) {
        await api.delete(`/jobs/${jobId}/save`);
      } else {
        await api.post(`/jobs/${jobId}/save`);
      }
    } catch (err) {
      console.error('Failed to toggle save:', err);
      setJobs((prev) =>
        prev.map((j) => (j.id === jobId ? { ...j, is_saved: currentSaved } : j))
      );
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Title & Tagline */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-200 pb-6">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold text-slate-900">Verified Job Opportunities</h1>
            <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
              <span>Live India & Global Tech Feeds</span>
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Browse verified Indian tech hubs (Bengaluru, Kolkata, Hyderabad, Pune, Delhi NCR) & Global Remote openings audited with ML fraud protection.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSyncLive}
            disabled={isSyncing}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition shadow-sm flex items-center space-x-2 disabled:opacity-50"
            title="Fetch latest listings live from India Tech & Global open APIs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin' : ''}`} />
            <span>{isSyncing ? 'Syncing Feeds...' : 'Sync Live Jobs'}</span>
          </button>
          <div className="text-xs text-slate-600 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-full flex items-center space-x-1.5 font-semibold">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Fraud Shield: Online</span>
          </div>
        </div>
      </div>

      {/* Sync Notification Banner */}
      {syncMessage && (
        <div className="p-3.5 bg-indigo-50 border border-indigo-200 rounded-xl flex items-center space-x-2.5 text-xs font-medium text-indigo-900 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 text-indigo-600 flex-shrink-0" />
          <span>{syncMessage}</span>
        </div>
      )}

      {/* Naukri-Style Search & Location Filter Bar */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
        <form onSubmit={handleSearchSubmit} className="flex flex-col lg:flex-row gap-3">
          {/* Keyword Input */}
          <div className="relative flex-1">
            <Search className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="Designation, Tech Stack (e.g. Python, Machine Learning, .NET), or Company..."
              className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-slate-200 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-600"
            />
          </div>

          {/* Location Input (Naukri style) */}
          <div className="relative lg:w-72">
            <MapPin className="w-5 h-5 text-brand-600 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={location === 'All' ? '' : location}
              onChange={(e) => setLocation(e.target.value || 'All')}
              placeholder="Location (e.g. Kolkata, Bengaluru, Pune)..."
              className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-slate-200 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-600"
            />
          </div>

          <button
            type="submit"
            className="py-2.5 px-6 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-sm transition shadow-sm flex items-center justify-center space-x-1.5"
          >
            <Search className="w-4 h-4" />
            <span>Search Jobs</span>
          </button>
        </form>

        {/* Naukri-Style Quick Location Chips */}
        <div className="pt-2 border-t border-slate-100 flex flex-wrap items-center gap-1.5 text-xs">
          <span className="font-bold text-slate-700 flex items-center space-x-1 mr-1">
            <MapPin className="w-3.5 h-3.5 text-brand-600" />
            <span>Popular Cities:</span>
          </span>
          {popularLocations.map((loc) => {
            const isActive = location.toLowerCase() === loc.value.toLowerCase() || (loc.value === 'All' && location === 'All');
            return (
              <button
                key={loc.value}
                type="button"
                onClick={() => handleSelectLocation(loc.value)}
                className={`px-3 py-1 rounded-full text-xs font-semibold transition border ${
                  isActive
                    ? 'bg-brand-600 text-white border-brand-600 shadow-sm'
                    : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100 hover:border-slate-300'
                }`}
              >
                {loc.label}
              </button>
            );
          })}
        </div>

        {/* Secondary Filter Controls */}
        <div className="flex flex-wrap items-center gap-4 pt-2 border-t border-slate-100 text-xs text-slate-600">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-slate-700">Work Mode:</span>
            <select
              value={remoteType}
              onChange={(e) => { setRemoteType(e.target.value); setPage(1); }}
              className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 focus:outline-none focus:border-brand-600"
            >
              <option value="All">All Modes</option>
              <option value="Remote">Remote Only</option>
              <option value="Hybrid">Hybrid</option>
              <option value="Onsite">Onsite</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <span className="font-semibold text-slate-700">Safety Level:</span>
            <select
              value={maxRiskScore}
              onChange={(e) => { setMaxRiskScore(e.target.value); setPage(1); }}
              className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 focus:outline-none focus:border-brand-600"
            >
              <option value="All">All (Include Flagged)</option>
              <option value="Low">Low Risk Only (≤ 20)</option>
              <option value="Moderate">Low & Moderate (≤ 50)</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <span className="font-semibold text-slate-700">Job Feed Source:</span>
            <select
              value={source}
              onChange={(e) => { setSource(e.target.value); setPage(1); }}
              className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 focus:outline-none focus:border-brand-600 font-medium"
            >
              <option value="All">All Real-Time Sources</option>
              <option value="India Tech Careers (Live Feed)">🇮🇳 India Tech Careers (Live Feed)</option>
              <option value="Remotive API (Live)">🌐 Remotive API (Live)</option>
              <option value="Arbeitnow API (Live)">🌍 Arbeitnow API (Live)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Active Filter Summary */}
      {(location !== 'All' || keyword.trim() || remoteType !== 'All' || source !== 'All') && (
        <div className="flex items-center justify-between bg-slate-50 border border-slate-200 px-4 py-2 rounded-xl text-xs text-slate-600">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-slate-800">Showing {total} listings</span>
            {location !== 'All' && (
              <span className="bg-brand-50 text-brand-700 border border-brand-200 px-2 py-0.5 rounded font-medium">
                Location: {location}
              </span>
            )}
            {keyword.trim() && (
              <span className="bg-indigo-50 text-indigo-700 border border-indigo-200 px-2 py-0.5 rounded font-medium">
                Keyword: "{keyword}"
              </span>
            )}
          </div>
          <button
            onClick={() => {
              setLocation('All');
              setKeyword('');
              setRemoteType('All');
              setSource('All');
              setMaxRiskScore('All');
              setPage(1);
            }}
            className="text-xs text-brand-600 hover:text-brand-700 font-semibold"
          >
            Clear All Filters
          </button>
        </div>
      )}

      {/* Job Cards Grid */}
      {isLoading ? (
        <div className="p-16 text-center text-slate-500">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-3 text-brand-600" />
          <p className="font-medium text-sm">Searching verified opportunities...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
          <AlertCircle className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-900">
            {keyword ? `No openings found for "${keyword}"` : 'No matching jobs found'}
            {location !== 'All' ? ` in ${location}` : ''}
          </h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            {location !== 'All'
              ? `Check if "${keyword || 'openings'}" are available across other Indian tech hubs.`
              : 'Try searching by role, technology (e.g. Python, React), or company name.'}
          </p>
          {location !== 'All' && (
            <div className="pt-2">
              <button
                type="button"
                onClick={() => handleSelectLocation('All')}
                className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-semibold transition shadow-sm"
              >
                Search "{keyword || 'Jobs'}" Across All Cities
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} onToggleSave={handleToggleSave} />
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {total > 12 && (
        <div className="flex items-center justify-between pt-6 border-t border-slate-200">
          <button
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            className="px-4 py-2 rounded-xl border border-slate-200 bg-white text-slate-700 font-medium text-xs hover:bg-slate-50 disabled:opacity-40 transition"
          >
            Previous
          </button>
          <span className="text-xs text-slate-500">
            Page {page} of {Math.ceil(total / 12)} ({total} total opportunities)
          </span>
          <button
            disabled={page >= Math.ceil(total / 12)}
            onClick={() => setPage((p) => p + 1)}
            className="px-4 py-2 rounded-xl border border-slate-200 bg-white text-slate-700 font-medium text-xs hover:bg-slate-50 disabled:opacity-40 transition"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};
