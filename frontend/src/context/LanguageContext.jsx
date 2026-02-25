/**
 * Language Context
 * Manages French/Arabic/English translations
 */

import { createContext, useContext, useState, useEffect } from 'react';

const LanguageContext = createContext(null);

// All 58 Algerian Wilayas
export const WILAYAS = [
  { code: '01', name: 'Adrar', nameAr: 'أدرار' },
  { code: '02', name: 'Chlef', nameAr: 'الشلف' },
  { code: '03', name: 'Laghouat', nameAr: 'الأغواط' },
  { code: '04', name: 'Oum El Bouaghi', nameAr: 'أم البواقي' },
  { code: '05', name: 'Batna', nameAr: 'باتنة' },
  { code: '06', name: 'Béjaïa', nameAr: 'بجاية' },
  { code: '07', name: 'Biskra', nameAr: 'بسكرة' },
  { code: '08', name: 'Béchar', nameAr: 'بشار' },
  { code: '09', name: 'Blida', nameAr: 'البليدة' },
  { code: '10', name: 'Bouira', nameAr: 'البويرة' },
  { code: '11', name: 'Tamanrasset', nameAr: 'تمنراست' },
  { code: '12', name: 'Tébessa', nameAr: 'تبسة' },
  { code: '13', name: 'Tlemcen', nameAr: 'تلمسان' },
  { code: '14', name: 'Tiaret', nameAr: 'تيارت' },
  { code: '15', name: 'Tizi Ouzou', nameAr: 'تيزي وزو' },
  { code: '16', name: 'Alger', nameAr: 'الجزائر' },
  { code: '17', name: 'Djelfa', nameAr: 'الجلفة' },
  { code: '18', name: 'Jijel', nameAr: 'جيجل' },
  { code: '19', name: 'Sétif', nameAr: 'سطيف' },
  { code: '20', name: 'Saïda', nameAr: 'سعيدة' },
  { code: '21', name: 'Skikda', nameAr: 'سكيكدة' },
  { code: '22', name: 'Sidi Bel Abbès', nameAr: 'سيدي بلعباس' },
  { code: '23', name: 'Annaba', nameAr: 'عنابة' },
  { code: '24', name: 'Guelma', nameAr: 'قالمة' },
  { code: '25', name: 'Constantine', nameAr: 'قسنطينة' },
  { code: '26', name: 'Médéa', nameAr: 'المدية' },
  { code: '27', name: 'Mostaganem', nameAr: 'مستغانم' },
  { code: '28', name: "M'Sila", nameAr: 'المسيلة' },
  { code: '29', name: 'Mascara', nameAr: 'معسكر' },
  { code: '30', name: 'Ouargla', nameAr: 'ورقلة' },
  { code: '31', name: 'Oran', nameAr: 'وهران' },
  { code: '32', name: 'El Bayadh', nameAr: 'البيض' },
  { code: '33', name: 'Illizi', nameAr: 'إليزي' },
  { code: '34', name: 'Bordj Bou Arréridj', nameAr: 'برج بوعريريج' },
  { code: '35', name: 'Boumerdès', nameAr: 'بومرداس' },
  { code: '36', name: 'El Tarf', nameAr: 'الطارف' },
  { code: '37', name: 'Tindouf', nameAr: 'تندوف' },
  { code: '38', name: 'Tissemsilt', nameAr: 'تيسمسيلت' },
  { code: '39', name: 'El Oued', nameAr: 'الوادي' },
  { code: '40', name: 'Khenchela', nameAr: 'خنشلة' },
  { code: '41', name: 'Souk Ahras', nameAr: 'سوق أهراس' },
  { code: '42', name: 'Tipaza', nameAr: 'تيبازة' },
  { code: '43', name: 'Mila', nameAr: 'ميلة' },
  { code: '44', name: 'Aïn Defla', nameAr: 'عين الدفلى' },
  { code: '45', name: 'Naâma', nameAr: 'النعامة' },
  { code: '46', name: 'Aïn Témouchent', nameAr: 'عين تموشنت' },
  { code: '47', name: 'Ghardaïa', nameAr: 'غرداية' },
  { code: '48', name: 'Relizane', nameAr: 'غليزان' },
  { code: '49', name: 'El M\'Ghair', nameAr: 'المغير' },
  { code: '50', name: 'El Meniaa', nameAr: 'المنيعة' },
  { code: '51', name: 'Ouled Djellal', nameAr: 'أولاد جلال' },
  { code: '52', name: 'Bordj Badji Mokhtar', nameAr: 'برج باجي مختار' },
  { code: '53', name: 'Béni Abbès', nameAr: 'بني عباس' },
  { code: '54', name: 'Timimoun', nameAr: 'تيميمون' },
  { code: '55', name: 'Touggourt', nameAr: 'تقرت' },
  { code: '56', name: 'Djanet', nameAr: 'جانت' },
  { code: '57', name: 'In Salah', nameAr: 'عين صالح' },
  { code: '58', name: 'In Guezzam', nameAr: 'عين قزام' },
];

