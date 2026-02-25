"""
AI Service for natural language processing
Handles job search queries, application commands, and general assistance
Optimized for ANEM/Wassit Online Algeria
Supports French, Arabic (Darja), and English
"""

import re
import json
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..core.config import settings
from ..models.models import Job, Application, User, ApplicationStatus


# All 58 Algerian Wilayas for location matching
ALGERIAN_WILAYAS = [
    'adrar', 'chlef', 'laghouat', 'oum el bouaghi', 'batna', 'béjaïa', 'bejaia', 
    'biskra', 'béchar', 'bechar', 'blida', 'bouira', 'tamanrasset', 'tébessa', 
    'tebessa', 'tlemcen', 'tiaret', 'tizi ouzou', 'alger', 'algiers', 'djelfa', 
    'jijel', 'sétif', 'setif', 'saïda', 'saida', 'skikda', 'sidi bel abbès', 
    'sidi bel abbes', 'annaba', 'guelma', 'constantine', 'médéa', 'medea', 
    'mostaganem', "m'sila", 'msila', 'mascara', 'ouargla', 'oran', 'el bayadh', 
    'illizi', 'bordj bou arréridj', 'bordj bou arreridj', 'boumerdès', 'boumerdes', 
    'el tarf', 'tindouf', 'tissemsilt', 'el oued', 'khenchela', 'souk ahras', 
    'tipaza', 'mila', 'aïn defla', 'ain defla', 'naâma', 'naama', 
    'aïn témouchent', 'ain temouchent', 'ghardaïa', 'ghardaia', 'relizane',
    "el m'ghair", 'el meniaa', 'ouled djellal', 'bordj badji mokhtar', 
    'béni abbès', 'beni abbes', 'timimoun', 'touggourt', 'djanet', 'in salah', 'in guezzam'
]

# Job sectors for filtering
JOB_SECTORS = {
    'it': ['informatique', 'it', 'tech', 'développeur', 'developer', 'مبرمج', 'تكنولوجيا'],
    'healthcare': ['santé', 'health', 'médecin', 'infirmier', 'pharmacie', 'صحة', 'طبيب'],
    'education': ['éducation', 'enseignement', 'teacher', 'professeur', 'تعليم', 'أستاذ'],
    'construction': ['btp', 'construction', 'bâtiment', 'architecture', 'بناء', 'هندسة'],
    'finance': ['finance', 'banque', 'comptable', 'banking', 'مالية', 'بنك', 'محاسب'],
    'commerce': ['commerce', 'vente', 'sales', 'commercial', 'تجارة', 'مبيعات'],
    'industry': ['industrie', 'factory', 'usine', 'manufacturing', 'صناعة', 'مصنع'],
    'oil_gas': ['pétrole', 'gaz', 'oil', 'gas', 'sonatrach', 'نفط', 'غاز'],
    'agriculture': ['agriculture', 'farming', 'فلاحة', 'زراعة'],
    'tourism': ['tourisme', 'hôtellerie', 'hotel', 'tourism', 'سياحة', 'فندقة'],
    'transport': ['transport', 'logistique', 'logistics', 'chauffeur', 'نقل'],
    'telecom': ['télécom', 'telecom', 'mobilis', 'djezzy', 'ooredoo', 'اتصالات']
}

