import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/layout/Navbar';
import { ProtectedRoute } from './components/layout/ProtectedRoute';

import { Landing } from './pages/Landing';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { ProfilePage } from './pages/Profile';
import { ResumePage } from './pages/Resume';
import { JobsPage } from './pages/Jobs';
import { JobDetailPage } from './pages/JobDetail';
import { VerifyJobPage } from './pages/VerifyJob';
import { SavedJobsPage } from './pages/SavedJobs';
import { ApplicationsPage } from './pages/Applications';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
          <Navbar />
          <main className="flex-1">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Protected Routes */}
              <Route element={<ProtectedRoute />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/jobs" element={<JobsPage />} />
                <Route path="/jobs/:id" element={<JobDetailPage />} />
                <Route path="/verify-job" element={<VerifyJobPage />} />
                <Route path="/resume" element={<ResumePage />} />
                <Route path="/saved" element={<SavedJobsPage />} />
                <Route path="/applications" element={<ApplicationsPage />} />
              </Route>

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
            <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-2">
              <span className="font-semibold text-slate-700">JobGuard AI © 2026</span>
              <span>Find Real Tech Jobs You Can Actually Trust</span>
              <span>Hybrid ML & Rule-Based Scam Detection</span>
            </div>
          </footer>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
