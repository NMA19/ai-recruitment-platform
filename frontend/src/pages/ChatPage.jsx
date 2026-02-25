/**
 * ChatPage
 * Main page with the chat interface
 */

import ChatBox from '../components/ChatBox';
import { MessageSquare, Search, FileText, Sparkles, Zap, TrendingUp } from 'lucide-react';

export default function ChatPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800">
      {/* Decorative background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-200 dark:bg-purple-900/30 rounded-full mix-blend-multiply dark:mix-blend-normal filter blur-3xl opacity-30 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-200 dark:bg-blue-900/30 rounded-full mix-blend-multiply dark:mix-blend-normal filter blur-3xl opacity-30 animate-pulse"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 py-6">
        <div className="grid lg:grid-cols-3 gap-6 h-[calc(100vh-8rem)]">
          {/* Sidebar - Features */}
          <div className="hidden lg:block space-y-4">
            {/* Welcome Card */}
            <div className="bg-gradient-to-br from-blue-600 via-blue-700 to-purple-700 rounded-2xl p-6 text-white shadow-xl shadow-blue-500/20">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-12 h-12 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center">
                  <Zap className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="font-bold text-lg">Welcome to HireMe</h2>
                  <p className="text-blue-100 text-sm">Your AI career assistant</p>
                </div>
              </div>
              <p className="text-sm text-blue-100 leading-relaxed">
                I can help you find perfect job opportunities, apply with one message, and track your applications.
              </p>
            </div>

            {/* Features */}
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/50 dark:border-gray-700/50">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-purple-600 dark:text-purple-400" />
                What I Can Do
              </h3>
              
              <div className="space-y-3">
                <FeatureCard 
                  icon={<Search className="w-4 h-4" />}
                  title="Smart Search"
                  example="Find Python jobs in Algiers"
                  color="blue"
                />
                
                <FeatureCard 
                  icon={<FileText className="w-4 h-4" />}
                  title="Quick Apply"
                  example="Apply for job #5"
                  color="green"
                />
                
                <FeatureCard 
                  icon={<TrendingUp className="w-4 h-4" />}
                  title="Track Progress"
                  example="Show my applications"
                  color="purple"
                />
              </div>
            </div>

            {/* Pro Tips */}
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-5 shadow-lg border border-white/50 dark:border-gray-700/50">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3 text-sm">💡 Pro Tips</h3>
              <ul className="space-y-2 text-xs text-gray-600 dark:text-gray-300">
                <li className="flex items-start space-x-2">
                  <span className="text-blue-500 mt-0.5">•</span>
                  <span>Be specific about skills & location</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-green-500 mt-0.5">•</span>
                  <span>Mention contract type (internship, full-time)</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-purple-500 mt-0.5">•</span>
                  <span>Sign up to save your applications</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Main Chat Area */}
          <div className="lg:col-span-2">
            <ChatBox />
          </div>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, example, color }) {
  const colors = {
    blue: 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 border-blue-100 dark:border-blue-800',
    green: 'bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 border-green-100 dark:border-green-800',
    purple: 'bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 border-purple-100 dark:border-purple-800',
  };

  return (
    <div className={`p-3 rounded-xl border ${colors[color]} transition-all hover:scale-[1.02]`}>
      <div className="flex items-center space-x-2 mb-1">
        {icon}
        <span className="font-medium text-sm">{title}</span>
      </div>
      <code className="text-xs opacity-75 dark:opacity-60">"{example}"</code>
    </div>
  );
}
