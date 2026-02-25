/**
 * JobCard Component
 * Displays a job listing in the chat
 */

import { MapPin, Building, Briefcase, Code, ChevronRight, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function JobCard({ job, onApply }) {
  const { isAuthenticated } = useAuth();

  const contractTypes = {
    internship: { label: 'Internship', color: 'bg-purple-50 text-purple-700 border-purple-200' },
    full_time: { label: 'Full-time', color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
    part_time: { label: 'Part-time', color: 'bg-amber-50 text-amber-700 border-amber-200' },
    contract: { label: 'Contract', color: 'bg-orange-50 text-orange-700 border-orange-200' },
    freelance: { label: 'Freelance', color: 'bg-blue-50 text-blue-700 border-blue-200' },
  };

  const contractInfo = contractTypes[job.contract_type] || contractTypes.full_time;

  return (
    <div className="bg-white/80 backdrop-blur-sm border border-white/50 rounded-2xl p-5 hover:shadow-xl hover:shadow-blue-500/10 transition-all group">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors text-lg">
            {job.title}
          </h3>
          <div className="flex items-center flex-wrap gap-3 mt-2 text-sm text-gray-500">
            <span className="flex items-center">
              <Building className="w-4 h-4 mr-1.5 text-gray-400" />
              {job.company}
            </span>
            <span className="flex items-center">
              <MapPin className="w-4 h-4 mr-1.5 text-gray-400" />
              {job.location}
            </span>
          </div>
        </div>
        
        <span className={`px-3 py-1.5 rounded-xl text-xs font-semibold border ${contractInfo.color}`}>
          {contractInfo.label}
        </span>
      </div>

      {/* Skills */}
      {job.skills && (
        <div className="flex items-start mt-4 text-sm text-gray-600">
          <Code className="w-4 h-4 mr-2 text-gray-400 mt-0.5 flex-shrink-0" />
          <div className="flex flex-wrap gap-1.5">
            {job.skills.split(',').slice(0, 4).map((skill, index) => (
              <span 
                key={index}
                className="px-2.5 py-1 bg-gradient-to-r from-gray-50 to-gray-100 border border-gray-200 rounded-lg text-xs font-medium"
              >
                {skill.trim()}
              </span>
            ))}
            {job.skills.split(',').length > 4 && (
              <span className="text-gray-400 text-xs py-1">
                +{job.skills.split(',').length - 4} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between mt-5 pt-4 border-t border-gray-100">
        <span className="text-xs text-gray-400">
          Job #{job.id}
        </span>

        {isAuthenticated ? (
          <button
            onClick={() => onApply?.(job.id)}
            className="flex items-center text-sm font-semibold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-all group/btn"
          >
            <Sparkles className="w-4 h-4 mr-1.5 text-blue-600" />
            Apply Now
            <ChevronRight className="w-4 h-4 ml-1 text-purple-600 group-hover/btn:translate-x-0.5 transition-transform" />
          </button>
        ) : (
          <span className="text-xs text-gray-400 italic">
            Login to apply
          </span>
        )}
      </div>
    </div>
  );
}