// Job sectors/domains
export const SECTORS = {
  en: [
    'Information Technology',
    'Healthcare',
    'Education',
    'Construction',
    'Finance & Banking',
    'Telecommunications',
    'Agriculture',
    'Energy & Oil',
    'Manufacturing',
    'Commerce & Sales',
    'Tourism & Hotels',
    'Transport & Logistics',
    'Administration',
    'Engineering',
    'Media & Communication',
  ],
  fr: [
    'Informatique',
    'Santé',
    'Éducation',
    'Construction',
    'Finance & Banque',
    'Télécommunications',
    'Agriculture',
    'Énergie & Pétrole',
    'Industrie',
    'Commerce & Vente',
    'Tourisme & Hôtellerie',
    'Transport & Logistique',
    'Administration',
    'Ingénierie',
    'Média & Communication',
  ],
  ar: [
    'تكنولوجيا المعلومات',
    'الصحة',
    'التعليم',
    'البناء',
    'المالية والبنوك',
    'الاتصالات',
    'الفلاحة',
    'الطاقة والنفط',
    'الصناعة',
    'التجارة والمبيعات',
    'السياحة والفندقة',
    'النقل واللوجستيك',
    'الإدارة',
    'الهندسة',
    'الإعلام والتواصل',
  ],
};

