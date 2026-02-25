import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

// Document type labels in 3 languages
const DOCUMENT_LABELS = {
  cni: { fr: "Carte Nationale d'Identité", ar: "بطاقة التعريف الوطنية", en: "National ID Card" },
  residence: { fr: "Certificat de Résidence", ar: "شهادة الإقامة", en: "Residence Certificate" },
  photo: { fr: "Photos d'identité", ar: "صور شمسية", en: "ID Photos" },
  diploma: { fr: "Diplômes/Certificats", ar: "الشهادات والدبلومات", en: "Diplomas/Certificates" },
  cv: { fr: "CV (Curriculum Vitae)", ar: "السيرة الذاتية", en: "Resume/CV" },
  birth_certificate: { fr: "Extrait de Naissance", ar: "شهادة الميلاد", en: "Birth Certificate" },
  military: { fr: "Situation Militaire", ar: "الوضعية تجاه الخدمة الوطنية", en: "Military Service" },
  work_certificate: { fr: "Attestation de Travail", ar: "شهادة العمل", en: "Work Certificate" }
};

const STATUS_STYLES = {
  not_submitted: { bg: 'bg-gray-100 dark:bg-gray-700', text: 'text-gray-600 dark:text-gray-300', icon: '📄' },
  pending: { bg: 'bg-yellow-100 dark:bg-yellow-900', text: 'text-yellow-700 dark:text-yellow-300', icon: '⏳' },
  approved: { bg: 'bg-green-100 dark:bg-green-900', text: 'text-green-700 dark:text-green-300', icon: '✅' },
  rejected: { bg: 'bg-red-100 dark:bg-red-900', text: 'text-red-700 dark:text-red-300', icon: '❌' }
};

const STATUS_LABELS = {
  not_submitted: { fr: "Non soumis", ar: "غير مقدم", en: "Not submitted" },
  pending: { fr: "En attente", ar: "قيد المراجعة", en: "Pending" },
  approved: { fr: "Approuvé", ar: "مقبول", en: "Approved" },
  rejected: { fr: "Rejeté", ar: "مرفوض", en: "Rejected" }
};

