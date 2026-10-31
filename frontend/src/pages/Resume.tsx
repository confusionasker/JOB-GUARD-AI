import React, { useState, useEffect, useRef } from 'react';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  Award, 
  GraduationCap, 
  Briefcase, 
  TrendingUp,
  RefreshCw,
  Plus,
  X,
  PlusCircle,
  Building2,
  Calendar,
  Trash2,
  Award as ScoreIcon
} from 'lucide-react';
import api from '../services/api';
import { ParsedResume } from '../types';

interface ResumeAnalysis {
  extracted_skills: string[];
  total_experience_years: number;
  experience_level: string;
  top_matched_roles: string[];
  missing_in_demand_skills: string[];
  recommended_skills_to_learn: string[];
  certifications: string[];
}

export const ResumePage: React.FC = () => {
  const [currentResume, setCurrentResume] = useState<ParsedResume | null>(null);
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // New Skill input state
  const [newSkillInput, setNewSkillInput] = useState('');

  // New Target Role input state
  const [newRoleInput, setNewRoleInput] = useState('');

  // Add Education Form State
  const [showAddEduForm, setShowAddEduForm] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [eduDegree, setEduDegree] = useState('');
  const [eduInst, setEduInst] = useState('');
  const [eduYear, setEduYear] = useState('');
  const [eduScore, setEduScore] = useState('');

  const roleSuggestions = [
    'Machine Learning Engineer',
    'Python Developer',
    'Data Scientist',
    'AI Engineer',
    'Full Stack Developer',
    'Backend Engineer',
    'Software Engineer'
  ];

  const fetchData = async () => {
    try {
      setIsLoading(true);
      const res = await api.get<ParsedResume>('/resumes/current');
      setCurrentResume(res.data);
      const analysisRes = await api.get<ResumeAnalysis>('/resumes/analysis');
      setAnalysis(analysisRes.data);
    } catch (err: any) {
      if (err.response?.status !== 404) {
        console.error('Error fetching resume data:', err);
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const showNotification = (msg: string, isError = false) => {
    if (isError) {
      setErrorMsg(msg);
      setTimeout(() => setErrorMsg(''), 5000);
    } else {
      setSuccessMsg(msg);
      setTimeout(() => setSuccessMsg(''), 4000);
    }
  };

  const handleFileUpload = async (file: File) => {
    setErrorMsg('');
    setSuccessMsg('');

    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!['.pdf', '.docx', '.doc'].includes(ext)) {
      showNotification('Invalid file format. Please upload a .pdf or .docx document.', true);
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      showNotification('File size exceeds the 10MB limit.', true);
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    try {
      const res = await api.post<ParsedResume>('/resumes/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setCurrentResume(res.data);
      showNotification('Resume parsed and synchronized successfully!');
      const analysisRes = await api.get<ResumeAnalysis>('/resumes/analysis');
      setAnalysis(analysisRes.data);
    } catch (err: any) {
      console.error(err);
      showNotification(err.response?.data?.detail || 'Failed to upload and parse resume.', true);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  // --- Skill Management Handlers ---
  const handleAddSkill = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const skillToAdd = newSkillInput.trim();
    if (!skillToAdd || !currentResume) return;

    const currentSkills = currentResume.structured_data.skills || [];
    if (currentSkills.some(s => s.toLowerCase() === skillToAdd.toLowerCase())) {
      showNotification(`"${skillToAdd}" is already in your skills list.`, true);
      return;
    }

    const updatedSkills = [...currentSkills, skillToAdd];
    try {
      setIsUpdating(true);
      const res = await api.put<ParsedResume>('/resumes/current', { skills: updatedSkills });
      setCurrentResume(res.data);
      setNewSkillInput('');
      showNotification(`Added skill: ${skillToAdd}`);
      const analysisRes = await api.get<ResumeAnalysis>('/resumes/analysis');
      setAnalysis(analysisRes.data);
    } catch (err: any) {
      showNotification('Failed to update skills.', true);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleRemoveSkill = async (skillToRemove: string) => {
    if (!currentResume) return;
    const currentSkills = currentResume.structured_data.skills || [];
    const updatedSkills = currentSkills.filter(s => s !== skillToRemove);

    try {
      setIsUpdating(true);
      const res = await api.put<ParsedResume>('/resumes/current', { skills: updatedSkills });
      setCurrentResume(res.data);
      showNotification(`Removed skill: ${skillToRemove}`);
      const analysisRes = await api.get<ResumeAnalysis>('/resumes/analysis');
      setAnalysis(analysisRes.data);
    } catch (err: any) {
      showNotification('Failed to update skills.', true);
    } finally {
      setIsUpdating(false);
    }
  };

  // --- Target Job Role Management Handlers ---
  const handleAddRole = async (roleToAdd: string) => {
    const roleClean = roleToAdd.trim();
    if (!roleClean || !currentResume) return;

    const currentRoles = currentResume.structured_data.job_titles || [];
    if (currentRoles.some(r => r.toLowerCase() === roleClean.toLowerCase())) {
      showNotification(`"${roleClean}" is already in your target roles.`, true);
      return;
    }

    const updatedRoles = [...currentRoles, roleClean];
    try {
      setIsUpdating(true);
      const res = await api.put<ParsedResume>('/resumes/current', { target_job_roles: updatedRoles });
      setCurrentResume(res.data);
      setNewRoleInput('');
      showNotification(`Target job role added: ${roleClean}`);
      const analysisRes = await api.get<ResumeAnalysis>('/resumes/analysis');
      setAnalysis(analysisRes.data);
    } catch (err: any) {
      showNotification('Failed to update target roles.', true);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleRemoveRole = async (roleToRemove: string) => {
    if (!currentResume) return;
    const currentRoles = currentResume.structured_data.job_titles || [];
    const updatedRoles = currentRoles.filter(r => r !== roleToRemove);

    try {
      setIsUpdating(true);
      const res = await api.put<ParsedResume>('/resumes/current', { target_job_roles: updatedRoles });
      setCurrentResume(res.data);
      showNotification(`Removed target role: ${roleToRemove}`);
      const analysisRes = await api.get<ResumeAnalysis>('/resumes/analysis');
      setAnalysis(analysisRes.data);
    } catch (err: any) {
      showNotification('Failed to update target roles.', true);
    } finally {
      setIsUpdating(false);
    }
  };

  // --- Education Management Handlers ---
  const handleAddEducation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!eduDegree.trim() || !currentResume) return;

    const newEduItem = {
      degree: eduDegree.trim(),
      institution: eduInst.trim() || undefined,
      year: eduYear.trim() || undefined,
      score: eduScore.trim() || undefined
    };

    const currentEdu = currentResume.structured_data.education || [];
    const updatedEdu = [newEduItem, ...currentEdu];

    try {
      setIsUpdating(true);
      const res = await api.put<ParsedResume>('/resumes/current', { education: updatedEdu });
      setCurrentResume(res.data);
      setEduDegree('');
      setEduInst('');
      setEduYear('');
      setEduScore('');
      setShowAddEduForm(false);
      showNotification(`Education record added: ${newEduItem.degree}`);
    } catch (err) {
      showNotification('Failed to update education.', true);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleRemoveEducation = async (idxToRemove: number) => {
    if (!currentResume) return;
    const currentEdu = currentResume.structured_data.education || [];
    const updatedEdu = currentEdu.filter((_, idx) => idx !== idxToRemove);

    try {
      setIsUpdating(true);
      const res = await api.put<ParsedResume>('/resumes/current', { education: updatedEdu });
      setCurrentResume(res.data);
      showNotification('Education entry removed.');
    } catch (err) {
      showNotification('Failed to update education.', true);
    } finally {
      setIsUpdating(false);
    }
  };

  // --- Resume Deletion Handler ---
  const handleDeleteResume = async () => {
    try {
      setIsUpdating(true);
      await api.delete('/resumes/current');
      setCurrentResume(null);
      setAnalysis(null);
      setShowDeleteConfirm(false);
      showNotification('Resume deleted successfully. You can now upload a fresh resume.');
    } catch (err: any) {
      showNotification(err.response?.data?.detail || 'Failed to delete resume.', true);
    } finally {
      setIsUpdating(false);
    }
  };

  // --- Experience Years Adjustment Handler ---
  const handleUpdateExperience = async (years: number) => {
    if (!currentResume) return;
    try {
      setIsUpdating(true);
      const res = await api.put<ParsedResume>('/resumes/current', { total_experience_years: years });
      setCurrentResume(res.data);
      showNotification(`Experience set to ${years === 0 ? 'Fresher (0 years)' : `${years} years`}`);
      const analysisRes = await api.get<ResumeAnalysis>('/resumes/analysis');
      setAnalysis(analysisRes.data);
    } catch (err: any) {
      showNotification('Failed to update experience.', true);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-200 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Resume Intelligence & Customization</h1>
          <p className="text-sm text-slate-500 mt-1">
            Extract skills, add target job roles, customize education, and discover real-time job compatibility.
          </p>
        </div>
        {isUpdating && (
          <div className="text-xs font-semibold text-brand-600 bg-brand-50 px-3 py-1.5 rounded-full flex items-center space-x-2 border border-brand-200">
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            <span>Syncing Profile Changes...</span>
          </div>
        )}
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center space-x-3 animate-fadeIn">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm flex items-center space-x-3 animate-fadeIn">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Grid: Upload Dropzone & Extracted Insights */}
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left Column: Upload Dropzone */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-4">
            <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
              <UploadCloud className="w-5 h-5 text-brand-600" />
              <span>{currentResume ? 'Update Resume Document' : 'Upload Resume'}</span>
            </h2>

            <div
              onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
              onDragLeave={() => setDragActive(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition flex flex-col items-center justify-center space-y-3 ${
                dragActive
                  ? 'border-brand-500 bg-brand-50/50'
                  : 'border-slate-300 hover:border-brand-400 bg-slate-50/50'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.doc"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileUpload(e.target.files[0]);
                  }
                }}
              />

              <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-brand-600 flex items-center justify-center">
                {isUploading ? (
                  <RefreshCw className="w-6 h-6 animate-spin" />
                ) : (
                  <UploadCloud className="w-6 h-6" />
                )}
              </div>

              <div>
                <span className="text-sm font-semibold text-slate-900">
                  {isUploading ? 'Parsing Resume...' : 'Click or drag file here'}
                </span>
                <p className="text-xs text-slate-500 mt-1">Supports PDF and DOCX (up to 10MB)</p>
              </div>
            </div>

            {currentResume && (
              <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 text-xs text-slate-600 space-y-3">
                <div className="font-semibold text-slate-800 flex items-center justify-between">
                  <span className="truncate max-w-[190px]">{currentResume.file_name}</span>
                  <span className="uppercase text-[10px] bg-indigo-100 text-indigo-700 font-bold px-2 py-0.5 rounded">
                    {currentResume.file_type}
                  </span>
                </div>

                {/* Total Experience Display */}
                <div className="flex items-center justify-between pt-1 border-t border-slate-200/70">
                  <span className="text-slate-500 font-medium">Experience Level:</span>
                  {currentResume.total_experience_years === 0 ? (
                    <span className="font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded text-[11px] border border-emerald-300">
                      Fresher (0 years)
                    </span>
                  ) : (
                    <span className="font-bold text-slate-800 bg-slate-200 px-2 py-0.5 rounded text-[11px]">
                      {currentResume.total_experience_years} years
                    </span>
                  )}
                </div>

                {/* Quick Experience Selector */}
                <div className="space-y-1 pt-1">
                  <div className="text-[11px] text-slate-500">Adjust Experience:</div>
                  <div className="grid grid-cols-4 gap-1 text-[11px]">
                    {[0, 1, 2, 3].map((yr) => (
                      <button
                        key={yr}
                        type="button"
                        onClick={() => handleUpdateExperience(yr)}
                        className={`py-1 rounded text-center font-semibold transition border ${
                          currentResume.total_experience_years === yr
                            ? 'bg-brand-600 text-white border-brand-600'
                            : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                        }`}
                      >
                        {yr === 0 ? 'Fresher' : `${yr}y`}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Delete Resume Action */}
                {showDeleteConfirm ? (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-xl space-y-2 mt-2 animate-fadeIn">
                    <p className="text-xs text-red-800 font-semibold">Delete this resume permanently?</p>
                    <p className="text-[11px] text-red-600 leading-tight">
                      This will remove all parsed skills, education, and target roles.
                    </p>
                    <div className="flex gap-2 pt-1">
                      <button
                        type="button"
                        onClick={handleDeleteResume}
                        disabled={isUpdating}
                        className="flex-1 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-lg text-xs font-semibold transition disabled:opacity-50"
                      >
                        Yes, Delete
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowDeleteConfirm(false)}
                        className="px-3 py-1.5 bg-white border border-slate-200 text-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-50 transition"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => setShowDeleteConfirm(true)}
                    className="w-full mt-2 py-2 px-3 rounded-xl border border-red-200 bg-red-50 hover:bg-red-100 text-red-700 font-semibold text-xs flex items-center justify-center space-x-1.5 transition"
                  >
                    <Trash2 className="w-3.5 h-3.5 text-red-600" />
                    <span>Delete Resume</span>
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Skills, Target Roles, Education & Recommendations */}
        <div className="lg:col-span-2 space-y-6">
          {isLoading ? (
            <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-500">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-brand-600" />
              Loading resume insights...
            </div>
          ) : !currentResume ? (
            <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
              <FileText className="w-12 h-12 text-slate-300 mx-auto" />
              <h3 className="text-lg font-bold text-slate-900">No Resume Uploaded</h3>
              <p className="text-sm text-slate-500 max-w-md mx-auto">
                Upload your resume on the left to extract skills, detect education, customize target roles, and start live job matching.
              </p>
            </div>
          ) : (
            <>
              {/* 1. Extracted Skills Card (with Add & Delete) */}
              <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-4">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                  <div className="flex items-center space-x-2">
                    <Sparkles className="w-5 h-5 text-brand-600" />
                    <h2 className="text-lg font-bold text-slate-900">Skills ({currentResume.structured_data.skills.length})</h2>
                  </div>
                  <span className="text-xs text-slate-500">Click &times; to remove or add missing skills below</span>
                </div>

                {/* Skills tags list */}
                <div className="flex flex-wrap gap-2 pt-1">
                  {currentResume.structured_data.skills.map((skill) => (
                    <span
                      key={skill}
                      className="group inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-50 border border-indigo-100 text-brand-700 font-medium text-xs shadow-sm transition hover:bg-indigo-100"
                    >
                      <span>{skill}</span>
                      <button
                        onClick={() => handleRemoveSkill(skill)}
                        className="text-indigo-400 hover:text-red-600 font-bold ml-1 rounded p-0.5 hover:bg-white/80 transition"
                        title={`Remove ${skill}`}
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>

                {/* Add Custom Skill Form */}
                <form onSubmit={handleAddSkill} className="flex gap-2 pt-2 border-t border-slate-100">
                  <input
                    type="text"
                    value={newSkillInput}
                    onChange={(e) => setNewSkillInput(e.target.value)}
                    placeholder="Add a new skill (e.g. FastAPI, Docker, TypeScript)..."
                    className="flex-1 px-3 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-brand-500"
                  />
                  <button
                    type="submit"
                    disabled={!newSkillInput.trim() || isUpdating}
                    className="px-4 py-1.5 bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs rounded-lg transition disabled:opacity-40 flex items-center space-x-1"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Add Skill</span>
                  </button>
                </form>
              </div>

              {/* 2. Target Job Roles Card (Customizable) */}
              <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-slate-900 font-bold text-base">
                    <Briefcase className="w-5 h-5 text-brand-600" />
                    <h2>Target Job Roles ({currentResume.structured_data.job_titles?.length || 0})</h2>
                  </div>
                  <span className="text-xs text-slate-500">Defines your job recommendations</span>
                </div>

                {/* Active Target Job Badges */}
                <div className="flex flex-wrap gap-2">
                  {(currentResume.structured_data.job_titles?.length ? currentResume.structured_data.job_titles : ['Machine Learning Engineer']).map((role) => (
                    <span
                      key={role}
                      className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 font-medium text-xs shadow-sm"
                    >
                      <span>{role}</span>
                      <button
                        onClick={() => handleRemoveRole(role)}
                        className="text-emerald-500 hover:text-red-600 font-bold ml-1 rounded p-0.5 hover:bg-white/80 transition"
                        title={`Remove ${role}`}
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>

                {/* Add Target Role input & Quick Suggestions */}
                <div className="space-y-2 pt-2 border-t border-slate-100">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newRoleInput}
                      onChange={(e) => setNewRoleInput(e.target.value)}
                      placeholder="Add custom target role (e.g. AI Engineer, Python Developer)..."
                      className="flex-1 px-3 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-brand-500"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          handleAddRole(newRoleInput);
                        }
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => handleAddRole(newRoleInput)}
                      disabled={!newRoleInput.trim() || isUpdating}
                      className="px-4 py-1.5 bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs rounded-lg transition disabled:opacity-40 flex items-center space-x-1"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>Add Role</span>
                    </button>
                  </div>

                  {/* Quick role suggestions */}
                  <div className="flex flex-wrap items-center gap-1.5 pt-1 text-[11px] text-slate-500">
                    <span className="font-semibold text-slate-600">Quick Suggestions:</span>
                    {roleSuggestions
                      .filter(s => !(currentResume.structured_data.job_titles || []).includes(s))
                      .slice(0, 4)
                      .map((s) => (
                        <button
                          key={s}
                          type="button"
                          onClick={() => handleAddRole(s)}
                          className="px-2 py-0.5 bg-slate-100 hover:bg-indigo-50 hover:text-brand-700 rounded-md transition text-slate-700 border border-slate-200"
                        >
                          + {s}
                        </button>
                      ))}
                  </div>
                </div>
              </div>

              {/* 3. Education & Certifications Card */}
              <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-slate-900 font-bold text-base">
                    <GraduationCap className="w-5 h-5 text-brand-600" />
                    <h2>Education & Qualifications ({currentResume.structured_data.education?.length || 0})</h2>
                  </div>
                  <button
                    type="button"
                    onClick={() => setShowAddEduForm(!showAddEduForm)}
                    className="text-xs text-brand-600 hover:text-brand-700 font-semibold flex items-center space-x-1"
                  >
                    <PlusCircle className="w-3.5 h-3.5" />
                    <span>{showAddEduForm ? 'Cancel' : '+ Add Education'}</span>
                  </button>
                </div>

                {/* Add Education Inline Form */}
                {showAddEduForm && (
                  <form onSubmit={handleAddEducation} className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3 text-xs animate-fadeIn">
                    <div className="font-bold text-slate-800">Add Academic Degree / Certification:</div>
                    <div className="grid sm:grid-cols-2 gap-3">
                      <div>
                        <label className="text-slate-600 block mb-1">Degree / Qualification *</label>
                        <input
                          type="text"
                          required
                          value={eduDegree}
                          onChange={(e) => setEduDegree(e.target.value)}
                          placeholder="e.g. M.Sc Computer Science"
                          className="w-full px-3 py-1.5 rounded-lg border border-slate-200 bg-white"
                        />
                      </div>
                      <div>
                        <label className="text-slate-600 block mb-1">Institution / University</label>
                        <input
                          type="text"
                          value={eduInst}
                          onChange={(e) => setEduInst(e.target.value)}
                          placeholder="e.g. Vidyasagar University"
                          className="w-full px-3 py-1.5 rounded-lg border border-slate-200 bg-white"
                        />
                      </div>
                      <div>
                        <label className="text-slate-600 block mb-1">Year of Passing</label>
                        <input
                          type="text"
                          value={eduYear}
                          onChange={(e) => setEduYear(e.target.value)}
                          placeholder="e.g. 2025"
                          className="w-full px-3 py-1.5 rounded-lg border border-slate-200 bg-white"
                        />
                      </div>
                      <div>
                        <label className="text-slate-600 block mb-1">Marks / CGPA / %</label>
                        <input
                          type="text"
                          value={eduScore}
                          onChange={(e) => setEduScore(e.target.value)}
                          placeholder="e.g. 8.87 CGPA or 85%"
                          className="w-full px-3 py-1.5 rounded-lg border border-slate-200 bg-white"
                        />
                      </div>
                    </div>
                    <div className="flex justify-end pt-2">
                      <button
                        type="submit"
                        disabled={!eduDegree.trim() || isUpdating}
                        className="px-4 py-1.5 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-lg transition"
                      >
                        Save Degree
                      </button>
                    </div>
                  </form>
                )}

                {/* Education List */}
                <div className="space-y-3">
                  {currentResume.structured_data.education?.length ? (
                    currentResume.structured_data.education.map((edu, idx) => (
                      <div
                        key={idx}
                        className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-slate-900 text-sm">{edu.degree || 'Degree'}</span>
                            {edu.score && (
                              <span className="bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded text-[10px]">
                                {edu.score}
                              </span>
                            )}
                          </div>
                          {edu.institution && (
                            <div className="text-slate-600 flex items-center space-x-1.5">
                              <Building2 className="w-3.5 h-3.5 text-slate-400" />
                              <span>{edu.institution}</span>
                            </div>
                          )}
                        </div>

                        <div className="flex items-center space-x-3 self-end sm:self-center">
                          {edu.year && (
                            <span className="text-slate-500 font-medium flex items-center space-x-1 bg-white px-2 py-1 rounded border border-slate-200">
                              <Calendar className="w-3 h-3 text-slate-400" />
                              <span>{edu.year}</span>
                            </span>
                          )}
                          <button
                            onClick={() => handleRemoveEducation(idx)}
                            className="text-slate-400 hover:text-red-600 transition"
                            title="Remove degree"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-slate-400 italic p-3 text-center bg-slate-50 rounded-xl">
                      No degree records added. Use '+ Add Education' to specify your qualifications.
                    </div>
                  )}

                  {currentResume.structured_data.certifications?.map((cert, idx) => (
                    <div key={idx} className="text-xs text-emerald-800 bg-emerald-50 p-2.5 rounded-xl flex items-center space-x-2 border border-emerald-100">
                      <Award className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                      <span className="font-medium">{cert}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* 4. Recommended Skills to Learn */}
              {analysis && (
                <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-4">
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="w-5 h-5 text-emerald-600" />
                    <h2 className="text-base font-bold text-slate-900">Recommended Skills to Boost Your Match</h2>
                  </div>
                  <p className="text-xs text-slate-500">
                    High-demand industry tech stacks that complement your {currentResume.structured_data.skills.length} skills:
                  </p>

                  <div className="grid sm:grid-cols-2 gap-3 pt-1">
                    {analysis.recommended_skills_to_learn.map((recSkill) => (
                      <div
                        key={recSkill}
                        className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 flex items-center justify-between text-xs"
                      >
                        <span className="font-semibold text-slate-800">{recSkill}</span>
                        <button
                          onClick={() => {
                            setNewSkillInput(recSkill);
                            handleAddSkill();
                          }}
                          className="text-[11px] text-brand-600 bg-brand-50 hover:bg-brand-100 px-2 py-0.5 rounded font-medium transition"
                          title={`Add ${recSkill} to your skills`}
                        >
                          + Add to Resume
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
