/**
 * JobsPage
 * Browse all available jobs
 */

import { useState, useEffect } from 'react';
import { Search, MapPin, Filter, Loader2, Briefcase, Sparkles } from 'lucide-react';
import { jobsAPI } from '../services/api';
import JobCard from '../components/JobCard';

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [location, setLocation] = useState('');
  const [contractType, setContractType] = useState('');

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async (params = {}) => {
    setLoading(true);
    try {
      const response = await jobsAPI.getAll(params);
      setJobs(response.data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    const params = {};
    if (search) params.search = search;
    if (location) params.location = location;
    if (contractType) params.contract_type = contractType;
    fetchJobs(params);
  };

  const contractTypes = [
    { value: '', label: 'All Types' },
    { value: 'internship', label: 'Internship' },
    { value: 'full_time', label: 'Full-time' },
    { value: 'part_time', label: 'Part-time' },
    { value: 'contract', label: 'Contract' },
    { value: 'freelance', label: 'Freelance' },
  ];

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
              <Briefcase className="w-6 h-6" />
            </div>
            <span className="text-blue-200 text-sm font-medium">Discover Opportunities</span>
          </div>
          <h1 className="text-4xl font-bold mb-3">Find Your Dream Job</h1>
          <p className="text-blue-100 text-lg">Browse through our curated list of amazing positions</p>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="relative max-w-7xl mx-auto px-4 -mt-8">
        <form onSubmit={handleSearch} className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-xl shadow-blue-500/10 p-6 border border-white/50 dark:border-gray-700/50">
          <div className="grid md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 w-5 h-5" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Job title or keyword"
                className="w-full pl-12 pr-4 py-3.5 bg-gray-50/50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white dark:focus:bg-gray-700 dark:text-white dark:placeholder-gray-400 transition-all"
              />
            </div>
            
            <div className="relative">
              <MapPin className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 w-5 h-5" />
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Location"
                className="w-full pl-12 pr-4 py-3.5 bg-gray-50/50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white dark:focus:bg-gray-700 dark:text-white dark:placeholder-gray-400 transition-all"
              />
            </div>

            <div className="relative">
              <Filter className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 w-5 h-5" />
              <select
                value={contractType}
                onChange={(e) => setContractType(e.target.value)}
                className="w-full pl-12 pr-4 py-3.5 bg-gray-50/50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white dark:focus:bg-gray-700 dark:text-white transition-all appearance-none cursor-pointer"
              >
                {contractTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3.5 rounded-xl hover:shadow-lg hover:shadow-blue-500/25 transition-all font-semibold flex items-center justify-center space-x-2"
            >
              <Sparkles className="w-5 h-5" />
              <span>Search Jobs</span>
            </button>
          </div>
        </form>
      </div>

      {/* Jobs List */}
      <div className="relative max-w-7xl mx-auto px-4 py-10">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="text-center">
              <Loader2 className="w-10 h-10 text-blue-600 dark:text-blue-400 animate-spin mx-auto" />
              <p className="text-gray-500 dark:text-gray-400 mt-3">Loading jobs...</p>
            </div>
          </div>
        ) : jobs.length === 0 ? (
          <div className="text-center py-16 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-2xl border border-white/50 dark:border-gray-700/50">
            <Briefcase className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400 text-lg">No jobs found. Try different search criteria.</p>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between mb-6">
              <p className="text-gray-600 dark:text-gray-400">
                <span className="font-semibold text-gray-900 dark:text-white">{jobs.length}</span> jobs found
              </p>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
              {jobs.map((job) => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