export default function DossierPage() {
  const { user } = useAuth();
  const [dossier, setDossier] = useState(null);
  const [requirements, setRequirements] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploadingDoc, setUploadingDoc] = useState(null);
  const [lang, setLang] = useState('fr'); // Default to French

  useEffect(() => {
    fetchDossier();
    fetchRequirements();
  }, []);

  const fetchDossier = async () => {
    try {
      const response = await api.get('/documents/my-dossier');
      setDossier(response.data);
    } catch (err) {
      setError('Erreur lors du chargement du dossier');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRequirements = async () => {
    try {
      const response = await api.get('/documents/requirements');
      setRequirements(response.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmitDocument = async (docType) => {
    setUploadingDoc(docType);
    
    // Simulate file upload - in real app, this would use file input
    try {
      await api.post('/documents', {
        document_type: docType,
        file_name: `${docType}_${Date.now()}.pdf`,
        file_url: `/uploads/${docType}_${Date.now()}.pdf`
      });
      await fetchDossier();
    } catch (err) {
      console.error(err);
      alert('Erreur lors de la soumission');
    } finally {
      setUploadingDoc(null);
    }
  };

  const getDocLabel = (docType) => {
    return DOCUMENT_LABELS[docType]?.[lang] || docType;
  };

  const getStatusLabel = (status) => {
    return STATUS_LABELS[status]?.[lang] || status;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center p-8">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-4">
            {lang === 'ar' ? 'يرجى تسجيل الدخول' : lang === 'fr' ? 'Connexion requise' : 'Login Required'}
          </h2>
          <p className="text-gray-600 dark:text-gray-300">
            {lang === 'ar' ? 'يجب تسجيل الدخول لعرض ملفك' : lang === 'fr' ? 'Connectez-vous pour voir votre dossier' : 'Please login to view your dossier'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Language Selector */}
        <div className="flex justify-end mb-4 space-x-2">
          <button onClick={() => setLang('fr')} className={`px-3 py-1 rounded ${lang === 'fr' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}>FR</button>
          <button onClick={() => setLang('ar')} className={`px-3 py-1 rounded ${lang === 'ar' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}>عربي</button>
          <button onClick={() => setLang('en')} className={`px-3 py-1 rounded ${lang === 'en' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}>EN</button>
        </div>

        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white mb-2">
            {lang === 'ar' ? '📁 ملف التسجيل ANEM' : lang === 'fr' ? '📁 Dossier d\'inscription ANEM' : '📁 ANEM Registration Dossier'}
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            {lang === 'ar' ? 'تتبع وثائقك للتسجيل في ANEM' : lang === 'fr' ? 'Suivez vos documents pour l\'inscription ANEM' : 'Track your documents for ANEM registration'}
          </p>
        </div>

        {/* Progress Card */}
        {dossier && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">
              {lang === 'ar' ? 'حالة التقدم' : lang === 'fr' ? 'Progression' : 'Progress'}
            </h2>
            
            {/* Progress Bar */}
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600 dark:text-gray-300">
                  {lang === 'ar' ? `${dossier.total_approved}/${dossier.total_required} وثائق مقبولة` 
                    : lang === 'fr' ? `${dossier.total_approved}/${dossier.total_required} documents approuvés` 
                    : `${dossier.total_approved}/${dossier.total_required} documents approved`}
                </span>
                <span className="font-semibold text-blue-600">{Math.round(dossier.completion_percentage)}%</span>
              </div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-green-500 transition-all duration-500"
                  style={{ width: `${dossier.completion_percentage}%` }}
                ></div>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="text-2xl font-bold text-gray-800 dark:text-white">{dossier.total_submitted}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {lang === 'ar' ? 'مقدم' : lang === 'fr' ? 'Soumis' : 'Submitted'}
                </div>
              </div>
              <div className="text-center p-3 bg-yellow-50 dark:bg-yellow-900/30 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">{dossier.total_pending}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {lang === 'ar' ? 'قيد المراجعة' : lang === 'fr' ? 'En attente' : 'Pending'}
                </div>
              </div>
              <div className="text-center p-3 bg-green-50 dark:bg-green-900/30 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{dossier.total_approved}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {lang === 'ar' ? 'مقبول' : lang === 'fr' ? 'Approuvés' : 'Approved'}
                </div>
              </div>
              <div className="text-center p-3 bg-red-50 dark:bg-red-900/30 rounded-lg">
                <div className="text-2xl font-bold text-red-600">{dossier.total_rejected}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {lang === 'ar' ? 'مرفوض' : lang === 'fr' ? 'Rejetés' : 'Rejected'}
                </div>
              </div>
            </div>

            {/* Status Badges */}
            <div className="mt-4 flex flex-wrap gap-2">
              {dossier.can_apply ? (
                <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full text-sm">
                  ✅ {lang === 'ar' ? 'يمكنك التقدم للوظائف' : lang === 'fr' ? 'Peut postuler aux emplois' : 'Can apply for jobs'}
                </span>
              ) : (
                <span className="px-3 py-1 bg-orange-100 dark:bg-orange-900 text-orange-700 dark:text-orange-300 rounded-full text-sm">
                  ⚠️ {lang === 'ar' ? 'أكمل ملفك للتقدم' : lang === 'fr' ? 'Complétez votre dossier' : 'Complete dossier to apply'}
                </span>
              )}
              {dossier.is_complete && (
                <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full text-sm">
                  🎉 {lang === 'ar' ? 'الملف مكتمل' : lang === 'fr' ? 'Dossier complet' : 'Dossier complete'}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Documents List */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">
            {lang === 'ar' ? 'الوثائق المطلوبة' : lang === 'fr' ? 'Documents requis' : 'Required Documents'}
          </h2>
          
          <div className="space-y-3">
            {dossier?.documents.map((doc, index) => {
              const statusStyle = STATUS_STYLES[doc.status] || STATUS_STYLES.not_submitted;
              const isRequired = ['cni', 'residence', 'photo', 'diploma', 'cv'].includes(doc.document_type);
              
              return (
                <div 
                  key={doc.id || index}
                  className={`p-4 rounded-lg border-2 ${statusStyle.bg} border-transparent hover:border-blue-300 transition-all`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3 rtl:space-x-reverse">
                      <span className="text-2xl">{statusStyle.icon}</span>
                      <div>
                        <h3 className={`font-medium ${statusStyle.text}`}>
                          {getDocLabel(doc.document_type)}
                          {isRequired && <span className="text-red-500 ml-1">*</span>}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {getStatusLabel(doc.status)}
                          {doc.submitted_at && ` - ${new Date(doc.submitted_at).toLocaleDateString()}`}
                        </p>
                        {doc.notes && (
                          <p className="text-sm text-red-500 mt-1">📝 {doc.notes}</p>
                        )}
                      </div>
                    </div>
                    
                    <div>
                      {doc.status === 'not_submitted' || doc.status === 'rejected' ? (
                        <button
                          onClick={() => handleSubmitDocument(doc.document_type)}
                          disabled={uploadingDoc === doc.document_type}
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm disabled:opacity-50"
                        >
                          {uploadingDoc === doc.document_type 
                            ? '...' 
                            : lang === 'ar' ? 'تحميل' : lang === 'fr' ? 'Soumettre' : 'Upload'}
                        </button>
                      ) : doc.status === 'pending' ? (
                        <span className="px-3 py-1 bg-yellow-200 dark:bg-yellow-800 text-yellow-800 dark:text-yellow-200 rounded text-sm">
                          ⏳
                        </span>
                      ) : (
                        <span className="px-3 py-1 bg-green-200 dark:bg-green-800 text-green-800 dark:text-green-200 rounded text-sm">
                          ✓
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Required Note */}
          <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">
            <span className="text-red-500">*</span> {lang === 'ar' ? 'وثيقة إلزامية' : lang === 'fr' ? 'Document obligatoire' : 'Required document'}
          </p>
        </div>

        {/* Help Section */}
        <div className="mt-6 bg-blue-50 dark:bg-blue-900/30 rounded-xl p-6">
          <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">
            💡 {lang === 'ar' ? 'نصائح' : lang === 'fr' ? 'Conseils' : 'Tips'}
          </h3>
          <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
            <li>• {lang === 'ar' ? 'تأكد من جودة المسح الضوئي' : lang === 'fr' ? 'Assurez-vous que les scans sont lisibles' : 'Ensure scans are readable'}</li>
            <li>• {lang === 'ar' ? 'الملفات بصيغة PDF مفضلة' : lang === 'fr' ? 'Format PDF recommandé' : 'PDF format recommended'}</li>
            <li>• {lang === 'ar' ? 'حجم الملف الأقصى: 5 ميغابايت' : lang === 'fr' ? 'Taille max: 5 Mo' : 'Max file size: 5MB'}</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