# ANEM FAQ Database
ANEM_FAQ = {
    # Registration questions
    "register|inscription|s'inscrire|تسجيل|enregistrer": {
        "en": """To register with ANEM (Wassit Online):
1. Visit https://wassitonline.anem.dz
2. Click "Espace demandeur" (Job Seeker Space)
3. Create an account with your email
4. Complete your profile with personal info
5. Upload required documents

**Required documents:**
- National ID card (CNI)
- Residence certificate (Certificat de résidence)
- Passport photos
- Diplomas/certificates""",
        "fr": """Pour s'inscrire à l'ANEM (Wassit Online):
1. Visitez https://wassitonline.anem.dz
2. Cliquez sur "Espace demandeur"
3. Créez un compte avec votre email
4. Complétez votre profil
5. Téléchargez les documents requis

**Documents requis:**
- Carte nationale d'identité (CNI)
- Certificat de résidence
- Photos d'identité
- Diplômes/certificats""",
        "ar": """للتسجيل في ANEM (وسيط أونلاين):
1. قم بزيارة https://wassitonline.anem.dz
2. انقر على "فضاء طالب العمل"
3. أنشئ حساباً بالبريد الإلكتروني
4. أكمل ملفك الشخصي
5. حمّل الوثائق المطلوبة

**الوثائق المطلوبة:**
- بطاقة التعريف الوطنية
- شهادة الإقامة
- صور شمسية
- الشهادات والدبلومات"""
    },
    
    # Renewal questions
    "renew|renouveler|renouvellement|تجديد|renewal": {
        "en": """To renew your ANEM registration:
1. Log in to Wassit Online
2. Go to "Renouveler ma demande"
3. Update your information if needed
4. Confirm the renewal

**Important:** Renewal must be done every 6 months. You'll receive an SMS reminder.""",
        "fr": """Pour renouveler votre inscription ANEM:
1. Connectez-vous à Wassit Online
2. Allez sur "Renouveler ma demande"
3. Mettez à jour vos informations si nécessaire
4. Confirmez le renouvellement

**Important:** Le renouvellement doit être fait tous les 6 mois. Vous recevrez un rappel par SMS.""",
        "ar": """لتجديد تسجيلك في ANEM:
1. سجّل الدخول إلى وسيط أونلاين
2. اذهب إلى "تجديد طلبي"
3. حدّث معلوماتك إذا لزم الأمر
4. أكّد التجديد

**مهم:** يجب التجديد كل 6 أشهر. ستتلقى رسالة تذكير."""
    },
    
    # Documents questions
    "documents|papers|papiers|وثائق|dossier": {
        "en": """Documents needed for ANEM registration:

**Mandatory:**
- National ID card (CNI)
- Residence certificate (less than 3 months old)
- 4 passport photos
- Birth certificate

**For graduates:**
- Diploma copy
- Academic transcripts

**For experienced workers:**
- Work certificates
- Reference letters""",
        "fr": """Documents nécessaires pour l'inscription ANEM:

**Obligatoires:**
- Carte nationale d'identité (CNI)
- Certificat de résidence (moins de 3 mois)
- 4 photos d'identité
- Acte de naissance

**Pour les diplômés:**
- Copie du diplôme
- Relevés de notes

**Pour les expérimentés:**
- Certificats de travail
- Lettres de recommandation""",
        "ar": """الوثائق المطلوبة للتسجيل في ANEM:

**إلزامية:**
- بطاقة التعريف الوطنية
- شهادة الإقامة (أقل من 3 أشهر)
- 4 صور شمسية
- شهادة الميلاد

**للمتخرجين:**
- نسخة من الشهادة
- كشوف النقاط

**لذوي الخبرة:**
- شهادات العمل
- رسائل التوصية"""
    },
    
    # Training questions
    "training|formation|تكوين|stage": {
        "en": """ANEM offers several training programs:

**1. DAIP (Dispositif d'Aide à l'Insertion Professionnelle)**
- For first-time job seekers
- Internship with monthly allowance
- Duration: 6-12 months

**2. CFI (Contrat Formation-Insertion)**
- Professional training contract
- Leads to permanent employment

**3. CTA (Contrat de Travail Aidé)**
- Subsidized employment contract
- For experienced workers

Visit your local ANEM agency for more details.""",
        "fr": """L'ANEM propose plusieurs programmes de formation:

**1. DAIP (Dispositif d'Aide à l'Insertion Professionnelle)**
- Pour les primo-demandeurs d'emploi
- Stage avec indemnité mensuelle
- Durée: 6-12 mois

**2. CFI (Contrat Formation-Insertion)**
- Contrat de formation professionnelle
- Mène à un emploi permanent

**3. CTA (Contrat de Travail Aidé)**
- Contrat de travail subventionné
- Pour les travailleurs expérimentés

Visitez votre agence ANEM locale pour plus de détails.""",
        "ar": """يقدم ANEM عدة برامج تكوينية:

**1. DAIP (جهاز المساعدة على الإدماج المهني)**
- للباحثين عن العمل لأول مرة
- تربص مع منحة شهرية
- المدة: 6-12 شهر

**2. CFI (عقد التكوين والإدماج)**
- عقد تكوين مهني
- يؤدي إلى توظيف دائم

**3. CTA (عقد العمل المدعوم)**
- عقد عمل مدعوم
- للعمال ذوي الخبرة

قم بزيارة وكالة ANEM المحلية لمزيد من التفاصيل."""
    },
    
    # Contact questions
    "contact|agency|agence|وكالة|address|adresse|عنوان": {
        "en": """ANEM Contact Information:

**Headquarters:**
5 Rue Capitaine Nourreddine Mennani, Algiers

**Website:** https://wassitonline.anem.dz
**Email:** support.technique@anem.dz

**Find your local agency:**
Visit the ANEM website and search by Wilaya

**Hotline:** Call your local agency for appointments""",
        "fr": """Coordonnées ANEM:

**Siège:**
5 Rue Capitaine Nourreddine Mennani, Alger

**Site web:** https://wassitonline.anem.dz
**Email:** support.technique@anem.dz

**Trouver votre agence locale:**
Visitez le site ANEM et recherchez par Wilaya

**Assistance:** Appelez votre agence locale pour prendre rendez-vous""",
        "ar": """معلومات الاتصال بـ ANEM:

**المقر الرئيسي:**
5 شارع النقيب نورالدين مناني، الجزائر

**الموقع:** https://wassitonline.anem.dz
**البريد:** support.technique@anem.dz

**ابحث عن وكالتك المحلية:**
قم بزيارة موقع ANEM وابحث حسب الولاية

**المساعدة:** اتصل بوكالتك المحلية لحجز موعد"""
    },
    
    # ANIS/ANSEJ questions
    "ansej|anis|cnac|startup|مقاولاتية|entreprise": {
        "en": """For entrepreneurship support in Algeria:

**ANIS (ex-ANSEJ)** - For young entrepreneurs (19-40 years)
- Startup funding
- Interest-free loans
- Training and support

**CNAC** - For unemployed over 30 years
- Business creation support
- Equipment financing

**Requirements:**
- Algerian nationality
- Professional qualification
- Business plan

Visit www.anis.dz for more information.""",
        "fr": """Pour le soutien à l'entrepreneuriat en Algérie:

**ANIS (ex-ANSEJ)** - Pour jeunes entrepreneurs (19-40 ans)
- Financement de startup
- Prêts sans intérêts
- Formation et accompagnement

**CNAC** - Pour chômeurs de plus de 30 ans
- Aide à la création d'entreprise
- Financement d'équipements

**Conditions:**
- Nationalité algérienne
- Qualification professionnelle
- Business plan

Visitez www.anis.dz pour plus d'informations.""",
        "ar": """لدعم ريادة الأعمال في الجزائر:

**ANIS (سابقاً ANSEJ)** - لرواد الأعمال الشباب (19-40 سنة)
- تمويل المشاريع الناشئة
- قروض بدون فوائد
- تكوين ومرافقة

**CNAC** - للعاطلين فوق 30 سنة
- دعم إنشاء المؤسسات
- تمويل المعدات

**الشروط:**
- الجنسية الجزائرية
- مؤهل مهني
- دراسة جدوى

قم بزيارة www.anis.dz لمزيد من المعلومات."""
    },
    
    # Interview preparation
    "interview|entretien|مقابلة|préparation": {
        "en": """Interview preparation tips for ANEM placements:

**Before the interview:**
- Research the company
- Prepare copies of your CV and documents
- Dress professionally
- Arrive 15 minutes early

**During the interview:**
- Speak clearly and confidently
- Give specific examples of your skills
- Ask questions about the role
- Show enthusiasm

**Common questions:**
- "Tell me about yourself"
- "Why do you want this job?"
- "What are your strengths/weaknesses?"
- "Where do you see yourself in 5 years?"

**For DAIP placements:**
- Emphasize your willingness to learn
- Show motivation for the field
- Ask about training opportunities""",
        "fr": """Conseils de préparation à l'entretien:

**Avant l'entretien:**
- Renseignez-vous sur l'entreprise
- Préparez des copies de votre CV et documents
- Habillez-vous professionnellement
- Arrivez 15 minutes en avance

**Pendant l'entretien:**
- Parlez clairement et avec confiance
- Donnez des exemples concrets de vos compétences
- Posez des questions sur le poste
- Montrez votre enthousiasme

**Questions fréquentes:**
- "Parlez-moi de vous"
- "Pourquoi voulez-vous ce poste?"
- "Quels sont vos points forts/faibles?"
- "Où vous voyez-vous dans 5 ans?"

**Pour les stages DAIP:**
- Soulignez votre volonté d'apprendre
- Montrez votre motivation
- Demandez les opportunités de formation""",
        "ar": """نصائح للتحضير للمقابلة:

**قبل المقابلة:**
- ابحث عن الشركة
- حضّر نسخاً من سيرتك الذاتية ووثائقك
- ارتدِ ملابس مهنية
- وصل قبل 15 دقيقة

**أثناء المقابلة:**
- تحدث بوضوح وثقة
- أعطِ أمثلة محددة عن مهاراتك
- اطرح أسئلة عن الوظيفة
- أظهر حماسك

**أسئلة شائعة:**
- "حدثني عن نفسك"
- "لماذا تريد هذه الوظيفة؟"
- "ما هي نقاط قوتك وضعفك؟"
- "أين ترى نفسك بعد 5 سنوات؟"

**لتربصات DAIP:**
- ركّز على رغبتك في التعلم
- أظهر الحافز في المجال
- اسأل عن فرص التكوين"""
    },
    
    # CV/Profile building
    "cv|سيرة|resume|profil|ملف": {
        "en": """Tips for building a strong CV for ANEM:

**Essential sections:**
1. Personal information (name, phone, email, address)
2. Professional objective (2-3 lines)
3. Education (most recent first)
4. Work experience (if any)
5. Skills (technical and soft)
6. Languages (Arabic, French, English levels)

**Tips:**
- Keep it to 1-2 pages
- Use clear formatting
- Include certifications
- Mention internships/volunteer work
- List computer skills (Word, Excel, etc.)

**Common mistakes to avoid:**
- Spelling errors
- Generic objectives
- Missing contact info
- Too long or too short

Would you like me to help you update your profile? Just tell me what to add!""",
        "fr": """Conseils pour créer un bon CV pour l'ANEM:

**Sections essentielles:**
1. Informations personnelles (nom, téléphone, email, adresse)
2. Objectif professionnel (2-3 lignes)
3. Formation (la plus récente en premier)
4. Expérience professionnelle (si existante)
5. Compétences (techniques et personnelles)
6. Langues (niveaux arabe, français, anglais)

**Conseils:**
- Limitez à 1-2 pages
- Utilisez un format clair
- Incluez les certifications
- Mentionnez les stages/bénévolat
- Listez les compétences informatiques (Word, Excel, etc.)

**Erreurs courantes à éviter:**
- Fautes d'orthographe
- Objectifs génériques
- Coordonnées manquantes
- Trop long ou trop court

Voulez-vous que je vous aide à mettre à jour votre profil? Dites-moi quoi ajouter!""",
        "ar": """نصائح لإنشاء سيرة ذاتية قوية لـ ANEM:

**الأقسام الأساسية:**
1. المعلومات الشخصية (الاسم، الهاتف، البريد، العنوان)
2. الهدف المهني (2-3 أسطر)
3. التعليم (الأحدث أولاً)
4. الخبرة المهنية (إن وجدت)
5. المهارات (تقنية وشخصية)
6. اللغات (مستويات العربية، الفرنسية، الإنجليزية)

**نصائح:**
- اجعلها صفحة أو صفحتين فقط
- استخدم تنسيقاً واضحاً
- أضف الشهادات
- اذكر التربصات/العمل التطوعي
- اذكر مهارات الكمبيوتر (Word، Excel، إلخ)

**أخطاء شائعة يجب تجنبها:**
- أخطاء إملائية
- أهداف عامة
- معلومات اتصال ناقصة
- طويل جداً أو قصير جداً

هل تريد مساعدتك في تحديث ملفك؟ أخبرني ماذا تريد إضافته!"""
    },
    
    # Renewal reminders
    "reminder|rappel|تذكير|deadline|délai|موعد": {
        "en": """ANEM Registration Renewal Information:

**Renewal deadline:** Every 6 months from your registration date

**How to renew:**
1. Login to wassitonline.anem.dz
2. Click "Renouveler ma demande"
3. Update your information if needed
4. Confirm the renewal

**Reminders:**
- ANEM sends SMS reminders before expiration
- You can also set a calendar reminder
- Non-renewal may require re-registration

**Tip:** Renew at least 2 weeks before the deadline to avoid issues.

Would you like me to remind you about renewal dates?""",
        "fr": """Informations sur le renouvellement ANEM:

**Délai de renouvellement:** Tous les 6 mois à partir de votre inscription

**Comment renouveler:**
1. Connectez-vous à wassitonline.anem.dz
2. Cliquez sur "Renouveler ma demande"
3. Mettez à jour vos informations si nécessaire
4. Confirmez le renouvellement

**Rappels:**
- L'ANEM envoie des SMS avant l'expiration
- Vous pouvez aussi mettre un rappel calendrier
- Le non-renouvellement peut nécessiter une ré-inscription

**Conseil:** Renouvelez au moins 2 semaines avant la date limite.""",
        "ar": """معلومات تجديد تسجيل ANEM:

**موعد التجديد:** كل 6 أشهر من تاريخ تسجيلك

**كيفية التجديد:**
1. سجّل الدخول إلى wassitonline.anem.dz
2. انقر على "تجديد طلبي"
3. حدّث معلوماتك إذا لزم الأمر
4. أكّد التجديد

**التذكيرات:**
- ترسل ANEM رسائل SMS قبل انتهاء الصلاحية
- يمكنك أيضاً وضع تذكير في التقويم
- عدم التجديد قد يتطلب إعادة التسجيل

**نصيحة:** جدّد قبل أسبوعين على الأقل من الموعد."""
    },
    
    # Sector-specific info
    "sector|secteur|قطاع|domain|domaine|مجال": {
        "en": """Job sectors available in Algeria:

**High demand sectors:**
🖥️ IT & Technology - Software, networks, digital
🏥 Healthcare - Doctors, nurses, pharmacists
🏗️ Construction - Engineers, architects, technicians
🛢️ Oil & Gas - Sonatrach, Schlumberger, etc.
🏦 Finance - Banks, accounting, insurance

**Growing sectors:**
📞 Telecommunications - Mobilis, Djezzy, Ooredoo
🏭 Industry - Manufacturing, factories
🌾 Agriculture - Farming, agribusiness
🚚 Transport & Logistics - Drivers, warehousing
🏨 Tourism & Hospitality - Hotels, restaurants

Tell me which sector interests you and I'll find relevant jobs!""",
        "fr": """Secteurs d'emploi disponibles en Algérie:

**Secteurs en forte demande:**
🖥️ IT & Technologie - Logiciels, réseaux, digital
🏥 Santé - Médecins, infirmiers, pharmaciens
🏗️ BTP - Ingénieurs, architectes, techniciens
🛢️ Pétrole & Gaz - Sonatrach, Schlumberger, etc.
🏦 Finance - Banques, comptabilité, assurance

**Secteurs en croissance:**
📞 Télécommunications - Mobilis, Djezzy, Ooredoo
🏭 Industrie - Fabrication, usines
🌾 Agriculture - Fermes, agrobusiness
🚚 Transport & Logistique - Chauffeurs, entreposage
🏨 Tourisme & Hôtellerie - Hôtels, restaurants

Dites-moi quel secteur vous intéresse et je trouverai les emplois!""",
        "ar": """قطاعات العمل المتاحة في الجزائر:

**قطاعات عالية الطلب:**
🖥️ تكنولوجيا المعلومات - برمجيات، شبكات، رقمنة
🏥 الصحة - أطباء، ممرضين، صيادلة
🏗️ البناء - مهندسين، معماريين، تقنيين
🛢️ النفط والغاز - سوناطراك، شلمبرجر، إلخ
🏦 المالية - بنوك، محاسبة، تأمين

**قطاعات نامية:**
📞 الاتصالات - موبيليس، جيزي، أوريدو
🏭 الصناعة - تصنيع، مصانع
🌾 الفلاحة - زراعة، أعمال زراعية
🚚 النقل واللوجستيك - سائقين، تخزين
🏨 السياحة والفندقة - فنادق، مطاعم

أخبرني بالقطاع الذي يهمك وسأجد لك الوظائف المناسبة!"""
    }
}