const translations = {
  en: {
    // Navigation
    nav: {
      chat: 'Chat',
      jobs: 'Jobs',
      applications: 'My Applications',
      login: 'Login',
      register: 'Sign Up',
      logout: 'Logout',
    },
    
    // Chat Page
    chat: {
      welcome: 'Welcome to Wassit Online',
      subtitle: 'Your ANEM career assistant',
      description: 'I can help you find job opportunities, apply with one message, track your applications, and answer your questions about ANEM services.',
      features: 'What I Can Do',
      smartSearch: 'Smart Search',
      searchExample: 'Find jobs in Alger',
      quickApply: 'Quick Apply',
      applyExample: 'Apply for job #5',
      trackProgress: 'Track Progress',
      trackExample: 'Show my applications',
      anemFaq: 'ANEM FAQ',
      anemExample: 'How to renew inscription?',
      tips: 'Pro Tips',
      tip1: 'Specify your Wilaya for local jobs',
      tip2: 'Ask about DAIP, CTA, CFI programs',
      tip3: 'Sign up to save your applications',
      placeholder: "Type your message... (e.g., 'Jobs in Oran' or 'Comment renouveler mon inscription?')",
      aiThinking: 'AI is thinking...',
    },
    // Jobs Page
    jobs: {
      title: 'Find Your Dream Job',
      subtitle: 'Browse through our curated list of amazing positions',
      searchPlaceholder: 'Job title or keyword',
      location: 'Location',
      allTypes: 'All Types',
      internship: 'Internship',
      fullTime: 'Full-time',
      partTime: 'Part-time',
      contract: 'Contract',
      freelance: 'Freelance',
      search: 'Search Jobs',
      loading: 'Loading jobs...',
      noResults: 'No jobs found. Try different search criteria.',
      found: 'jobs found',
      applyNow: 'Apply Now',
      loginToApply: 'Login to apply',
      salary: 'Salary',
      skills: 'Skills',
    },
    
    // Applications Page
    applications: {
      title: 'My Applications',
      subtitle: 'Track Your Progress',
      description: 'Stay updated on your job application status',
      noApplications: 'No applications yet',
      noApplicationsDesc: "You haven't applied to any jobs yet. Explore our job listings!",
      findJobs: 'Find Jobs',
      pending: 'Pending',
      reviewed: 'Reviewed',
      interview: 'Interview',
      accepted: 'Accepted',
      rejected: 'Rejected',
      appliedOn: 'Applied on',
    },
    
    // Login Page
    login: {
      title: 'Welcome Back',
      subtitle: 'Sign in to continue to Wassit Online',
      email: 'Email Address',
      password: 'Password',
      submit: 'Sign In',
      submitting: 'Signing in...',
      noAccount: "Don't have an account?",
      createOne: 'Create one',
      demoAccess: 'Quick demo access:',
      candidate: 'Candidate',
      recruiter: 'Recruiter',
    },
    
    // Register Page
    register: {
      title: 'Create Account',
      subtitle: 'Join Wassit Online - ANEM Platform',
      fullName: 'Full Name',
      email: 'Email Address',
      password: 'Password',
      confirmPassword: 'Confirm Password',
      role: 'I am a...',
      jobSeeker: 'Job Seeker',
      recruiter: 'Recruiter',
      submit: 'Create Account',
      submitting: 'Creating account...',
      haveAccount: 'Already have an account?',
      signIn: 'Sign In',
      success: 'Account Created!',
      redirecting: 'Redirecting to login page...',
    },
    
    // Profile/CV Builder
    profile: {
      title: 'My Profile',
      buildCV: 'Build Your CV',
      personalInfo: 'Personal Information',
      education: 'Education',
      experience: 'Work Experience',
      skills: 'Skills',
      languages: 'Languages',
      phone: 'Phone Number',
      address: 'Address',
      dateOfBirth: 'Date of Birth',
      bio: 'About Me',
      save: 'Save Profile',
      saving: 'Saving...',
    },
    
    // ANEM specific
    anem: {
      wilaya: 'Wilaya',
      selectWilaya: 'Select Wilaya',
      sector: 'Sector',
      selectSector: 'Select Sector',
      registration: 'ANEM Registration',
      registrationDate: 'Registration Date',
      renewalDate: 'Renewal Date',
      registered: 'Registered with ANEM',
    },
    
    // Common
    common: {
      loading: 'Loading...',
      error: 'An error occurred',
      save: 'Save',
      cancel: 'Cancel',
      edit: 'Edit',
      delete: 'Delete',
      search: 'Search',
      filter: 'Filter',
      all: 'All',
    },
  },
  
  fr: {
    // Navigation
    nav: {
      chat: 'Discussion',
      jobs: 'Emplois',
      applications: 'Mes Candidatures',
      login: 'Connexion',
      register: "S'inscrire",
      logout: 'Déconnexion',
    },
    
    // Chat Page
    chat: {
      welcome: 'Bienvenue sur Wassit Online',
      subtitle: 'Votre assistant carrière ANEM',
      description: 'Je peux vous aider à trouver des opportunités d\'emploi, postuler en un message, suivre vos candidatures et répondre à vos questions sur les services ANEM.',
      features: 'Ce que je peux faire',
      smartSearch: 'Recherche intelligente',
      searchExample: 'Emplois à Alger',
      quickApply: 'Candidature rapide',
      applyExample: 'Postuler pour l\'emploi #5',
      trackProgress: 'Suivre la progression',
      trackExample: 'Afficher mes candidatures',
      anemFaq: 'FAQ ANEM',
      anemExample: 'Comment renouveler mon inscription?',
      tips: 'Conseils',
      tip1: 'Précisez votre Wilaya pour les emplois locaux',
      tip2: 'Demandez des infos sur DAIP, CTA, CFI',
      tip3: 'Inscrivez-vous pour sauvegarder vos candidatures',
      placeholder: "Tapez votre message... (ex: 'Emplois à Oran' ou 'Comment m'inscrire à l'ANEM?')",
      aiThinking: 'L\'IA réfléchit...',
    },
    
    // Jobs Page
    jobs: {
      title: 'Trouvez votre emploi de rêve',
      subtitle: 'Parcourez nos offres d\'emploi',
      searchPlaceholder: 'Titre du poste ou mot-clé',
      location: 'Wilaya',
      allTypes: 'Tous les types',
      internship: 'Stage',
      fullTime: 'CDI',
      partTime: 'Temps partiel',
      contract: 'CDD',
      freelance: 'Freelance',
      search: 'Rechercher',
      loading: 'Chargement...',
      noResults: 'Aucun emploi trouvé. Essayez d\'autres critères.',
      found: 'emplois trouvés',
      applyNow: 'Postuler',
      loginToApply: 'Connectez-vous pour postuler',
      salary: 'Salaire',
      skills: 'Compétences',
    },
    
    // Applications Page
    applications: {
      title: 'Mes Candidatures',
      subtitle: 'Suivez votre progression',
      description: 'Restez informé du statut de vos candidatures',
      noApplications: 'Aucune candidature',
      noApplicationsDesc: "Vous n'avez pas encore postulé. Explorez nos offres d'emploi!",
      findJobs: 'Trouver des emplois',
      pending: 'En attente',
      reviewed: 'Examinée',
      interview: 'Entretien',
      accepted: 'Acceptée',
      rejected: 'Refusée',
      appliedOn: 'Postulé le',
    },
    
    // Login Page
    login: {
      title: 'Bon retour',
      subtitle: 'Connectez-vous à Wassit Online',
      email: 'Adresse email',
      password: 'Mot de passe',
      submit: 'Se connecter',
      submitting: 'Connexion...',
      noAccount: "Pas encore de compte?",
      createOne: 'Créer un compte',
      demoAccess: 'Accès démo rapide:',
      candidate: 'Candidat',
      recruiter: 'Recruteur',
    },
    
    // Register Page
    register: {
      title: 'Créer un compte',
      subtitle: 'Rejoignez Wassit Online - Plateforme ANEM',
      fullName: 'Nom complet',
      email: 'Adresse email',
      password: 'Mot de passe',
      confirmPassword: 'Confirmer le mot de passe',
      role: 'Je suis...',
      jobSeeker: 'Demandeur d\'emploi',
      recruiter: 'Recruteur',
      submit: 'Créer le compte',
      submitting: 'Création en cours...',
      haveAccount: 'Déjà un compte?',
      signIn: 'Se connecter',
      success: 'Compte créé!',
      redirecting: 'Redirection vers la connexion...',
    },
    
    // Profile/CV Builder
    profile: {
      title: 'Mon Profil',
      buildCV: 'Construire mon CV',
      personalInfo: 'Informations personnelles',
      education: 'Formation',
      experience: 'Expérience professionnelle',
      skills: 'Compétences',
      languages: 'Langues',
      phone: 'Téléphone',
      address: 'Adresse',
      dateOfBirth: 'Date de naissance',
      bio: 'À propos de moi',
      save: 'Enregistrer',
      saving: 'Enregistrement...',
    },
    
    // ANEM specific
    anem: {
      wilaya: 'Wilaya',
      selectWilaya: 'Sélectionner la Wilaya',
      sector: 'Secteur',
      selectSector: 'Sélectionner le secteur',
      registration: 'Inscription ANEM',
      registrationDate: 'Date d\'inscription',
      renewalDate: 'Date de renouvellement',
      registered: 'Inscrit à l\'ANEM',
    },
    
    // Common
    common: {
      loading: 'Chargement...',
      error: 'Une erreur est survenue',
      save: 'Enregistrer',
      cancel: 'Annuler',
      edit: 'Modifier',
      delete: 'Supprimer',
      search: 'Rechercher',
      filter: 'Filtrer',
      all: 'Tout',
    },
  },
  
  ar: {
    // Navigation
    nav: {
      chat: 'المحادثة',
      jobs: 'الوظائف',
      applications: 'طلباتي',
      login: 'تسجيل الدخول',
      register: 'إنشاء حساب',
      logout: 'تسجيل الخروج',
    },
    
    // Chat Page
    chat: {
      welcome: 'مرحبا بك في وسيط أونلاين',
      subtitle: 'مساعدك المهني من الوكالة الوطنية للتشغيل',
      description: 'يمكنني مساعدتك في إيجاد فرص العمل، التقديم برسالة واحدة، متابعة طلباتك والإجابة على أسئلتك حول خدمات الوكالة.',
      features: 'ما يمكنني فعله',
      smartSearch: 'بحث ذكي',
      searchExample: 'وظائف في الجزائر',
      quickApply: 'تقديم سريع',
      applyExample: 'تقديم للوظيفة رقم 5',
      trackProgress: 'متابعة التقدم',
      trackExample: 'عرض طلباتي',
      anemFaq: 'أسئلة شائعة',
      anemExample: 'كيف أجدد تسجيلي؟',
      tips: 'نصائح',
      tip1: 'حدد ولايتك للوظائف المحلية',
      tip2: 'اسأل عن برامج DAIP، CTA، CFI',
      tip3: 'سجّل لحفظ طلباتك',
      placeholder: "اكتب رسالتك... (مثال: 'وظائف في وهران')",
      aiThinking: 'جاري التفكير...',
    },
    
    // Jobs Page
    jobs: {
      title: 'ابحث عن وظيفة أحلامك',
      subtitle: 'تصفح عروض العمل المتاحة',
      searchPlaceholder: 'عنوان الوظيفة أو كلمة مفتاحية',
      location: 'الولاية',
      allTypes: 'جميع الأنواع',
      internship: 'تربص',
      fullTime: 'دوام كامل',
      partTime: 'دوام جزئي',
      contract: 'عقد محدد',
      freelance: 'عمل حر',
      search: 'بحث',
      loading: 'جاري التحميل...',
      noResults: 'لا توجد وظائف. جرّب معايير أخرى.',
      found: 'وظيفة موجودة',
      applyNow: 'تقديم الآن',
      loginToApply: 'سجّل الدخول للتقديم',
      salary: 'الراتب',
      skills: 'المهارات',
    },
    
    // Applications Page
    applications: {
      title: 'طلباتي',
      subtitle: 'تابع تقدّمك',
      description: 'ابق على اطلاع بحالة طلباتك',
      noApplications: 'لا توجد طلبات',
      noApplicationsDesc: 'لم تتقدم لأي وظيفة بعد. تصفح عروض العمل!',
      findJobs: 'البحث عن وظائف',
      pending: 'قيد الانتظار',
      reviewed: 'تمت المراجعة',
      interview: 'مقابلة',
      accepted: 'مقبول',
      rejected: 'مرفوض',
      appliedOn: 'تاريخ التقديم',
    },
    
    // Login Page
    login: {
      title: 'مرحبا بعودتك',
      subtitle: 'سجّل الدخول إلى وسيط أونلاين',
      email: 'البريد الإلكتروني',
      password: 'كلمة المرور',
      submit: 'تسجيل الدخول',
      submitting: 'جاري الدخول...',
      noAccount: 'ليس لديك حساب؟',
      createOne: 'إنشاء حساب',
      demoAccess: 'وصول تجريبي سريع:',
      candidate: 'مرشح',
      recruiter: 'موظّف',
    },
    
    // Register Page
    register: {
      title: 'إنشاء حساب',
      subtitle: 'انضم إلى وسيط أونلاين - منصة الوكالة الوطنية للتشغيل',
      fullName: 'الاسم الكامل',
      email: 'البريد الإلكتروني',
      password: 'كلمة المرور',
      confirmPassword: 'تأكيد كلمة المرور',
      role: 'أنا...',
      jobSeeker: 'باحث عن عمل',
      recruiter: 'موظّف',
      submit: 'إنشاء الحساب',
      submitting: 'جاري الإنشاء...',
      haveAccount: 'لديك حساب؟',
      signIn: 'تسجيل الدخول',
      success: 'تم إنشاء الحساب!',
      redirecting: 'جاري التحويل...',
    },
    
    // Profile/CV Builder
    profile: {
      title: 'ملفي الشخصي',
      buildCV: 'بناء السيرة الذاتية',
      personalInfo: 'المعلومات الشخصية',
      education: 'التعليم',
      experience: 'الخبرة المهنية',
      skills: 'المهارات',
      languages: 'اللغات',
      phone: 'رقم الهاتف',
      address: 'العنوان',
      dateOfBirth: 'تاريخ الميلاد',
      bio: 'نبذة عني',
      save: 'حفظ',
      saving: 'جاري الحفظ...',
    },
    
    // ANEM specific
    anem: {
      wilaya: 'الولاية',
      selectWilaya: 'اختر الولاية',
      sector: 'القطاع',
      selectSector: 'اختر القطاع',
      registration: 'التسجيل في الوكالة',
      registrationDate: 'تاريخ التسجيل',
      renewalDate: 'تاريخ التجديد',
      registered: 'مسجّل في الوكالة',
    },
    
    // Common
    common: {
      loading: 'جاري التحميل...',
      error: 'حدث خطأ',
      save: 'حفظ',
      cancel: 'إلغاء',
      edit: 'تعديل',
      delete: 'حذف',
      search: 'بحث',
      filter: 'تصفية',
      all: 'الكل',
    },
  },
};

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    const saved = localStorage.getItem('language');
    return saved || 'fr'; // Default to French for Algeria
  });

  useEffect(() => {
    localStorage.setItem('language', language);
    // Update document direction for Arabic
    document.documentElement.dir = language === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = language;
  }, [language]);

  const t = (key) => {
    // Support nested keys like 'chat.welcome'
    const keys = key.split('.');
    let value = translations[language];
    for (const k of keys) {
      value = value?.[k];
    }
    if (value !== undefined) return value;
    
    // Fallback to English
    value = translations.en;
    for (const k of keys) {
      value = value?.[k];
    }
    return value !== undefined ? value : key;
  };

  const getWilayaName = (code) => {
    const wilaya = WILAYAS.find(w => w.code === code);
    if (!wilaya) return code;
    return language === 'ar' ? wilaya.nameAr : wilaya.name;
  };

  const getSectors = () => {
    return SECTORS[language] || SECTORS.en;
  };

  return (
    <LanguageContext.Provider value={{ 
      language, 
      setLanguage, 
      t, 
      WILAYAS, 
      getWilayaName, 
      getSectors,
      isRTL: language === 'ar' 
    }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
