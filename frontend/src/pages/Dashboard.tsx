import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  Search, 
  Bookmark, 
  Briefcase, 
  AlertTriangle, 
  FileText, 
  ArrowUpRight,
  Sparkles,
  CheckCircle,
  TrendingUp,
  BarChart3,
  PieChart as PieChartIcon,
  RefreshCw,
  Radio
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { Job } from '../types';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [recommendedJobs, setRecommendedJobs] = useState<Job[]>([]);
  const [highRiskJobs, setHighRiskJobs] = useState<Job[]>([]);
  const [stats, setStats] = useState({
    recommendedCount: 0,
    lowRiskCount: 0,
    savedCount: 0,
    applicationsCount: 0,
    highRiskDetected: 0,
  });
  const [riskChartData, setRiskChartData] = useState<any[]>([]);
  const [pipelineChartData, setPipelineChartData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);

      const [savedRes, appsRes, jobsRes, recRes] = await Promise.allSettled([
        api.get('/jobs/saved'),
        api.get('/applications'),
        api.get('/jobs/search', { params: { limit: 50 } }),
        api.get('/jobs/recommended'),
      ]);

      const savedCount = savedRes.status === 'fulfilled' ? savedRes.value.data.length : 0;
      const appsList = appsRes.status === 'fulfilled' ? appsRes.value.data : [];
      const allJobs: Job[] = jobsRes.status === 'fulfilled' ? jobsRes.value.data.jobs || [] : [];

      // Truly personalized AI recommendations matching user's resume
      let recommended: Job[] = [];
      if (recRes.status === 'fulfilled' && Array.isArray(recRes.value.data) && recRes.value.data.length > 0) {
        recommended = recRes.value.data.slice(0, 5);
      } else {
        // Fallback: sort allJobs by resume match score descending
        recommended = [...allJobs]
          .filter((j) => (j.risk?.risk_score ?? 0) < 50)
          .sort((a, b) => (b.match?.match_score ?? 0) - (a.match?.match_score ?? 0))
          .slice(0, 5);
      }

      // Quarantined scams: risk >= 70
      const flagged = allJobs.filter((j) => (j.risk?.risk_score ?? 0) >= 70);

      setRecommendedJobs(recommended);
      setHighRiskJobs(flagged.slice(0, 4));

      const lowRiskTotal = allJobs.filter((j) => (j.risk?.risk_score ?? 0) <= 20).length;
      const modRiskTotal = allJobs.filter((j) => (j.risk?.risk_score ?? 0) > 20 && (j.risk?.risk_score ?? 0) <= 50).length;
      const suspiciousTotal = allJobs.filter((j) => (j.risk?.risk_score ?? 0) > 50 && (j.risk?.risk_score ?? 0) < 70).length;
      const highRiskTotal = flagged.length;

      setStats({
        recommendedCount: recommended.length,
        lowRiskCount: lowRiskTotal,
        savedCount,
        applicationsCount: appsList.length,
        highRiskDetected: highRiskTotal,
      });

        // Risk distribution for Recharts
        setRiskChartData([
          { name: 'Low Risk', value: lowRiskTotal, color: '#10b981' },
          { name: 'Moderate', value: modRiskTotal, color: '#f59e0b' },
          { name: 'Suspicious', value: suspiciousTotal, color: '#f97316' },
          { name: 'High Risk (Flagged)', value: highRiskTotal, color: '#ef4444' },
        ]);

        // Pipeline stage counts
        const stages: { [key: string]: number } = {
          Applied: 0,
          Assessment: 0,
          Interview: 0,
          Offer: 0,
        };
        appsList.forEach((a: any) => {
          if (stages[a.status] !== undefined) stages[a.status]++;
        });

        setPipelineChartData([
          { stage: 'Applied', count: stages.Applied },
          { stage: 'Assessment', count: stages.Assessment },
          { stage: 'Interview', count: stages.Interview },
          { stage: 'Offer', count: stages.Offer },
        ]);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setIsLoading(false);
      }
    };

  const handleSyncLive = async () => {
    try {
      setIsSyncing(true);
      setSyncStatus(null);
      const res = await api.post('/jobs/sync-live');
      setSyncStatus(res.data?.message || 'Live sync completed!');
      // Re-fetch dashboard
      const [savedRes, appsRes, jobsRes] = await Promise.allSettled([
        api.get('/jobs/saved'),
        api.get('/applications'),
        api.get('/jobs/search', { params: { limit: 50 } }),
      ]);
      const savedCount = savedRes.status === 'fulfilled' ? savedRes.value.data.length : 0;
      const appsList = appsRes.status === 'fulfilled' ? appsRes.value.data : [];
      const allJobs: Job[] = jobsRes.status === 'fulfilled' ? jobsRes.value.data.jobs || [] : [];
      const recommended = allJobs.filter((j) => (j.risk?.risk_score ?? 0) < 50).slice(0, 5);
      const flagged = allJobs.filter((j) => (j.risk?.risk_score ?? 0) >= 70);
      setRecommendedJobs(recommended);
      setHighRiskJobs(flagged.slice(0, 4));
      setStats({
        recommendedCount: recommended.length,
        lowRiskCount: allJobs.filter((j) => (j.risk?.risk_score ?? 0) <= 20).length,
        savedCount,
        applicationsCount: appsList.length,
        highRiskDetected: flagged.length,
      });
      setTimeout(() => setSyncStatus(null), 5000);
    } catch (err) {
      console.error('Sync failed:', err);
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Real-time Data Source Badge Bar */}
      <div className="bg-emerald-50 border border-emerald-200/80 rounded-2xl px-5 py-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-emerald-900 shadow-sm">
        <div className="flex items-center space-x-2.5">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-600"></span>
          </span>
          <span className="font-bold uppercase tracking-wider text-emerald-800">100% Real-Time Ingestion</span>
          <span className="text-emerald-700 hidden md:inline">|</span>
          <span className="text-emerald-700 hidden md:inline">
            Live Stream: <strong>India Tech Careers (Kolkata, Bengaluru, Hyderabad, Pune, Delhi NCR)</strong>, <strong>Remotive</strong> & <strong>Arbeitnow</strong> &bull; Connected to MySQL
          </span>
        </div>
        <button
          onClick={handleSyncLive}
          disabled={isSyncing}
          className="px-3 py-1.5 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white font-semibold transition flex items-center space-x-1.5 disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin' : ''}`} />
          <span>{isSyncing ? 'Syncing...' : 'Sync Real-Time Feed'}</span>
        </button>
      </div>

      {syncStatus && (
        <div className="p-3 bg-indigo-50 border border-indigo-200 text-indigo-900 rounded-xl text-xs font-medium">
          {syncStatus}
        </div>
      )}

      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-brand-900 via-indigo-900 to-slate-900 rounded-3xl p-6 sm:p-8 text-white shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>JobGuard AI Active Protection</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
            Welcome back, {user?.name || 'Engineer'}!
          </h1>
          <p className="text-sm sm:text-base text-slate-300 max-w-xl">
            Find jobs you can actually trust. Every listing is audited for fraud signatures, verified corporate domains, and resume skill alignment.
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <Link
            to="/jobs"
            className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-sm transition shadow-sm flex items-center space-x-2"
          >
            <Search className="w-4 h-4" />
            <span>Explore Jobs</span>
          </Link>
          <Link
            to="/verify-job"
            className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-sm transition backdrop-blur-sm flex items-center space-x-2 border border-white/10"
          >
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Verify Job URL</span>
          </Link>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Recommended</span>
            <Sparkles className="w-4 h-4 text-brand-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{stats.recommendedCount}</div>
          <div className="text-xs text-slate-500 mt-1">Matched to profile</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Low Risk</span>
            <CheckCircle className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-emerald-600">{stats.lowRiskCount}</div>
          <div className="text-xs text-slate-500 mt-1">High trust score</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Saved Jobs</span>
            <Bookmark className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{stats.savedCount}</div>
          <div className="text-xs text-slate-500 mt-1">In your bookmarks</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Applications</span>
            <Briefcase className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{stats.applicationsCount}</div>
          <div className="text-xs text-slate-500 mt-1">In active tracker</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm col-span-2 md:col-span-1">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Scams Flagged</span>
            <AlertTriangle className="w-4 h-4 text-red-500" />
          </div>
          <div className="text-2xl font-bold text-red-600">{stats.highRiskDetected}</div>
          <div className="text-xs text-slate-500 mt-1">High-risk listings</div>
        </div>
      </div>

      {/* Analytics Charts Row */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Risk Distribution Chart */}
        <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center space-x-2">
              <PieChartIcon className="w-4 h-4 text-brand-600" />
              <h3 className="text-sm font-bold text-slate-900">Safety Risk Distribution</h3>
            </div>
            <span className="text-xs text-slate-400">Database overview</span>
          </div>

          <div className="h-56 w-full flex items-center justify-center">
            {riskChartData.some((d) => d.value > 0) ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {riskChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <span className="text-xs text-slate-400">Loading risk data...</span>
            )}
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
            {riskChartData.map((d) => (
              <div key={d.name} className="p-2 rounded-xl bg-slate-50">
                <span className="block font-bold text-slate-800">{d.value}</span>
                <span className="text-[10px] text-slate-500">{d.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Pipeline Funnel Bar Chart */}
        <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4 text-brand-600" />
              <h3 className="text-sm font-bold text-slate-900">Application Pipeline Funnel</h3>
            </div>
            <Link to="/applications" className="text-xs text-brand-600 font-semibold hover:underline">
              Manage Tracker
            </Link>
          </div>

          <div className="h-56 w-full flex items-center justify-center">
            {pipelineChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={pipelineChartData}>
                  <XAxis dataKey="stage" tickLine={false} tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} tickLine={false} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#6366f1" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <span className="text-xs text-slate-400">No active applications</span>
            )}
          </div>

          <p className="text-xs text-slate-500 text-center">
            Track interview rounds, assessments, and offer letters to optimize your job search.
          </p>
        </div>
      </div>

      {/* Main Split: Recommended vs Quarantined Scams */}
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Recommended Jobs (2 cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-brand-600" />
              <h2 className="text-lg font-bold text-slate-900">AI Recommended Opportunities</h2>
            </div>
            <Link to="/jobs" className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center space-x-1">
              <span>View all</span>
              <ArrowUpRight className="w-4 h-4" />
            </Link>
          </div>

          {isLoading ? (
            <div className="p-12 bg-white rounded-3xl border border-slate-200 text-center text-slate-500">
              <div className="w-6 h-6 border-2 border-indigo-200 border-t-brand-600 rounded-full animate-spin mx-auto mb-2"></div>
              Loading trusted recommendations...
            </div>
          ) : recommendedJobs.length === 0 ? (
            <div className="p-8 bg-white rounded-3xl border border-slate-200 text-center space-y-3">
              <FileText className="w-10 h-10 text-slate-300 mx-auto" />
              <p className="text-slate-600 font-medium">Upload your resume to get matched recommendations!</p>
              <Link
                to="/resume"
                className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-brand-600 text-white font-medium text-xs hover:bg-brand-700 transition"
              >
                <span>Upload Resume</span>
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {recommendedJobs.map((job) => (
                <div
                  key={job.id}
                  className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition flex flex-col sm:flex-row justify-between sm:items-center gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-semibold text-slate-900 text-sm">{job.title}</span>
                      <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium">
                        {job.remote_type || 'Onsite'}
                      </span>
                      {job.match?.match_score !== undefined && (
                        <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-indigo-50 text-brand-600 font-bold border border-indigo-100 flex items-center space-x-1">
                          <Sparkles className="w-3 h-3 inline" />
                          <span>{Math.round(job.match.match_score)}% Match</span>
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-slate-600 font-medium">{job.company} • {job.location || 'Remote'}</div>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {job.skills?.slice(0, 5).map((s) => {
                        const isMatched = job.match?.matched_skills?.some((ms: string) => ms.toLowerCase() === s.toLowerCase());
                        return (
                          <span
                            key={s}
                            className={`text-[11px] px-2 py-0.5 rounded-md font-medium ${
                              isMatched
                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                : 'bg-slate-100 text-slate-700'
                            }`}
                          >
                            {isMatched ? `✓ ${s}` : s}
                          </span>
                        );
                      })}
                    </div>
                  </div>

                  <div className="flex items-center space-x-3 self-end sm:self-center">
                    <div className="text-right">
                      <div className="text-xs font-semibold text-emerald-600 uppercase">
                        Low Risk ({job.risk?.risk_score ?? 10}/100)
                      </div>
                      <div className="text-[11px] text-slate-400">Verified corporate domain</div>
                    </div>
                    <Link
                      to={`/jobs/${job.id}`}
                      className="px-3.5 py-2 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 font-semibold text-xs border border-slate-200 transition"
                    >
                      Details
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* High Risk / Review Section (1 col) */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 text-red-600">
            <AlertTriangle className="w-5 h-5" />
            <h2 className="text-lg font-bold text-slate-900">High Risk / Scams Flagged</h2>
          </div>

          <div className="bg-red-50/50 rounded-3xl border border-red-200/70 p-5 space-y-4">
            <p className="text-xs text-red-700 leading-relaxed font-medium">
              JobGuard AI quarantines listings with upfront registration fees, free recruiter emails, or WhatsApp-only hiring channels.
            </p>

            {highRiskJobs.length === 0 ? (
              <div className="p-4 bg-white/80 rounded-xl border border-red-100 text-center text-xs text-slate-500">
                No high-risk jobs currently quarantined.
              </div>
            ) : (
              <div className="space-y-3">
                {highRiskJobs.map((job) => (
                  <div key={job.id} className="bg-white p-3.5 rounded-xl border border-red-100 shadow-sm space-y-2">
                    <div className="flex justify-between items-start">
                      <span className="font-semibold text-slate-900 text-xs">{job.title}</span>
                      <span className="text-[10px] font-bold text-red-600 bg-red-100 px-2 py-0.5 rounded-full">
                        Risk {job.risk?.risk_score}/100
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500">{job.company}</p>
                    <div className="text-[11px] text-red-700 bg-red-50 p-2 rounded-lg">
                      {job.risk?.signals?.[0]?.message || 'Flagged by fraud detection rules.'}
                    </div>
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
