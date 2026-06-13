/**
 * JobCard Component
 * Displays a recommendation returned by the Flask backend.
 */

import { Building2, MapPin, Briefcase, BadgeDollarSign, Star, Sparkles } from 'lucide-react';

export default function JobCard({ job }) {
  const matchScore = typeof job.matchScore === 'number' ? job.matchScore : null;
  const skills = Array.isArray(job.skills) ? job.skills : [];

  return (
    <div className="bg-white dark:bg-slate-800 border-2 border-gray-100 dark:border-slate-700 rounded-2xl overflow-hidden shadow-md hover:shadow-xl hover:border-indigo-200 dark:hover:border-indigo-600 transition-all duration-300 hover:-translate-y-0.5 group" data-testid="job-card">
      <div className="p-5 sm:p-6 space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4 min-w-0 flex-1">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-indigo-500 via-blue-500 to-cyan-500 flex items-center justify-center flex-shrink-0 shadow-lg shadow-indigo-500/40 group-hover:shadow-indigo-500/60 transition-shadow">
              <Building2 className="w-7 h-7 text-white" />
            </div>
            <div className="min-w-0">
              <p className="text-[10px] uppercase tracking-[0.25em] text-indigo-600 dark:text-indigo-400 font-bold mb-1.5">
                💼 Job Match
              </p>
              <h3 className="font-bold text-gray-900 dark:text-white text-lg sm:text-xl line-clamp-2 leading-tight group-hover:text-indigo-600 dark:group-hover:text-indigo-300 transition-colors">
                {job.jobTitle}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 flex items-center gap-1.5 font-semibold">
                <Building2 className="w-4 h-4 flex-shrink-0" />
                {job.company}
              </p>
            </div>
          </div>

          {matchScore !== null && (
            <div className="flex-shrink-0">
              <div className="inline-flex flex-col items-center gap-1.5 px-4 py-2.5 rounded-xl bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/40 dark:to-orange-900/40 text-amber-700 dark:text-amber-200 border-2 border-amber-200 dark:border-amber-700 shadow-md">
                <Star className="w-5 h-5 fill-amber-500" />
                <span className="font-bold text-lg">{Math.round(matchScore * 100)}%</span>
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <InfoPill icon={<MapPin className="w-4 h-4" />} label="Location" value={job.location} />
          <InfoPill icon={<Briefcase className="w-4 h-4" />} label="Work type" value={job.workType} />
          <InfoPill icon={<BadgeDollarSign className="w-4 h-4" />} label="Salary" value={job.salaryRange} />
        </div>

        <div className="flex flex-wrap gap-2.5 pt-2">
          <span className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full text-xs font-bold bg-gradient-to-r from-slate-100 to-gray-100 dark:from-slate-700 dark:to-slate-600 text-slate-700 dark:text-slate-200 shadow-sm">
            <Sparkles className="w-4 h-4" />
            {job.experience}
          </span>
          {skills.slice(0, 3).map((skill) => (
            <span key={skill} className="px-3.5 py-2 rounded-full text-xs font-bold bg-gradient-to-r from-indigo-100 to-blue-100 dark:from-indigo-900/50 dark:to-blue-900/50 text-indigo-700 dark:text-indigo-200 border-1.5 border-indigo-200 dark:border-indigo-700 shadow-sm">
              {skill}
            </span>
          ))}
          {skills.length > 3 && (
            <span className="px-3.5 py-2 rounded-full text-xs font-bold text-gray-600 dark:text-gray-400">
              +{skills.length - 3} more
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

function InfoPill({ icon, label, value }) {
  return (
    <div className="rounded-xl bg-gradient-to-br from-gray-50 to-gray-100 dark:from-slate-700/60 dark:to-slate-800/60 border-2 border-gray-100 dark:border-slate-700 px-4 py-3 hover:border-indigo-200 dark:hover:border-indigo-600 transition-colors">
      <div className="flex items-center gap-2.5 text-[10px] text-gray-600 dark:text-gray-400 uppercase tracking-[0.2em] font-bold mb-1.5">
        {icon}
        <span>{label}</span>
      </div>
      <div className="text-sm font-bold text-gray-900 dark:text-white line-clamp-2">
        {value || 'Not specified'}
      </div>
    </div>
  );
}
