/**
 * ApplicationsPage
 * User's job applications dashboard
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Loader2, CheckCircle, Clock, XCircle, Calendar, Building, ClipboardList, Sparkles } from 'lucide-react';
import { applicationsAPI } from '../services/api';

export default function ApplicationsPage() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      const response = await applicationsAPI.getMyApplications();
      setApplications(response.data);
    } catch (error) {
      console.error('Error fetching applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const statusConfig = {
    pending: {
      label: 'Pending',
      color: 'bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800',
      icon: Clock,
      gradient: 'from-amber-400 to-orange-500',
    },
    reviewed: {
      label: 'Reviewed',
      color: 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800',
      icon: FileText,
      gradient: 'from-blue-400 to-blue-600',
    },
    interview: {
      label: 'Interview',
      color: 'bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800',
      icon: Calendar,
      gradient: 'from-purple-400 to-purple-600',
    },
    accepted: {
      label: 'Accepted',
      color: 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800',
      icon: CheckCircle,
      gradient: 'from-emerald-400 to-green-600',
    },
    rejected: {
      label: 'Rejected',
      color: 'bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-300 border-red-200 dark:border-red-800',
      icon: XCircle,
      gradient: 'from-red-400 to-red-600',
    },
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-10 h-10 text-blue-600 dark:text-blue-400 animate-spin mx-auto" />
          <p className="text-gray-500 dark:text-gray-400 mt-3">Loading your applications...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800">
      {/* Decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-40 left-10 w-72 h-72 bg-purple-200 dark:bg-purple-900/30 rounded-full mix-blend-multiply dark:mix-blend-normal filter blur-3xl opacity-20"></div>
        <div className="absolute top-60 right-10 w-72 h-72 bg-blue-200 dark:bg-blue-900/30 rounded-full mix-blend-multiply dark:mix-blend-normal filter blur-3xl opacity-20"></div>
      </div>

      {/* Header */}
      <div className="relative bg-gradient-to-r from-blue-600 via-blue-700 to-purple-700 text-white py-16">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0aDR2NEgzNnpNMzAgMzRoNHY0aC00ek0yNCAzNGg0djRoLTR6TTE4IDM0aDR2NGgtNHoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-30"></div>
        <div className="relative max-w-7xl mx-auto px-4">
          <div className="flex items-center space-x-3 mb-3">
            <div className="p-2 bg-white/10 rounded-xl backdrop-blur-sm">
              <ClipboardList className="w-6 h-6" />
            </div>
            <span className="text-blue-200 text-sm font-medium">Track Your Progress</span>
          </div>
          <h1 className="text-4xl font-bold mb-3">My Applications</h1>
          <p className="text-blue-100 text-lg">Stay updated on your job application status</p>
        </div>
      </div>

      {/* Content */}
      <div className="relative max-w-7xl mx-auto px-4 py-10 -mt-6">
        {applications.length === 0 ? (
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-3xl shadow-xl shadow-blue-500/10 p-12 text-center border border-white/50 dark:border-gray-700/50">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/50 dark:to-purple-900/50 rounded-2xl mb-4">
              <FileText className="w-8 h-8 text-blue-500 dark:text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No applications yet</h3>
            <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-md mx-auto">
              You haven't applied to any jobs yet. Explore our job listings and find your dream position!
            </p>
            <Link
              to="/"
              className="inline-flex items-center px-6 py-3.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:shadow-lg hover:shadow-blue-500/25 transition-all font-semibold space-x-2"
            >
              <Sparkles className="w-5 h-5" />
              <span>Find Jobs</span>
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {Object.entries(statusConfig).map(([key, config]) => {
                const count = applications.filter(a => a.status === key).length;
                const Icon = config.icon;
                return (
                  <div key={key} className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-5 shadow-lg shadow-blue-500/5 border border-white/50 dark:border-gray-700/50 hover:shadow-xl transition-shadow">
                    <div className="flex items-center space-x-2 mb-2">
                      <div className={`p-1.5 rounded-lg bg-gradient-to-br ${config.gradient}`}>
                        <Icon className="w-4 h-4 text-white" />
                      </div>
                      <span className="text-sm text-gray-500 dark:text-gray-400 font-medium">{config.label}</span>
                    </div>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">{count}</p>
                  </div>
                );
              })}
            </div>

            {/* Applications list */}
            <div className="space-y-4">
              {applications.map((application) => {
                const status = statusConfig[application.status] || statusConfig.pending;
                const StatusIcon = status.icon;

                return (
                  <div key={application.id} className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-lg shadow-blue-500/5 p-6 border border-white/50 dark:border-gray-700/50 hover:shadow-xl transition-all">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 flex-wrap gap-y-2">
                          <h3 className="font-semibold text-gray-900 dark:text-white text-lg">
                            Job #{application.job_id}
                          </h3>
                          <span className={`px-3 py-1.5 rounded-full text-xs font-semibold flex items-center border ${status.color}`}>
                            <StatusIcon className="w-3.5 h-3.5 mr-1.5" />
                            {status.label}
                          </span>
                        </div>

                        <div className="mt-3 text-sm text-gray-500 dark:text-gray-400">
                          <span className="flex items-center">
                            <Calendar className="w-4 h-4 mr-2 text-gray-400 dark:text-gray-500" />
                            Applied on {new Date(application.created_at).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric'
                            })}
                          </span>
                        </div>

                        {application.cover_letter && (
                          <p className="mt-4 text-gray-600 dark:text-gray-300 text-sm bg-gray-50/50 dark:bg-gray-700/50 p-4 rounded-xl border border-gray-100 dark:border-gray-600">
                            {application.cover_letter}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
