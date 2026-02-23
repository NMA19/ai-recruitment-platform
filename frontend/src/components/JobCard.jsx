/**
 * JobCard Component
 * Displays a job listing in the chat
 */

import { MapPin, Building, Briefcase, Code, ChevronRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function JobCard({ job, onApply }) {
  const { isAuthenticated } = useAuth();

  const contractTypes = {
    internship: { label: 'Internship', color: 'bg-purple-100 text-purple-700' },
    full_time: { label: 'Full-time', color: 'bg-green-100 text-green-700' },
    part_time: { label: 'Part-time', color: 'bg-yellow-100 text-yellow-700' },
    contract: { label: 'Contract', color: 'bg-orange-100 text-orange-700' },
    freelance: { label: 'Freelance', color: 'bg-blue-100 text-blue-700' },
  };

  const contractInfo = contractTypes[job.contract_type] || contractTypes.full_time;

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 hover:text-blue-600 cursor-pointer">
            {job.title}
          </h3>
          <div className="flex items-center space-x-3 mt-1 text-sm text-gray-500">
            <span className="flex items-center">
              <Building className="w-4 h-4 mr-1" />
              {job.company}
            </span>
            <span className="flex items-center">
              <MapPin className="w-4 h-4 mr-1" />
              {job.location}
            </span>
          </div>
        </div>
        
        <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${contractInfo.color}`}>
          {contractInfo.label}
        </span>
      </div>

      {/* Skills */}
      {job.skills && (
        <div className="flex items-center mt-3 text-sm text-gray-600">
          <Code className="w-4 h-4 mr-2 text-gray-400" />
          <div className="flex flex-wrap gap-1.5">
            {job.skills.split(',').slice(0, 4).map((skill, index) => (
              <span 
                key={index}
                className="px-2 py-0.5 bg-gray-100 rounded-md text-xs"
              >
                {skill.trim()}
              </span>
            ))}
            {job.skills.split(',').length > 4 && (
              <span className="text-gray-400 text-xs">
                +{job.skills.split(',').length - 4} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
        <span className="text-xs text-gray-400">
          Job #{job.id}
        </span>

        {isAuthenticated ? (
          <button
            onClick={() => onApply?.(job.id)}
            className="flex items-center text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            Apply Now
            <ChevronRight className="w-4 h-4 ml-1" />
          </button>
        ) : (
          <span className="text-xs text-gray-400">
            Login to apply
          </span>
        )}
      </div>
    </div>
  );
}
