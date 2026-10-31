import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Search, FileText, CheckCircle2, AlertTriangle, ArrowRight, Sparkles, Building2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Landing: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-20 pb-20">
      {/* Hero Section */}
      <section className="relative pt-12 pb-16 overflow-hidden">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 text-center space-y-6">
          <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-indigo-50 border border-indigo-100 text-brand-700 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-4 h-4 text-brand-600" />
            <span>AI-Driven Trust & Transparency</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
            Find Real Tech Jobs You Can{' '}
            <span className="bg-gradient-to-r from-brand-600 to-indigo-500 bg-clip-text text-transparent">
              Actually Trust
            </span>
          </h1>

          <p className="max-w-2xl mx-auto text-lg sm:text-xl text-slate-600">
            Stop wasting time on ghost jobs, fake listings, and upfront registration scams.
            JobGuard AI scores job risks with ML and matches opportunities directly to your resume.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            {user ? (
              <Link
                to="/dashboard"
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-base shadow-lg shadow-brand-600/25 transition-all flex items-center justify-center space-x-2"
              >
                <span>Go to Dashboard</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
            ) : (
              <>
                <Link
                  to="/register"
                  className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-base shadow-lg shadow-brand-600/25 transition-all flex items-center justify-center space-x-2"
                >
                  <span>Upload Resume & Start Free</span>
                  <ArrowRight className="w-5 h-5" />
                </Link>
                <Link
                  to="/verify-job"
                  className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-white hover:bg-slate-50 text-slate-700 font-semibold text-base border border-slate-200 shadow-sm transition-all flex items-center justify-center space-x-2"
                >
                  <span>Verify a Job URL</span>
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Feature Pillar Grid */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-5">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">Hybrid Fraud Detector</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Scans for upfront fee requests, suspicious recruiter domains, WhatsApp-only interviews, and unrealistic salary anomalies.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition">
            <div className="w-12 h-12 rounded-xl bg-indigo-50 text-brand-600 flex items-center justify-center mb-5">
              <FileText className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">Semantic Resume Matching</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Upload your PDF/DOCX resume to extract canonical skills, calculate deep semantic similarity, and highlight missing requirements.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition">
            <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-5">
              <Building2 className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">Company Domain Verification</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Cross-references job listings against official corporate domains and career sites to ensure you never apply to impersonators.
            </p>
          </div>
        </div>
      </section>

      {/* Transparent Risk vs Match Preview */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6">
        <div className="bg-gradient-to-br from-slate-900 to-indigo-950 rounded-3xl p-8 sm:p-12 text-white shadow-2xl">
          <div className="max-w-2xl space-y-4">
            <span className="text-xs font-bold tracking-widest uppercase text-indigo-400">
              Unique Core Philosophy
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold">
              We Never Hide Risk Behind High Match Scores
            </h2>
            <p className="text-slate-300 text-sm leading-relaxed">
              A candidate might have a 95% skill match with a listing, but if the recruiter asks for a refundable security deposit via UPI, the risk is 90/100. JobGuard AI displays safety and skill alignment side-by-side.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

