/**
 * ApplicationsPage
 * User's job applications dashboard
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Loader2, CheckCircle, Clock, XCircle, Calendar, Building } from 'lucide-react';
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
      color: 'bg-yellow-100 text-yellow-700',
      icon: Clock,
    },
    reviewed: {
      label: 'Reviewed',
      color: 'bg-blue-100 text-blue-700',
      icon: FileText,
    },
    interview: {
      label: 'Interview',
      color: 'bg-purple-100 text-purple-700',
      icon: Calendar,
    },
    accepted: {
      label: 'Accepted',
      color: 'bg-green-100 text-green-700',
      icon: CheckCircle,
    },
    rejected: {
      label: 'Rejected',
      color: 'bg-red-100 text-red-700',
      icon: XCircle,
    },
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-12">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-3xl font-bold mb-2">My Applications</h1>
          <p className="text-blue-100">Track your job applications</p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {applications.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-sm p-12 text-center">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No applications yet</h3>
            <p className="text-gray-500 mb-6">
              You haven't applied to any jobs yet. Start your job search!
            </p>
            <Link
              to="/"
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Find Jobs
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
              {Object.entries(statusConfig).map(([key, config]) => {
                const count = applications.filter(a => a.status === key).length;
                const Icon = config.icon;
                return (
                  <div key={key} className="bg-white rounded-xl p-4 shadow-sm">
                    <div className="flex items-center space-x-2">
                      <Icon className={`w-5 h-5 ${config.color.split(' ')[1]}`} />
                      <span className="text-sm text-gray-500">{config.label}</span>
                    </div>
                    <p className="text-2xl font-bold text-gray-900 mt-1">{count}</p>
                  </div>
                );
              })}
            </div>

            {/* Applications list */}
            {applications.map((application) => {
              const status = statusConfig[application.status] || statusConfig.pending;
              const StatusIcon = status.icon;

              return (
                <div key={application.id} className="bg-white rounded-xl shadow-sm p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <h3 className="font-semibold text-gray-900">
                          Job #{application.job_id}
                        </h3>
                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium flex items-center ${status.color}`}>
                          <StatusIcon className="w-3 h-3 mr-1" />
                          {status.label}
                        </span>
                      </div>

                      <div className="mt-2 text-sm text-gray-500">
                        <span className="flex items-center">
                          <Calendar className="w-4 h-4 mr-1" />
                          Applied on {new Date(application.created_at).toLocaleDateString()}
                        </span>
                      </div>

                      {application.cover_letter && (
                        <p className="mt-3 text-gray-600 text-sm">
                          {application.cover_letter}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
