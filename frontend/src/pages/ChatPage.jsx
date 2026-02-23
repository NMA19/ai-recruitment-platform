/**
 * ChatPage
 * Main page with the chat interface
 */

import ChatBox from '../components/ChatBox';
import { MessageSquare, Search, FileText, Sparkles } from 'lucide-react';

export default function ChatPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid lg:grid-cols-3 gap-6 h-[calc(100vh-8rem)]">
          {/* Sidebar - Features */}
          <div className="hidden lg:block space-y-4">
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-blue-600" />
                AI-Powered Features
              </h3>
              
              <div className="space-y-4">
                <FeatureCard 
                  icon={<Search className="w-5 h-5" />}
                  title="Smart Job Search"
                  description="Just describe what you're looking for in natural language"
                  example='"Find me Python internships in Algiers"'
                />
                
                <FeatureCard 
                  icon={<FileText className="w-5 h-5" />}
                  title="Quick Apply"
                  description="Apply to jobs directly through the chat"
                  example='"Apply for job #5"'
                />
                
                <FeatureCard 
                  icon={<MessageSquare className="w-5 h-5" />}
                  title="Track Applications"
                  description="Check the status of your applications"
                  example='"Show my applications"'
                />
              </div>
            </div>

            {/* Quick tips */}
            <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl p-6 text-white">
              <h3 className="font-semibold mb-3">💡 Pro Tips</h3>
              <ul className="space-y-2 text-sm text-blue-100">
                <li>• Be specific about your skills and location</li>
                <li>• Mention contract type (internship, full-time)</li>
                <li>• Ask for job details before applying</li>
                <li>• Create an account to track applications</li>
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

function FeatureCard({ icon, title, description, example }) {
  return (
    <div className="p-3 bg-gray-50 rounded-xl">
      <div className="flex items-center space-x-2 text-blue-600 mb-1">
        {icon}
        <span className="font-medium text-sm">{title}</span>
      </div>
      <p className="text-xs text-gray-500 mb-1">{description}</p>
      <code className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded">
        {example}
      </code>
    </div>
  );
}
