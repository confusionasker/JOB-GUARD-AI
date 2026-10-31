import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Briefcase, Calendar, Building2, CheckCircle2, Clock, XCircle, ArrowUpRight, RefreshCw } from 'lucide-react';
import api from '../services/api';
import { Application } from '../types';

export const ApplicationsPage: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchApplications = async () => {
    try {
      setIsLoading(true);
      const res = await api.get('/applications');
      setApplications(res.data || []);
    } catch (err) {
      console.error('Failed to load applications:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, []);

  const handleStatusChange = async (appId: string, newStatus: string) => {
    setApplications((prev) =>
      prev.map((a) => (a.id === appId ? { ...a, status: newStatus as any } : a))
    );
    try {
      await api.patch(`/applications/${appId}`, { status: newStatus });
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  const statusOptions = ['Applied', 'Assessment', 'Interview', 'Offer', 'Rejected'];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Offer':
        return 'bg-emerald-50 text-emerald-800 border-emerald-200';
      case 'Interview':
        return 'bg-indigo-50 text-brand-700 border-indigo-200';
      case 'Assessment':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'Rejected':
        return 'bg-slate-100 text-slate-500 border-slate-200';
      default:
        return 'bg-amber-50 text-amber-800 border-amber-200';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-200 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Application Pipeline Tracker</h1>
          <p className="text-sm text-slate-500 mt-1">
            Track your interview stages, take notes, and monitor response status across your applications.
          </p>
        </div>
        <div className="text-xs text-slate-600 bg-slate-100 px-3 py-1.5 rounded-full font-semibold">
          {applications.length} Active Records
        </div>
      </div>

      {isLoading ? (
        <div className="p-16 text-center text-slate-500">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-3 text-brand-600" />
          <p className="font-medium text-sm">Loading your application pipeline...</p>
        </div>
      ) : applications.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
          <Briefcase className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-900">No applications tracked yet</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            When you view any job listing, you can track it into your application pipeline with a single click.
          </p>
          <Link
            to="/jobs"
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-brand-600 text-white font-medium text-xs hover:bg-brand-700 transition"
          >
            <span>Browse Jobs</span>
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/60 text-slate-500 uppercase font-semibold">
                  <th className="py-4 px-6">Role & Company</th>
                  <th className="py-4 px-6">Pipeline Stage</th>
                  <th className="py-4 px-6">Applied Date</th>
                  <th className="py-4 px-6">Safety Score</th>
                  <th className="py-4 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {applications.map((app) => {
                  const job = app.job;
                  const riskScore = job?.risk?.risk_score ?? 15;

                  return (
                    <tr key={app.id} className="hover:bg-slate-50/50 transition">
                      <td className="py-4 px-6">
                        {job ? (
                          <div>
                            <Link
                              to={`/jobs/${job.id}`}
                              className="font-bold text-slate-900 hover:text-brand-600 text-sm transition"
                            >
                              {job.title}
                            </Link>
                            <p className="text-slate-500 font-medium">{job.company} • {job.location || 'Remote'}</p>
                          </div>
                        ) : (
                          <span className="font-semibold text-slate-800">Job Reference {app.job_id}</span>
                        )}
                      </td>

                      <td className="py-4 px-6">
                        <select
                          value={app.status}
                          onChange={(e) => handleStatusChange(app.id, e.target.value)}
                          className={`px-3 py-1 rounded-xl border text-xs font-semibold focus:outline-none ${getStatusBadge(app.status)}`}
                        >
                          {statusOptions.map((opt) => (
                            <option key={opt} value={opt} className="bg-white text-slate-900">
                              {opt}
                            </option>
                          ))}
                        </select>
                      </td>

                      <td className="py-4 px-6 text-slate-500">
                        {app.applied_date
                          ? new Date(app.applied_date).toLocaleDateString()
                          : 'Recent'}
                      </td>

                      <td className="py-4 px-6">
                        <span className={`px-2.5 py-0.5 rounded-full font-bold border text-[11px] ${
                          riskScore <= 20
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                            : 'bg-amber-50 text-amber-700 border-amber-200'
                        }`}>
                          Risk: {riskScore}/100
                        </span>
                      </td>

                      <td className="py-4 px-6 text-right">
                        {job && (
                          <Link
                            to={`/jobs/${job.id}`}
                            className="inline-flex items-center space-x-1 text-brand-600 hover:text-brand-700 font-semibold"
                          >
                            <span>View</span>
                            <ArrowUpRight className="w-3.5 h-3.5" />
                          </Link>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