class AIService:
    """AI Service for processing chat messages with NLP and LLM support"""

    def __init__(self):
        self.openai_client = None
        self.groq_client = None
        self.nlp_fr = None
        self.nlp_en = None
        self._init_nlp()
        self._init_llm()

    def _init_nlp(self):
        """Initialize spaCy NLP models"""
        try:
            import spacy
            # Load French model for NLP processing
            try:
                self.nlp_fr = spacy.load("fr_core_news_sm")
            except OSError:
                pass
            # English model (optional)
            try:
                self.nlp_en = spacy.load("en_core_web_sm")
            except OSError:
                pass
        except ImportError:
            pass

    def _init_llm(self):
        """Initialize LLM clients (Groq or OpenAI)"""
        # Try Groq first (free tier)
        if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your-groq-api-key-here":
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
            except ImportError:
                pass
        
        # Fallback to OpenAI
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here":
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                pass

    def _detect_language(self, message: str) -> str:
        """Detect language using langdetect library with fallback"""
        try:
            from langdetect import detect, DetectorFactory
            DetectorFactory.seed = 0  # For consistent results
            lang = detect(message)
            # Map to our supported languages
            if lang == 'ar':
                return 'ar'
            elif lang == 'fr':
                return 'fr'
            else:
                return 'en'
        except:
            # Fallback to pattern-based detection
            return self._detect_language_fallback(message)

    def _detect_language_fallback(self, message: str) -> str:
        """Fallback language detection using patterns"""
        # Arabic detection - check for Arabic characters
        arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
        if arabic_pattern.search(message):
            return 'ar'
        
        # French detection - common French words/patterns
        french_indicators = [
            'bonjour', 'salut', 'merci', 'comment', 'pourquoi', 'quoi', 'qui', 'où',
            'trouver', 'cherche', 'emploi', 'travail', 'postuler', 'candidature',
            'je', 'tu', 'il', 'elle', 'nous', 'vous', 'les', 'des', 'une', 'est',
            "j'", "l'", "d'", "s'", "n'", "c'", 'dans', 'pour', 'avec', 'sur',
            'quel', 'quelle', 'quels', 'quelles', 'comment', "aujourd'hui",
            'inscription', 'renouvellement', 'documents', 'formation', 'stage',
            'aide', 'besoin', 'veux', 'voudrais', 'peux', 'puis', 'pouvez'
        ]
        message_lower = message.lower()
        french_count = sum(1 for word in french_indicators if word in message_lower)
        
        # English detection
        english_indicators = [
            'hello', 'hi', 'how', 'what', 'where', 'when', 'why', 'who',
            'find', 'search', 'looking', 'want', 'need', 'help', 'please',
            'job', 'jobs', 'work', 'apply', 'application', 'resume', 'cv',
            'the', 'is', 'are', 'am', 'of', 'in', 'at', 'for', 'to', 'and',
            'can', 'could', 'would', 'should', 'my', 'your', 'this', 'that'
        ]
        english_count = sum(1 for word in english_indicators if word in message_lower)
        
        # Decision logic
        if french_count > english_count:
            return 'fr'
        elif english_count > 0:
            return 'en'
        else:
            # Default to French for Algeria
            return 'fr'

    def process_message(
        self,
        message: str,
        db: Session,
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and return appropriate response
        Detects language and responds in the same language
        
        Returns:
            Dict with 'response', optional 'jobs', and optional 'action'
        """
        message_lower = message.lower().strip()
        
        # Detect language
        lang = self._detect_language(message)

        # Check for specific intents
        intent, params = self._detect_intent(message_lower)
        params['lang'] = lang  # Pass language to handlers

        if intent == "search_jobs":
            return self._handle_job_search(params, db, lang)
        elif intent == "apply_job":
            return self._handle_apply(params, db, user, lang)
        elif intent == "my_applications":
            return self._handle_my_applications(db, user, lang)
        elif intent == "anem_faq":
            return self._handle_anem_faq(params, lang)
        elif intent == "help":
            return self._handle_help(lang)
        elif intent == "greeting":
            return self._handle_greeting(user, lang)
        elif intent == "profile_update":
            return self._handle_profile_update(params, db, user, lang)
        else:
            # Try OpenAI if available, otherwise use fallback
            return self._handle_general_query(message, db, lang)

    def _detect_intent(self, message: str) -> Tuple[str, Dict]:
        """Detect the intent of the message"""
        params = {}

        # Greeting patterns
        greeting_patterns = ["hello", "hi", "hey", "bonjour", "salut", "good morning", "good afternoon", "مرحبا", "السلام", "صباح"]
        if any(message.startswith(g) for g in greeting_patterns):
            return "greeting", params

        # Help patterns
        if any(word in message for word in ["help", "what can you do", "commands", "aide", "مساعدة"]):
            return "help", params

        # ANEM FAQ detection
        for pattern, responses in ANEM_FAQ.items():
            if re.search(pattern, message, re.IGNORECASE):
                params["faq_key"] = pattern
                params["responses"] = responses
                return "anem_faq", params

        # Apply patterns
        apply_match = re.search(r"(?:apply|postuler|تقدم)\s+(?:for\s+)?(?:job\s+)?#?(\d+)", message)
        if apply_match:
            params["job_id"] = int(apply_match.group(1))
            return "apply_job", params

        # My applications
        if any(phrase in message for phrase in ["my applications", "mes candidatures", "show my applications", "list my applications", "طلباتي"]):
            return "my_applications", params

        # Job search patterns
        search_keywords = ["find", "search", "show", "list", "looking for", "cherche", "trouver", "jobs", "job", 
                          "positions", "internship", "internships", "stage", "emploi", "travail", "وظائف", "عمل", "ابحث"]
        if any(keyword in message for keyword in search_keywords):
            # Extract search parameters
            params = self._extract_search_params(message)
            return "search_jobs", params

        return "general", params

    def _extract_search_params(self, message: str) -> Dict:
        """Extract search parameters from message including sector detection"""
        params = {}
        message_lower = message.lower()

        # Check for Algerian Wilayas first
        for wilaya in ALGERIAN_WILAYAS:
            if wilaya in message_lower:
                # Normalize wilaya name
                params["location"] = wilaya.title()
                break

        # If no wilaya found, try general location patterns
        if "location" not in params:
            location_patterns = [
                r"in\s+([A-Za-z\s]+?)(?:\s+with|\s+for|\s*$|,|\.|!)",
                r"at\s+([A-Za-z\s]+?)(?:\s+with|\s+for|\s*$|,|\.|!)",
                r"à\s+([A-Za-z\s]+?)(?:\s+avec|\s+pour|\s*$|,|\.|!)",
                r"في\s+([A-Za-z\s\u0600-\u06FF]+?)(?:\s|$|,|\.|!)"
            ]
            for pattern in location_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    params["location"] = match.group(1).strip()
                    break

        # Detect job sector from keywords
        for sector_key, sector_keywords in JOB_SECTORS.items():
            for keyword in sector_keywords:
                if keyword.lower() in message_lower:
                    params["sector"] = sector_key
                    break
            if "sector" in params:
                break

        # Extract skills
        skill_keywords = ["python", "java", "javascript", "react", "node", "sql", "django", "fastapi", 
                         "machine learning", "ai", "data science", "devops", "aws", "docker", "kubernetes",
                         "php", "laravel", "vue", "angular", "typescript", "go", "rust", "c++", "c#", ".net",
                         "excel", "word", "comptabilité", "gestion", "marketing", "commercial", "vente",
                         "électricité", "mécanique", "plomberie", "soudure", "btp", "architecture"]
        found_skills = [skill for skill in skill_keywords if skill in message_lower]
        if found_skills:
            params["skills"] = found_skills

        # Extract contract type (including French/Arabic terms)
        if any(word in message_lower for word in ["internship", "stage", "intern", "تربص"]):
            params["contract_type"] = "internship"
        elif any(word in message_lower for word in ["full-time", "full time", "temps plein", "cdi", "دائم"]):
            params["contract_type"] = "full-time"
        elif any(word in message_lower for word in ["part-time", "part time", "temps partiel", "جزئي"]):
            params["contract_type"] = "part-time"
        elif any(word in message_lower for word in ["freelance", "remote", "عن بعد"]):
            params["contract_type"] = "freelance"
        elif any(word in message_lower for word in ["contract", "cdd", "عقد"]):
            params["contract_type"] = "contract"

        return params

    def _handle_job_search(self, params: Dict, db: Session, lang: str = 'fr') -> Dict[str, Any]:
        """Handle job search request with multilingual response"""
        query = db.query(Job).filter(Job.is_active == True)

        # Apply filters
        if "location" in params:
            query = query.filter(Job.location.ilike(f"%{params['location']}%"))

        if "skills" in params:
            for skill in params["skills"]:
                query = query.filter(Job.skills.ilike(f"%{skill}%"))

        if "contract_type" in params:
            query = query.filter(Job.contract_type == params["contract_type"])
        
        # Apply sector filter if specified
        if "sector" in params:
            sector_keywords = JOB_SECTORS.get(params["sector"], [])
            # Search by sector keywords in title, description
            if sector_keywords:
                sector_filter = or_(*[Job.title.ilike(f"%{kw}%") for kw in sector_keywords], 
                                    *[Job.description.ilike(f"%{kw}%") for kw in sector_keywords])
                query = query.filter(sector_filter)

        jobs = query.limit(10).all()

        no_results_messages = {
            "en": "I couldn't find any jobs matching your criteria. Try broadening your search or check all available jobs.",
            "fr": "Je n'ai pas trouvé d'emplois correspondant à vos critères. Essayez d'élargir votre recherche.",
            "ar": "لم أجد وظائف تتوافق مع معاييرك. حاول توسيع نطاق البحث."
        }

        if not jobs:
            return {
                "response": no_results_messages.get(lang, no_results_messages["fr"]),
                "jobs": [],
                "action": "search"
            }

        job_list = [
            {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "contract_type": job.contract_type,
                "skills": job.skills,
                "description": job.description,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "recruiter_id": job.recruiter_id,
                "is_active": job.is_active,
                "created_at": job.created_at.isoformat()
            }
            for job in jobs
        ]

        filter_desc = []
        if "location" in params:
            filter_desc.append(params['location'])
        if "skills" in params:
            filter_desc.append(', '.join(params['skills']))
        if "contract_type" in params:
            filter_desc.append(params['contract_type'])

        filter_text = " - ".join(filter_desc) if filter_desc else ""
        
        result_messages = {
            "en": f"I found {len(jobs)} job(s) {filter_text}. Here are the results:",
            "fr": f"J'ai trouvé {len(jobs)} emploi(s) {filter_text}. Voici les résultats:",
            "ar": f"وجدت {len(jobs)} وظيفة {filter_text}. إليك النتائج:"
        }
        
        return {
            "response": result_messages.get(lang, result_messages["fr"]),
            "jobs": job_list,
            "action": "search"
        }

    def _handle_apply(self, params: Dict, db: Session, user: Optional[User], lang: str = 'fr') -> Dict[str, Any]:
        """Handle job application request with multilingual response"""
        
        auth_required_messages = {
            "en": "You need to be logged in to apply for jobs. Please sign in or create an account.",
            "fr": "Vous devez être connecté pour postuler. Veuillez vous connecter ou créer un compte.",
            "ar": "يجب تسجيل الدخول للتقدم للوظائف. يرجى تسجيل الدخول أو إنشاء حساب."
        }
        
        if not user:
            return {
                "response": auth_required_messages.get(lang, auth_required_messages["fr"]),
                "action": "auth_required"
            }

        job_id = params.get("job_id")
        
        clarify_messages = {
            "en": "Please specify the job ID you want to apply for. For example: 'Apply for job #5'",
            "fr": "Veuillez préciser l'ID de l'emploi. Par exemple: 'Postuler pour l'emploi #5'",
            "ar": "يرجى تحديد رقم الوظيفة. مثال: 'تقدم للوظيفة #5'"
        }
        
        if not job_id:
            return {
                "response": clarify_messages.get(lang, clarify_messages["fr"]),
                "action": "clarify"
            }

        job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()
        
        not_found_messages = {
            "en": f"Job #{job_id} was not found or is no longer available.",
            "fr": f"L'emploi #{job_id} n'a pas été trouvé ou n'est plus disponible.",
            "ar": f"الوظيفة #{job_id} غير موجودة أو لم تعد متاحة."
        }
        
        if not job:
            return {
                "response": not_found_messages.get(lang, not_found_messages["fr"]),
                "action": "not_found"
            }

        # Check if already applied
        existing = db.query(Application).filter(
            Application.job_id == job_id,
            Application.candidate_id == user.id
        ).first()

        if existing:
            already_applied_messages = {
                "en": f"You have already applied for '{job.title}' at {job.company}. Your application status is: {existing.status}.",
                "fr": f"Vous avez déjà postulé pour '{job.title}' chez {job.company}. Statut: {existing.status}.",
                "ar": f"لقد تقدمت بالفعل لوظيفة '{job.title}' في {job.company}. الحالة: {existing.status}."
            }
            return {
                "response": already_applied_messages.get(lang, already_applied_messages["fr"]),
                "action": "already_applied"
            }

        # Create application
        application = Application(
            job_id=job_id,
            candidate_id=user.id,
            status=ApplicationStatus.PENDING.value
        )
        db.add(application)
        db.commit()

        success_messages = {
            "en": f"🎉 Successfully applied for '{job.title}' at {job.company}! Your application is now pending review.",
            "fr": f"🎉 Candidature envoyée pour '{job.title}' chez {job.company}! Votre candidature est en attente d'examen.",
            "ar": f"🎉 تم التقدم بنجاح لوظيفة '{job.title}' في {job.company}! طلبك قيد المراجعة."
        }

        return {
            "response": success_messages.get(lang, success_messages["fr"]),
            "action": "applied"
        }

    def _handle_my_applications(self, db: Session, user: Optional[User], lang: str = 'fr') -> Dict[str, Any]:
        """Handle request to view user's applications with multilingual response"""
        
        auth_required_messages = {
            "en": "You need to be logged in to view your applications. Please sign in.",
            "fr": "Vous devez être connecté pour voir vos candidatures. Veuillez vous connecter.",
            "ar": "يجب تسجيل الدخول لعرض طلباتك. يرجى تسجيل الدخول."
        }
        
        if not user:
            return {
                "response": auth_required_messages.get(lang, auth_required_messages["fr"]),
                "action": "auth_required"
            }

        applications = db.query(Application).filter(
            Application.candidate_id == user.id
        ).order_by(Application.created_at.desc()).all()

        no_applications_messages = {
            "en": "You haven't applied to any jobs yet. Search for jobs and apply using 'Apply for job #ID'.",
            "fr": "Vous n'avez pas encore postulé. Cherchez des emplois et postulez avec 'Postuler pour #ID'.",
            "ar": "لم تتقدم لأي وظيفة بعد. ابحث عن وظائف وتقدم باستخدام 'تقدم للوظيفة #ID'."
        }

        if not applications:
            return {
                "response": no_applications_messages.get(lang, no_applications_messages["fr"]),
                "action": "no_applications"
            }

        app_list = []
        for app in applications:
            job = db.query(Job).filter(Job.id == app.job_id).first()
            if job:
                app_list.append({
                    "id": app.id,
                    "job_title": job.title,
                    "company": job.company,
                    "status": app.status,
                    "applied_at": app.created_at.isoformat()
                })

        header_messages = {
            "en": f"You have {len(applications)} application(s):\n\n",
            "fr": f"Vous avez {len(applications)} candidature(s):\n\n",
            "ar": f"لديك {len(applications)} طلب(ات):\n\n"
        }
        
        response_text = header_messages.get(lang, header_messages["fr"])
        for app in app_list:
            status_emoji = {"pending": "⏳", "reviewed": "👀", "accepted": "✅", "rejected": "❌"}.get(app["status"], "📋")
            response_text += f"{status_emoji} {app['job_title']} @ {app['company']} - {app['status'].upper()}\n"

        return {
            "response": response_text,
            "action": "show_applications"
        }

    def _handle_help(self, lang: str = 'fr') -> Dict[str, Any]:
        """Handle help request with multilingual response"""
        
        help_messages = {
            "en": """I can help you with the following:

🔍 **Job Search:**
- "Find Python jobs in Algiers"
- "Show me internships in Oran"
- "Search for React developer positions"

📝 **Applications:**
- "Apply for job #5"
- "Show my applications"

🏛️ **ANEM Information:**
- "How to register with ANEM?"
- "What documents do I need?"
- "How to renew my registration?"
- "ANEM training programs"
- "Interview preparation tips"

💡 **Tips:**
- Search by skills, location (Wilaya), or contract type
- Login to apply and track applications
- Ask me anything about ANEM services!

How can I assist you today?""",

            "fr": """Je peux vous aider avec:

🔍 **Recherche d'emploi:**
- "Trouver des emplois Python à Alger"
- "Montre-moi des stages à Oran"
- "Chercher des postes développeur React"

📝 **Candidatures:**
- "Postuler pour l'emploi #5"
- "Mes candidatures"

🏛️ **Informations ANEM:**
- "Comment s'inscrire à l'ANEM?"
- "Quels documents faut-il?"
- "Renouvellement d'inscription"
- "Programmes de formation ANEM"
- "Conseils pour l'entretien"

💡 **Astuces:**
- Recherchez par compétences, Wilaya, ou type de contrat
- Connectez-vous pour postuler et suivre vos candidatures
- Posez-moi toute question sur les services ANEM!

Comment puis-je vous aider?""",

            "ar": """يمكنني مساعدتك في:

🔍 **البحث عن عمل:**
- "ابحث عن وظائف Python في الجزائر"
- "أرني تربصات في وهران"
- "ابحث عن وظائف مطور React"

📝 **الطلبات:**
- "تقدم للوظيفة #5"
- "طلباتي"

🏛️ **معلومات ANEM:**
- "كيفية التسجيل في ANEM؟"
- "ما هي الوثائق المطلوبة؟"
- "تجديد التسجيل"
- "برامج التكوين ANEM"
- "نصائح للمقابلة"

💡 **نصائح:**
- ابحث حسب المهارات، الولاية، أو نوع العقد
- سجل دخولك للتقدم ومتابعة طلباتك
- اسألني أي شيء عن خدمات ANEM!

كيف يمكنني مساعدتك؟"""
        }
        
        return {
            "response": help_messages.get(lang, help_messages["fr"]),
            "action": "help"
        }

    def _handle_anem_faq(self, params: Dict, lang: str = 'fr') -> Dict[str, Any]:
        """Handle ANEM FAQ questions with multilingual response"""
        responses = params.get("responses", {})
        # Use detected language, fallback to French then English
        response = responses.get(lang, responses.get("fr", responses.get("en", "")))
        
        return {
            "response": response,
            "action": "anem_faq"
        }

    def _handle_greeting(self, user: Optional[User], lang: str = 'fr') -> Dict[str, Any]:
        """Handle greeting with multilingual response"""
        
        if user:
            greetings_logged_in = {
                "en": f"Hello {user.full_name}! 👋 Welcome to Wassit Online. How can I help you today? You can search for jobs, apply, or ask me about ANEM services.",
                "fr": f"Bonjour {user.full_name}! 👋 Bienvenue sur Wassit Online. Comment puis-je vous aider aujourd'hui? Vous pouvez chercher des emplois, postuler, ou me poser des questions sur l'ANEM.",
                "ar": f"مرحباً {user.full_name}! 👋 أهلاً بك في وسيط أونلاين. كيف يمكنني مساعدتك اليوم؟ يمكنك البحث عن وظائف، التقدم، أو سؤالي عن خدمات ANEM."
            }
            return {
                "response": greetings_logged_in.get(lang, greetings_logged_in["fr"]),
                "action": "greeting"
            }
        
        greetings_guest = {
            "en": "Hello! 👋 Welcome to Wassit Online - Your ANEM assistant. I can help you find jobs, apply, and answer your questions about ANEM. What are you looking for today?",
            "fr": "Bonjour! 👋 Bienvenue sur Wassit Online - Votre assistant ANEM. Je peux vous aider à trouver des emplois, postuler, et répondre à vos questions sur l'ANEM. Que cherchez-vous aujourd'hui?",
            "ar": "مرحباً! 👋 أهلاً بك في وسيط أونلاين - مساعدك في ANEM. يمكنني مساعدتك في إيجاد وظائف، التقدم، والإجابة على أسئلتك حول ANEM. ماذا تبحث عنه اليوم؟"
        }
        
        return {
            "response": greetings_guest.get(lang, greetings_guest["fr"]),
            "action": "greeting"
        }

    def _handle_profile_update(self, params: Dict, db: Session, user: Optional[User], lang: str = 'fr') -> Dict[str, Any]:
        """Handle profile update requests"""
        auth_required_messages = {
            "en": "You need to be logged in to update your profile.",
            "fr": "Vous devez être connecté pour mettre à jour votre profil.",
            "ar": "يجب تسجيل الدخول لتحديث ملفك الشخصي."
        }
        
        if not user:
            return {
                "response": auth_required_messages.get(lang, auth_required_messages["fr"]),
                "action": "auth_required"
            }
        
        # Profile update guidance
        profile_messages = {
            "en": "To update your profile, go to your Profile page. You can add your education, experience, skills, and ANEM registration details there.",
            "fr": "Pour mettre à jour votre profil, allez sur votre page Profil. Vous pouvez y ajouter votre formation, expérience, compétences et détails d'inscription ANEM.",
            "ar": "لتحديث ملفك الشخصي، اذهب إلى صفحة الملف الشخصي. يمكنك إضافة تعليمك، خبرتك، مهاراتك وتفاصيل تسجيل ANEM هناك."
        }
        
        return {
            "response": profile_messages.get(lang, profile_messages["fr"]),
            "action": "profile_guide"
        }

    def _handle_general_query(self, message: str, db: Session, lang: str = 'fr') -> Dict[str, Any]:
        """Handle general queries using LLM (Groq/OpenAI) with NLP preprocessing"""
        
        # NLP preprocessing with spaCy (if available)
        entities = []
        keywords = []
        if self.nlp_fr and lang == 'fr':
            doc = self.nlp_fr(message)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            keywords = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
        
        # Get job context
        jobs = db.query(Job).filter(Job.is_active == True).limit(5).all()
        job_context = "\n".join([
            f"- {j.title} at {j.company} ({j.location}, {j.contract_type})"
            for j in jobs
        ]) if jobs else "No jobs currently available."
        
        lang_instruction = {
            "en": "Respond in English.",
            "fr": "Répondez en français.",
            "ar": "أجب باللغة العربية."
        }
        
        system_prompt = f"""You are Wassit, a helpful recruitment assistant for ANEM Algeria. {lang_instruction.get(lang, lang_instruction['fr'])}

Available jobs:
{job_context}

Extracted entities: {entities}
Keywords: {keywords}

Help users find jobs, answer questions about ANEM services, and provide career advice. Be concise and helpful."""

        # Try Groq LLM first (free tier)
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                return {
                    "response": response.choices[0].message.content,
                    "action": "llm_response",
                    "nlp_entities": entities,
                    "nlp_keywords": keywords
                }
            except Exception as e:
                pass
        
        # Try OpenAI as fallback
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=300
                )
                return {
                    "response": response.choices[0].message.content,
                    "action": "ai_response",
                    "nlp_entities": entities,
                    "nlp_keywords": keywords
                }
            except Exception as e:
                pass

        # Multilingual fallback responses
        fallback_messages = {
            "en": "I'm here to help you find jobs! Try asking me to:\n- Search for jobs (e.g., 'Find Python jobs')\n- Apply for a position (e.g., 'Apply for job #5')\n- View your applications\n- Ask about ANEM services\n\nWhat would you like to do?",
            "fr": "Je suis là pour vous aider à trouver un emploi! Essayez de me demander:\n- Chercher des emplois (ex: 'Trouver emplois Python')\n- Postuler (ex: 'Postuler pour #5')\n- Voir vos candidatures\n- Questions sur l'ANEM\n\nQue souhaitez-vous faire?",
            "ar": "أنا هنا لمساعدتك في إيجاد عمل! جرب أن تطلب مني:\n- البحث عن وظائف (مثال: 'ابحث عن وظائف Python')\n- التقدم لوظيفة (مثال: 'تقدم للوظيفة #5')\n- عرض طلباتك\n- أسئلة حول ANEM\n\nماذا تريد أن تفعل؟"
        }
        
        return {
            "response": fallback_messages.get(lang, fallback_messages["fr"]),
            "action": "fallback"
        }


# Singleton instance
ai_service = AIService()
