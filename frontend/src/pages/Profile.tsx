import React, { useState, useEffect } from 'react';
import { User as UserIcon, Save, CheckCircle, AlertCircle, Briefcase, MapPin, DollarSign, Award } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { Profile as ProfileType } from '../types';

export const ProfilePage: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const [profile, setProfile] = useState<Partial<ProfileType>>({
    full_name: '',
    preferred_titles: '',
    preferred_locations: '',
    remote_preference: 'Any',
    expected_salary: 120000,
    experience_level: 'Mid-Level',
    key_skills: '',
    education: '',
  });

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get<ProfileType>('/profile');
        if (res.data) {
          setProfile(res.data);
        }
      } catch (err) {
        console.error('Failed to load profile:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setStatusMsg(null);
    try {
      await api.put('/profile', profile);
      await refreshUser();
      setStatusMsg({ type: 'success', text: 'Candidate profile updated successfully!' });
    } catch (err: any) {
      console.error(err);
      setStatusMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to update profile.' });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center text-slate-500">
        <div className="w-8 h-8 border-3 border-indigo-200 border-t-brand-600 rounded-full animate-spin mx-auto mb-3"></div>
        Loading profile details...
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 sm:p-8 space-y-6">
        <div className="flex items-center space-x-4 border-b border-slate-100 pb-6">
          <div className="w-14 h-14 rounded-2xl bg-indigo-50 text-brand-700 flex items-center justify-center font-bold text-xl border border-indigo-100 shadow-inner">
            {user?.name?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">{user?.name}</h1>
            <p className="text-sm text-slate-500">{user?.email}</p>
          </div>
        </div>

        {statusMsg && (
          <div
            className={`p-4 rounded-xl flex items-center space-x-3 text-sm ${
              statusMsg.type === 'success'
                ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}
          >
            {statusMsg.type === 'success' ? (
              <CheckCircle className="w-5 h-5 flex-shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
            )}
            <span>{statusMsg.text}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid sm:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
                Full Name
              </label>
              <input
                type="text"
                value={profile.full_name || ''}
                onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-600"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
                Experience Level
              </label>
              <select
                value={profile.experience_level || 'Mid-Level'}
                onChange={(e) => setProfile({ ...profile, experience_level: e.target.value as any })}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-600"
              >
                <option value="Entry">Entry (0-2 years)</option>
                <option value="Mid-Level">Mid-Level (2-5 years)</option>
                <option value="Senior">Senior (5-8 years)</option>
                <option value="Lead">Lead / Principal (8+ years)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
              Preferred Job Titles (comma-separated)
            </label>
            <input
              type="text"
              value={profile.preferred_titles || ''}
              onChange={(e) => setProfile({ ...profile, preferred_titles: e.target.value })}
              placeholder="e.g. Senior Python Developer, Backend Architect, ML Engineer"
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-600"
            />
          </div>

          <div className="grid sm:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
                Preferred Locations
              </label>
              <input
                type="text"
                value={profile.preferred_locations || ''}
                onChange={(e) => setProfile({ ...profile, preferred_locations: e.target.value })}
                placeholder="e.g. San Francisco, New York, Bangalore, Remote"
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-600"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
                Work Mode Preference
              </label>
              <select
                value={profile.remote_preference || 'Any'}
                onChange={(e) => setProfile({ ...profile, remote_preference: e.target.value as any })}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-600"
              >
                <option value="Remote">100% Remote</option>
                <option value="Hybrid">Hybrid</option>
                <option value="Onsite">Onsite</option>
                <option value="Any">Any Work Mode</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
              Key Technical Skills (comma-separated)
            </label>
            <input
              type="text"
              value={profile.key_skills || ''}
              onChange={(e) => setProfile({ ...profile, key_skills: e.target.value })}
              placeholder="e.g. Python, FastAPI, Docker, PostgreSQL, React, AWS"
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-600"
            />
          </div>

          <button
            type="submit"
            disabled={isSaving}
            className="px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-medium text-sm shadow-md shadow-brand-600/20 transition flex items-center space-x-2 disabled:opacity-60"
          >
            <Save className="w-4 h-4" />
            <span>{isSaving ? 'Saving Changes...' : 'Save Profile'}</span>
          </button>
        </form>
      </div>
    </div>
  );
};

