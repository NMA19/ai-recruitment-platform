/**
 * ChatPage
 * Main page with the chat interface
 */

import ChatBox from '../components/ChatBox';
import ErrorBoundary from '../components/ErrorBoundary';
import { Search, Sparkles, Zap, TrendingUp, HelpCircle } from 'lucide-react';

export default function ChatPage() {

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50 dark:from-gray-900 dark:via-gray-900 dark:to-slate-900">
      {/* Decorative background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-indigo-200 dark:bg-indigo-900/20 rounded-full mix-blend-multiply dark:mix-blend-normal filter blur-3xl opacity-20"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-200 dark:bg-blue-900/20 rounded-full mix-blend-multiply dark:mix-blend-normal filter blur-3xl opacity-20"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 py-6">
        <div className="grid lg:grid-cols-3 gap-6 h-[calc(100vh-8rem)]">
          {/* Sidebar - Features */}
          <div className="hidden lg:block space-y-4">
            {/* Welcome Card */}
            <div className="glass rounded-2xl p-6 shadow-xl shadow-indigo-500/20 border border-white/20 dark:border-white/10 bg-gradient-to-br from-indigo-600/10 via-blue-600/10 to-cyan-600/10 dark:from-indigo-900/30 dark:via-blue-900/30 dark:to-cyan-900/30">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/40">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="font-bold text-lg text-gray-900 dark:text-white">Welcome to Requ-AI</h2>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">Recommendation chat for Algerian jobs</p>
                </div>
              </div>
              <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                Ask for jobs by skill, location, salary, or work type. The backend returns matched recommendations directly.
              </p>
            </div>

            {/* Features */}
            <div className="glass rounded-2xl p-6 shadow-lg border border-white/20 dark:border-white/10">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-indigo-600 dark:text-indigo-400" />
                Features
              </h3>
              
              <div className="space-y-3">
                <FeatureCard 
                  icon={<Search className="w-4 h-4" />}
                  title="Smart recommendations"
                  example="find Python jobs in Algiers"
                  color="indigo"
                />
                
                <FeatureCard 
                  icon={<Sparkles className="w-4 h-4" />}
                  title="Match summary"
                  example="show top matches"
                  color="blue"
                />
                
                <FeatureCard 
                  icon={<TrendingUp className="w-4 h-4" />}
                  title="Salary + location filters"
                  example="remote frontend jobs with salary"
                  color="cyan"
                />

                <FeatureCard 
                  icon={<HelpCircle className="w-4 h-4" />}
                  title="Natural language"
                  example="I want a backend job near Oran"
                  color="emerald"
                />
              </div>
            </div>

            {/* Pro Tips */}
            <div className="glass rounded-2xl p-5 shadow-lg border border-white/20 dark:border-white/10">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3 text-sm">💡 Pro Tips</h3>
              <ul className="space-y-2 text-xs text-gray-600 dark:text-gray-400">
                <li className="flex items-start space-x-2">
                  <span className="text-indigo-500 mt-0.5 font-bold">•</span>
                  <span>Use Wilaya names or city names (e.g., Algiers, Oran)</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-blue-500 mt-0.5 font-bold">•</span>
                  <span>Mention skills to improve the matching score</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-cyan-500 mt-0.5 font-bold">•</span>
                  <span>Ask for salary or work type if you want narrower results</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Main Chat Area */}
          <div className="lg:col-span-2">
            <ErrorBoundary>
              <ChatBox />
            </ErrorBoundary>
          </div>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, example, color }) {
  const colors = {
    indigo: 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 border-indigo-100 dark:border-indigo-800/50',
    blue: 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 border-blue-100 dark:border-blue-800/50',
    cyan: 'bg-cyan-50 dark:bg-cyan-900/30 text-cyan-600 dark:text-cyan-400 border-cyan-100 dark:border-cyan-800/50',
    emerald: 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 border-emerald-100 dark:border-emerald-800/50',
  };

  return (
    <div className={`p-3 rounded-xl border ${colors[color]} transition-all hover:scale-[1.02] hover:shadow-md`}>
      <div className="flex items-center space-x-2 mb-1">
        {icon}
        <span className="font-semibold text-sm">{title}</span>
      </div>
      <code className="text-xs opacity-70 dark:opacity-60 font-mono">"{example}"</code>
    </div>
  );
}
