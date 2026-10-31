import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Link as LinkIcon, 
  AlertTriangle, 
  CheckCircle2, 
  Sparkles, 
  ArrowRight,
  FileText,
  Building2,
  RefreshCw
} from 'lucide-react';
import api from '../services/api';

export const VerifyJobPage: React.FC = () => {
  const [url, setUrl] = useState('');
  const [manualTitle, setManualTitle] = useState('');
  const [manualCompany, setManualCompany] = useState('');
  const [manualDescription, setManualDescription] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [platformWarning, setPlatformWarning] = useState<string | null>(null);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsVerifying(true);
    setPlatformWarning(null);
    setResult(null);

    try {
      const payload: any = {};
      if (url.trim()) payload.url = url.trim();
      if (manualTitle.trim()) payload.title = manualTitle.trim();
      if (manualCompany.trim()) payload.company = manualCompany.trim();
      if (manualDescription.trim()) payload.description = manualDescription.trim();

      const res = await api.post('/jobs/verify-url', payload);
      const data = res.data;

      if (!data.success) {
        setPlatformWarning(data.error);
      } else {
        setResult(data);
      }
    } catch (err: any) {
      console.error(err);
      setPlatformWarning(err.response?.data?.detail || 'Verification request failed.');
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="text-center space-y-2 border-b border-slate-200 pb-6">
        <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-brand-600 flex items-center justify-center mx-auto mb-2 border border-indigo-100 shadow-inner">
          <ShieldCheck className="w-7 h-7" />
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Verify Any Job Opportunity
        </h1>
        <p className="text-sm text-slate-500 max-w-lg mx-auto">
          Paste a job link or job description from any board. We audit upfront fee demands, recruiter domains, and match the role to your resume.
        </p>
      </div>

      {/* Main Verification Card */}
      <div className="bg-white rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-sm space-y-6">
        <form onSubmit={handleVerify} className="space-y-5">
          {/* URL Input */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
              Job URL
            </label>
            <div className="relative">
              <LinkIcon className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://company.com/careers/job-id or job posting link"
                className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-slate-200 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-600"
              />
            </div>
          </div>

          {/* Platform Access Notice */}
          {platformWarning && (
            <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-800 text-xs space-y-2">
              <div className="flex items-start space-x-2">
                <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5 text-amber-600" />
                <span className="font-semibold">{platformWarning}</span>
              </div>
              <p className="text-amber-700">
                Please paste the job title, company, and description into the fallback fields below for an instant safety score.
              </p>
            </div>
          )}

          {/* Fallback Manual Fields */}
          <div className="pt-2 border-t border-slate-100 space-y-4">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Or Paste Job Details Manually (Recommended fallback):
            </span>

            <div className="grid sm:grid-cols-2 gap-4">
              <input
                type="text"
                value={manualTitle}
                onChange={(e) => setManualTitle(e.target.value)}
                placeholder="Job Title (e.g. Senior Python Developer)"
                className="w-full px-4 py-2 rounded-xl border border-slate-200 text-slate-900 text-xs focus:outline-none focus:border-brand-600"
              />
              <input
                type="text"
                value={manualCompany}
                onChange={(e) => setManualCompany(e.target.value)}
                placeholder="Company Name (e.g. Acme Corp)"
                className="w-full px-4 py-2 rounded-xl border border-slate-200 text-slate-900 text-xs focus:outline-none focus:border-brand-600"
              />
            </div>

            <textarea
              rows={5}
              value={manualDescription}
              onChange={(e) => setManualDescription(e.target.value)}
              placeholder="Paste full job description, requirements, or recruiter communication here..."
              className="w-full p-4 rounded-xl border border-slate-200 text-slate-900 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-600"
            />
          </div>

          <button
            type="submit"
            disabled={isVerifying || (!url && !manualDescription)}
            className="w-full py-3 px-6 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-sm shadow-md shadow-brand-600/20 transition flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {isVerifying ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Auditing Safety Signals & Running ML Classifier...</span>
              </>
            ) : (
              <>
                <ShieldCheck className="w-5 h-5" />
                <span>Analyze & Verify Job</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Results Section */}
      {result && result.success && (
        <div className="bg-white rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-sm space-y-6 animate-fadeIn">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-100 pb-5">
            <div>
              <span className="text-xs text-slate-400 font-semibold uppercase">Verification Result</span>
              <h2 className="text-2xl font-bold text-slate-900">{result.job.title}</h2>
              <div className="text-sm font-semibold text-slate-600">{result.job.company}</div>
            </div>

            {/* Risk Badge */}
            <div className={`px-4 py-2 rounded-2xl border text-center ${
              result.risk.risk_score <= 20
                ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                : result.risk.risk_score <= 50
                ? 'bg-amber-50 text-amber-800 border-amber-200'
                : 'bg-red-50 text-red-800 border-red-200'
            }`}>
              <div className="text-2xl font-extrabold">{result.risk.risk_score} / 100</div>
              <div className="text-xs font-bold uppercase">{result.risk.risk_level}</div>
            </div>
          </div>

          {/* AI Explanation & Recommendation */}
          <div className="p-5 rounded-2xl bg-indigo-50/50 border border-indigo-100 space-y-2">
            <div className="flex items-center space-x-2 text-brand-900 font-bold text-sm">
              <Sparkles className="w-4 h-4 text-brand-600" />
              <span>AI Match & Safety Verdict</span>
            </div>
            <p className="text-xs text-slate-700 leading-relaxed">
              {result.recommendation.explanation}
            </p>
          </div>

          {/* Signals Grid */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">Audit Breakdown</h3>

            <div className="grid sm:grid-cols-2 gap-3">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs flex justify-between">
                <span className="text-slate-600">Resume Match Score:</span>
                <span className="font-bold text-brand-700">{Math.round(result.match.match_score)}%</span>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs flex justify-between">
                <span className="text-slate-600">Upfront Fee Demand:</span>
                <span className={`font-bold ${result.risk.verification_signals.payment_demanded ? 'text-red-600' : 'text-emerald-600'}`}>
                  {result.risk.verification_signals.payment_demanded ? 'Detected (High Risk)' : 'None Detected'}
                </span>
              </div>
            </div>

            {result.risk.signals.length > 0 && (
              <div className="space-y-2 pt-2">
                <span className="text-xs font-bold text-slate-600">Flagged Risk Signals:</span>
                {result.risk.signals.map((s: any, idx: number) => (
                  <div key={idx} className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-800">
                    {s.message}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

