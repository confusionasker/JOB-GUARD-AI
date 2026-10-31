import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { ShieldCheck, User as UserIcon, LogOut, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Find Jobs', path: '/jobs' },
    { name: 'Verify Job', path: '/verify-job' },
    { name: 'My Resume', path: '/resume' },
    { name: 'Saved', path: '/saved' },
    { name: 'Applications', path: '/applications' },
  ];

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Logo & Tagline */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-700 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-indigo-100 group-hover:scale-105 transition-transform">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xl font-bold bg-gradient-to-r from-slate-900 to-brand-700 bg-clip-text text-transparent">
                JobGuard AI
              </span>
              <span className="hidden sm:block text-[11px] font-medium text-slate-500 tracking-wide">
                Real Jobs You Can Actually Trust
              </span>
            </div>
          </Link>

          {/* Navigation Links for Authenticated Users */}
          {user && (
            <nav className="hidden md:flex space-x-1">
              {navLinks.map((link) => {
                const isActive = location.pathname === link.path;
                return (
                  <Link
                    key={link.path}
                    to={link.path}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-indigo-50 text-brand-700 font-semibold'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                    }`}
                  >
                    {link.name}
                  </Link>
                );
              })}
            </nav>
          )}

          {/* User Profile / Auth buttons */}
          <div className="flex items-center space-x-3">
            {user ? (
              <div className="flex items-center space-x-3">
                <Link
                  to="/profile"
                  className="flex items-center space-x-2 text-sm text-slate-700 hover:text-brand-700 py-1.5 px-3 rounded-lg hover:bg-slate-50 border border-transparent hover:border-slate-200 transition-all"
                >
                  <div className="w-8 h-8 rounded-full bg-indigo-100 text-brand-700 flex items-center justify-center font-semibold text-xs">
                    {user.name.charAt(0).toUpperCase()}
                  </div>
                  <span className="hidden sm:inline font-medium">{user.name}</span>
                </Link>
                <button
                  onClick={handleLogout}
                  title="Log out"
                  className="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link
                  to="/login"
                  className="text-sm font-medium text-slate-700 hover:text-brand-600 px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="text-sm font-medium text-white bg-brand-600 hover:bg-brand-700 px-4 py-2 rounded-lg shadow-sm transition-colors"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

