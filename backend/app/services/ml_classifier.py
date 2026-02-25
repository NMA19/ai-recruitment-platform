"""
ML-based Intent Classifier for Chatbot
Uses sklearn for intent classification with TF-IDF + Logistic Regression
Trained on multilingual data (French, Arabic, English)
"""

import os
import json
import pickle
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# ML imports
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.svm import SVC
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import classification_report, accuracy_score
    from sklearn.pipeline import Pipeline
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Get the directory where this file is located
BASE_DIR = Path(__file__).parent


class IntentClassifier:
    """
    Machine Learning-based Intent Classifier
    Uses TF-IDF vectorization + Logistic Regression for multilingual intent detection
    """
    
    # Intent labels
    INTENTS = [
        "search_jobs",      # Job search queries
        "apply_job",        # Apply for a job
        "my_applications",  # View applications
        "anem_faq",         # ANEM information questions
        "greeting",         # Hello, hi, etc.
        "help",             # Help/commands
        "profile_update",   # Update profile/CV
        "general"           # General queries
    ]
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.is_trained = False
        self.model_path = BASE_DIR / "models" / "intent_classifier.pkl"
        self.vectorizer_path = BASE_DIR / "models" / "tfidf_vectorizer.pkl"
        self.training_data_path = BASE_DIR / "data" / "training_data.json"
        
        # Create directories
        (BASE_DIR / "models").mkdir(exist_ok=True)
        (BASE_DIR / "data").mkdir(exist_ok=True)
        
        # Try to load existing model
        self._load_model()
        
        # If no model exists, train with default data
        if not self.is_trained:
            self._train_with_default_data()
    
    def _get_training_data(self) -> Tuple[List[str], List[str]]:
        """
        Get training data for intent classification
        Multilingual: French, Arabic (Darja), English
        """
        training_data = {
            "search_jobs": [
                # French
                "chercher emploi", "trouver travail", "recherche emploi",
                "emplois à alger", "jobs en algérie", "postes disponibles",
                "cherche stage", "offres d'emploi", "trouver un poste",
                "chercher travail informatique", "emploi développeur",
                "stage à oran", "emplois constantine", "jobs bejaia",
                "chercher un emploi dans le secteur", "postes ouverts",
                "offres de travail", "recherche de stage", "emploi temps plein",
                "travail à distance", "télétravail algérie", "job remote",
                "emploi marketing", "travail commercial", "poste comptable",
                "cherche emploi btp", "jobs santé", "emploi enseignement",
                "trouve moi un travail", "je cherche un emploi",
                "montre moi les offres", "liste des emplois",
                "quels emplois disponibles", "y a-t-il des postes",
                "emploi sans expérience", "premier emploi", "job étudiant",
                # English
                "find jobs", "search jobs", "looking for work",
                "jobs in algiers", "find employment", "job openings",
                "search for internship", "find positions", "job search",
                "looking for developer job", "find python jobs",
                "internships in oran", "jobs available", "show me jobs",
                "find work in constantine", "search for opportunities",
                "remote jobs", "full time positions", "part time work",
                "entry level jobs", "no experience required", "fresh graduate jobs",
                "it jobs", "developer positions", "engineering jobs",
                # Arabic/Darja
                "نلقى خدمة", "ابحث عن عمل", "خدمة في الجزائر",
                "وظائف متاحة", "فرص عمل", "نحوس على خدمة",
                "ستاج في وهران", "عمل في قسنطينة", "خدمة في الجزائر العاصمة",
                "نبحث على تربص", "فرصة عمل", "عروض شغل",
                "نلقى خدمة بلا خبرة", "أول خدمة", "شغل طالب",
            ],
            
            "apply_job": [
                # French
                "postuler", "candidater", "soumettre candidature",
                "postuler pour emploi", "envoyer candidature",
                "postuler pour le poste", "je veux postuler",
                "comment postuler", "postuler emploi 5",
                "candidater pour ce poste", "envoyer ma candidature",
                "postuler pour offre", "je candidate", "soumettre cv",
                "postuler stage", "candidature spontanée",
                # English
                "apply for job", "submit application", "apply to position",
                "apply job 5", "submit my cv", "apply for internship",
                "how to apply", "i want to apply", "apply to this job",
                "send my application", "apply for this position",
                "apply now", "submit resume", "application submission",
                # Arabic/Darja
                "نتقدم للوظيفة", "أرسل طلب", "بغيت نتقدم",
                "كيفاش نتقدم", "نسجل في الوظيفة", "ارسل cv",
                "التقدم للعمل", "تقديم طلب", "ارسال السيرة الذاتية",
            ],
            
            "my_applications": [
                # French
                "mes candidatures", "mes postulations", "voir mes candidatures",
                "statut candidature", "où en est ma candidature",
                "liste mes candidatures", "mes demandes", "suivre candidature",
                "état de ma candidature", "mes applications",
                "historique candidatures", "candidatures en cours",
                # English
                "my applications", "show my applications", "application status",
                "view applications", "list my applications", "track applications",
                "check application status", "my submitted applications",
                "applications history", "pending applications",
                # Arabic/Darja
                "طلباتي", "شوف طلباتي", "وين وصلت طلباتي",
                "حالة طلبي", "تتبع الطلبات", "قائمة طلباتي",
                "الطلبات المقدمة", "حالة الطلب",
            ],
            
            "anem_faq": [
                # French - Registration
                "inscription anem", "comment s'inscrire anem", "créer compte anem",
                "enregistrement wassit", "inscription en ligne",
                "ouvrir compte anem", "première inscription",
                # French - Documents
                "documents nécessaires", "papiers requis", "dossier anem",
                "quels documents", "pièces justificatives", "attestation",
                "certificat résidence", "carte nationale", "diplôme",
                # French - Renewal
                "renouveler inscription", "renouvellement anem",
                "mettre à jour inscription", "prolonger inscription",
                # French - Programs
                "formation anem", "daip", "cfsi", "cta",
                "contrat aidé", "programme insertion",
                "stage professionnel", "formation professionnelle",
                # French - Contact
                "contact anem", "adresse agence", "numéro téléphone",
                "agence locale", "où se trouve anem",
                # French - Interview
                "préparer entretien", "conseils entretien", "questions entretien",
                "réussir entretien", "entretien embauche",
                # English
                "anem registration", "how to register anem", "create anem account",
                "required documents", "what papers needed", "documents for anem",
                "renew registration", "anem renewal", "update registration",
                "anem training", "professional training", "daip program",
                "contact anem", "anem address", "local agency",
                "interview preparation", "interview tips",
                # Arabic/Darja
                "تسجيل anem", "كيفاش نسجل في anem", "فتح حساب anem",
                "الوثائق المطلوبة", "أوراق التسجيل", "شهادة الإقامة",
                "تجديد التسجيل", "تحديث الملف", "تمديد التسجيل",
                "تكوين anem", "برامج التكوين", "عقد ادماج",
                "عنوان الوكالة", "رقم الهاتف", "اتصل بـ anem",
                "نصائح المقابلة", "أسئلة المقابلة",
            ],
            
            "greeting": [
                # French
                "bonjour", "salut", "bonsoir", "hello", "coucou",
                "bonne journée", "salam", "hey", "hi",
                "bonjour à tous", "salut à toi", "cc",
                # English
                "hello", "hi", "hey", "good morning", "good afternoon",
                "good evening", "hi there", "hello there", "greetings",
                "what's up", "howdy",
                # Arabic/Darja
                "مرحبا", "السلام عليكم", "صباح الخير", "مساء الخير",
                "أهلا", "سلام", "وش راك", "كيفك", "لاباس",
            ],
            
            "help": [
                # French
                "aide", "besoin d'aide", "comment ça marche",
                "que peux-tu faire", "commandes disponibles",
                "qu'est-ce que tu peux faire", "fonctionnalités",
                "help", "aidez moi", "j'ai besoin d'aide",
                "comment utiliser", "mode d'emploi", "guide",
                "assistance", "support", "tutoriel",
                # English
                "help", "help me", "what can you do", "how does this work",
                "available commands", "features", "capabilities",
                "i need help", "assist me", "support",
                "how to use", "instructions", "guide",
                # Arabic/Darja
                "مساعدة", "ساعدني", "كيفاش نستعمل", "شنو تقدر دير",
                "واش تقدر تدير", "الأوامر المتاحة", "دليل الاستخدام",
            ],
            
            "profile_update": [
                # French
                "modifier profil", "mettre à jour cv", "changer informations",
                "ajouter compétences", "modifier cv", "ajouter formation",
                "ajouter expérience", "mettre à jour profil",
                "éditer mon profil", "changer mon cv",
                "ajouter diplôme", "modifier mes informations",
                # English
                "update profile", "edit cv", "change information",
                "add skills", "modify resume", "add education",
                "add experience", "update my profile", "edit my info",
                "change my details", "add certification",
                # Arabic/Darja
                "تحديث الملف الشخصي", "تعديل السيرة الذاتية", "إضافة مهارات",
                "تعديل المعلومات", "إضافة خبرة", "إضافة شهادة",
                "بدل المعلومات", "زيد المهارات",
            ],
            
            "general": [
                # French
                "merci", "ok", "d'accord", "je comprends", "super",
                "parfait", "bien", "c'est noté", "entendu",
                "quoi de neuf", "comment vas-tu", "ça va",
                "au revoir", "à bientôt", "bye",
                "autre chose", "différent", "autre question",
                # English
                "thanks", "thank you", "ok", "okay", "understood",
                "got it", "great", "perfect", "good", "fine",
                "how are you", "what's new", "anything else",
                "bye", "goodbye", "see you", "later",
                "something else", "different question", "another topic",
                # Arabic/Darja
                "شكرا", "مليح", "فهمت", "واه", "باي",
                "بصحتك", "كيما قلت", "تمام", "حسنا",
                "وداعا", "الى اللقاء", "نشوفك",
            ],
        }
        
        # Flatten data
        texts = []
        labels = []
        
        for intent, examples in training_data.items():
            for example in examples:
                texts.append(example.lower().strip())
                labels.append(intent)
        
        return texts, labels
    
    def _train_with_default_data(self):
        """Train the model with default training data"""
        if not SKLEARN_AVAILABLE:
            print("sklearn not available, using rule-based fallback")
            return
        
        texts, labels = self._get_training_data()
        self.train(texts, labels)
    
    def train(self, texts: List[str], labels: List[str], save: bool = True) -> Dict:
        """
        Train the intent classifier
        
        Args:
            texts: List of training text examples
            labels: List of corresponding intent labels
            save: Whether to save the model after training
            
        Returns:
            Dictionary with training metrics
        """
        if not SKLEARN_AVAILABLE:
            return {"error": "sklearn not available"}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Create TF-IDF vectorizer with n-grams for better feature extraction
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),      # Use unigrams, bigrams, trigrams
            max_features=5000,        # Limit vocabulary size
            min_df=1,                 # Minimum document frequency
            sublinear_tf=True,        # Apply sublinear tf scaling
            strip_accents='unicode',  # Handle accents
            analyzer='word',
            token_pattern=r'\w{1,}',  # Match words of length >= 1
        )
        
        # Transform training data
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf = self.vectorizer.transform(X_test)
        
        # Train Logistic Regression classifier
        self.model = LogisticRegression(
            max_iter=1000,
            multi_class='multinomial',
            solver='lbfgs',
            C=10.0,                   # Regularization strength
            class_weight='balanced'   # Handle class imbalance
        )
        
        self.model.fit(X_train_tfidf, y_train)
        self.is_trained = True
        
        # Evaluate
        y_pred = self.model.predict(X_test_tfidf)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.model, 
            self.vectorizer.transform(texts), 
            labels, 
            cv=5
        )
        
        metrics = {
            "accuracy": accuracy,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std(),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "intents": list(set(labels))
        }
        
        # Save model
        if save:
            self._save_model()
            self._save_training_data(texts, labels)
        
        print(f"Intent Classifier trained - Accuracy: {accuracy:.2%}, CV: {cv_scores.mean():.2%}")
        
        return metrics
    
    def predict(self, text: str) -> Tuple[str, float]:
        """
        Predict intent for a given text
        
        Returns:
            Tuple of (predicted_intent, confidence_score)
        """
        if not self.is_trained or not SKLEARN_AVAILABLE:
            return self._rule_based_predict(text)
        
        try:
            text_tfidf = self.vectorizer.transform([text.lower().strip()])
            
            # Get prediction and probability
            prediction = self.model.predict(text_tfidf)[0]
            probabilities = self.model.predict_proba(text_tfidf)[0]
            confidence = max(probabilities)
            
            # If confidence is low, fall back to rule-based
            if confidence < 0.3:
                rule_prediction, _ = self._rule_based_predict(text)
                return rule_prediction, confidence
            
            return prediction, confidence
            
        except Exception as e:
            print(f"ML prediction error: {e}")
            return self._rule_based_predict(text)
    
    def predict_with_details(self, text: str) -> Dict:
        """
        Get detailed prediction with all intent probabilities
        """
        if not self.is_trained or not SKLEARN_AVAILABLE:
            intent, conf = self._rule_based_predict(text)
            return {
                "intent": intent,
                "confidence": conf,
                "probabilities": {intent: conf},
                "method": "rule_based"
            }
        
        try:
            text_tfidf = self.vectorizer.transform([text.lower().strip()])
            
            prediction = self.model.predict(text_tfidf)[0]
            probabilities = self.model.predict_proba(text_tfidf)[0]
            
            # Map probabilities to intent names
            prob_dict = {
                intent: float(prob) 
                for intent, prob in zip(self.model.classes_, probabilities)
            }
            
            return {
                "intent": prediction,
                "confidence": float(max(probabilities)),
                "probabilities": prob_dict,
                "method": "ml_classifier"
            }
            
        except Exception as e:
            intent, conf = self._rule_based_predict(text)
            return {
                "intent": intent,
                "confidence": conf,
                "probabilities": {intent: conf},
                "method": "rule_based",
                "error": str(e)
            }
    
    def _rule_based_predict(self, text: str) -> Tuple[str, float]:
        """Fallback rule-based intent detection"""
        text_lower = text.lower().strip()
        
        # Greeting patterns
        greetings = ["hello", "hi", "hey", "bonjour", "salut", "مرحبا", "السلام", "سلام"]
        if any(text_lower.startswith(g) or text_lower == g for g in greetings):
            return "greeting", 0.9
        
        # Help patterns
        help_words = ["help", "aide", "مساعدة", "what can you do", "que peux-tu"]
        if any(w in text_lower for w in help_words):
            return "help", 0.85
        
        # Apply patterns
        if any(w in text_lower for w in ["apply", "postuler", "candidater", "تقدم", "نتقدم"]):
            return "apply_job", 0.85
        
        # Applications status
        if any(w in text_lower for w in ["my applications", "mes candidatures", "طلباتي"]):
            return "my_applications", 0.9
        
        # ANEM FAQ
        anem_words = ["anem", "inscription", "documents", "renouveler", "formation", "daip", "تسجيل", "وثائق"]
        if any(w in text_lower for w in anem_words):
            return "anem_faq", 0.8
        
        # Profile update
        profile_words = ["profil", "cv", "profile", "update", "modifier", "تحديث", "سيرة"]
        if any(w in text_lower for w in profile_words):
            return "profile_update", 0.75
        
        # Job search (broad patterns)
        search_words = ["find", "search", "job", "work", "emploi", "travail", "cherche", "وظيفة", "عمل", "خدمة"]
        if any(w in text_lower for w in search_words):
            return "search_jobs", 0.7
        
        return "general", 0.5
    
    def _save_model(self):
        """Save trained model and vectorizer"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            
            with open(self.vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizer, f)
                
            print(f"Model saved to {self.model_path}")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def _load_model(self):
        """Load trained model and vectorizer"""
        try:
            if self.model_path.exists() and self.vectorizer_path.exists():
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                
                self.is_trained = True
                print("ML Intent Classifier loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.is_trained = False
    
    def _save_training_data(self, texts: List[str], labels: List[str]):
        """Save training data for future reference"""
        try:
            data = [{"text": t, "intent": l} for t, l in zip(texts, labels)]
            with open(self.training_data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving training data: {e}")
    
    def add_training_example(self, text: str, intent: str):
        """Add a new training example and retrain"""
        if not self.training_data_path.exists():
            texts, labels = self._get_training_data()
        else:
            try:
                with open(self.training_data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                texts = [d["text"] for d in data]
                labels = [d["intent"] for d in data]
            except:
                texts, labels = self._get_training_data()
        
        texts.append(text.lower().strip())
        labels.append(intent)
        
        self.train(texts, labels)
    
    def get_model_info(self) -> Dict:
        """Get information about the current model"""
        return {
            "is_trained": self.is_trained,
            "sklearn_available": SKLEARN_AVAILABLE,
            "intents": self.INTENTS,
            "model_type": "LogisticRegression + TF-IDF",
            "model_path": str(self.model_path),
            "vectorizer_path": str(self.vectorizer_path)
        }


# Singleton instance
intent_classifier = IntentClassifier()
