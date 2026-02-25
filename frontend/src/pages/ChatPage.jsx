/**
 * ChatPage
 * Main page with the chat interface
 */

import ChatBox from '../components/ChatBox';
import { MessageSquare, Search, FileText, Sparkles, Zap, TrendingUp, HelpCircle } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export default function ChatPage() {
  const { t, language } = useLanguage();
  const isRTL = language === 'ar';

  return (
    <div className={`min-h-[calc(100vh-4rem)] bg-gradient-to-br from-slate-50 via-green-50 to-blue-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 ${isRTL ? 'rtl' : ''}`}>
      {/* Decorative background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-green-200 dark:bg-green-900/30 rounded-full mix-blend-multiply dark:mix-blend-normal filter blur-3xl opacity-30 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-200 dark:bg-blue-900/30 rounded-full mix-blend-multiply dark:mix-blend-normal filter blur-3xl opacity-30 animate-pulse"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 py-6">
        <div className="grid lg:grid-cols-3 gap-6 h-[calc(100vh-8rem)]">
          {/* Sidebar - Features */}
          <div className="hidden lg:block space-y-4">
            {/* Welcome Card */}
            <div className="bg-gradient-to-br from-green-600 via-green-700 to-blue-700 rounded-2xl p-6 text-white shadow-xl shadow-green-500/20">
              <div className={`flex items-center ${isRTL ? 'space-x-reverse' : ''} space-x-3 mb-4`}>
                <div className="w-12 h-12 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center">
                  <Zap className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="font-bold text-lg">{t('chat.welcome')}</h2>
                  <p className="text-green-100 text-sm">{t('chat.subtitle')}</p>
                </div>
              </div>
              <p className="text-sm text-green-100 leading-relaxed">
                {t('chat.description')}
              </p>
            </div>

            {/* Features */}
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/50 dark:border-gray-700/50">
              <h3 className={`font-semibold text-gray-900 dark:text-white mb-4 flex items-center ${isRTL ? 'space-x-reverse' : ''}`}>
                <Sparkles className={`w-5 h-5 ${isRTL ? 'ml-2' : 'mr-2'} text-green-600 dark:text-green-400`} />
                {t('chat.features')}
              </h3>
              
              <div className="space-y-3">
                <FeatureCard 
                  icon={<Search className="w-4 h-4" />}
                  title={t('chat.smartSearch')}
                  example={t('chat.searchExample')}
                  color="green"
                  isRTL={isRTL}
                />
                
                <FeatureCard 
                  icon={<FileText className="w-4 h-4" />}
                  title={t('chat.quickApply')}
                  example={t('chat.applyExample')}
                  color="blue"
                  isRTL={isRTL}
                />
                
                <FeatureCard 
                  icon={<TrendingUp className="w-4 h-4" />}
                  title={t('chat.trackProgress')}
                  example={t('chat.trackExample')}
                  color="purple"
                  isRTL={isRTL}
                />

                <FeatureCard 
                  icon={<HelpCircle className="w-4 h-4" />}
                  title={t('chat.anemFaq')}
                  example={t('chat.anemExample')}
                  color="orange"
                  isRTL={isRTL}
                />
              </div>
            </div>

            {/* Pro Tips */}
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-5 shadow-lg border border-white/50 dark:border-gray-700/50">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3 text-sm">💡 {t('chat.tips')}</h3>
              <ul className="space-y-2 text-xs text-gray-600 dark:text-gray-300">
                <li className={`flex items-start ${isRTL ? 'space-x-reverse' : ''} space-x-2`}>
                  <span className="text-green-500 mt-0.5">•</span>
                  <span>{t('chat.tip1')}</span>
                </li>
                <li className={`flex items-start ${isRTL ? 'space-x-reverse' : ''} space-x-2`}>
                  <span className="text-blue-500 mt-0.5">•</span>
                  <span>{t('chat.tip2')}</span>
                </li>
                <li className={`flex items-start ${isRTL ? 'space-x-reverse' : ''} space-x-2`}>
                  <span className="text-purple-500 mt-0.5">•</span>
                  <span>{t('chat.tip3')}</span>
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

function FeatureCard({ icon, title, example, color, isRTL }) {
  const colors = {
    green: 'bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 border-green-100 dark:border-green-800',
    blue: 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 border-blue-100 dark:border-blue-800',
    purple: 'bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 border-purple-100 dark:border-purple-800',
    orange: 'bg-orange-50 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 border-orange-100 dark:border-orange-800',
  };

  return (
    <div className={`p-3 rounded-xl border ${colors[color]} transition-all hover:scale-[1.02]`}>
      <div className={`flex items-center ${isRTL ? 'space-x-reverse' : ''} space-x-2 mb-1`}>
        {icon}
        <span className="font-medium text-sm">{title}</span>
      </div>
      <code className="text-xs opacity-75 dark:opacity-60">"{example}"</code>
    </div>
  );
}
