/**
 * Navbar Component
 * Main navigation bar
 */

import { Link, useNavigate } from 'react-router-dom';
import { LogOut, User, Menu, X, Briefcase, MessageSquare } from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
    setMobileMenuOpen(false);
  };

  return (
    <nav className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2 group">
              <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25 group-hover:shadow-blue-500/40 transition-shadow">
                <Briefcase className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                HireMe
              </span>
            </Link>
          </div>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center space-x-1">
            <Link 
              to="/" 
              className="px-4 py-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all flex items-center space-x-2"
            >
              <MessageSquare className="w-4 h-4" />
              <span>Chat</span>
            </Link>
            <Link 
              to="/jobs" 
              className="px-4 py-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all flex items-center space-x-2"
            >
              <Briefcase className="w-4 h-4" />
              <span>Jobs</span>
            </Link>

            {isAuthenticated ? (
              <div className="flex items-center space-x-2 ml-4">
                <Link 
                  to="/applications" 
                  className="px-4 py-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
                >
                  My Applications
                </Link>
                <div className="flex items-center space-x-2 px-3 py-1.5 bg-gray-100 rounded-full">
                  <div className="w-7 h-7 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-sm font-medium text-gray-700">{user?.name}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 px-3 py-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2 ml-4">
                <Link 
                  to="/login" 
                  className="px-4 py-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
                >
                  Login
                </Link>
                <Link 
                  to="/register" 
                  className="px-5 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg hover:shadow-blue-500/25 transition-all font-medium"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-gray-600 hover:text-gray-900"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 space-y-2">
            <Link 
              to="/" 
              onClick={() => setMobileMenuOpen(false)}
              className="block px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
            >
              Chat
            </Link>
            <Link 
              to="/jobs" 
              onClick={() => setMobileMenuOpen(false)}
              className="block px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
            >
              Jobs
            </Link>
            {isAuthenticated ? (
              <>
                <Link 
                  to="/applications" 
                  onClick={() => setMobileMenuOpen(false)}
                  className="block px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  My Applications
                </Link>
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link 
                  to="/login" 
                  onClick={() => setMobileMenuOpen(false)}
                  className="block px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  Login
                </Link>
                <Link 
                  to="/register" 
                  onClick={() => setMobileMenuOpen(false)}
                  className="block px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
