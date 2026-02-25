"""
Candidate Ranking Service for Recruiters
ML-based automatic ranking of job applications
Uses TF-IDF similarity and weighted scoring
"""

import re
import json
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@dataclass
class RankingWeights:
    """Configurable weights for candidate scoring"""
    skills_match: float = 0.35        # Skills match score weight
    experience_match: float = 0.25    # Experience relevance weight
    education_match: float = 0.20     # Education relevance weight
    location_match: float = 0.10      # Location proximity weight
    recency: float = 0.10             # Application recency weight


class CandidateRankingService:
    """
    ML-based Candidate Ranking System
    
    Features:
    - TF-IDF based skill matching
    - Weighted multi-criteria scoring
    - Automatic application sorting
    - Configurable ranking weights
    """
    
    def __init__(self, weights: Optional[RankingWeights] = None):
        self.weights = weights or RankingWeights()
        
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words=None,  # Keep all words for multilingual
                max_features=1000
            )
    
    def rank_candidates(
        self,
        job: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        top_n: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank candidates for a job posting
        
        Args:
            job: Job posting dict with title, description, skills, location
            candidates: List of candidate dicts with profile info
            top_n: Return only top N candidates (None for all)
            
        Returns:
            Sorted list of candidates with scores
        """
        if not candidates:
            return []
        
        scored_candidates = []
        
        for candidate in candidates:
            score_details = self._calculate_score(job, candidate)
            candidate_with_score = {
                **candidate,
                "ranking_score": score_details["total_score"],
                "score_breakdown": score_details
            }
            scored_candidates.append(candidate_with_score)
        
        # Sort by total score (descending)
        scored_candidates.sort(key=lambda x: x["ranking_score"], reverse=True)
        
        if top_n:
            return scored_candidates[:top_n]
        
        return scored_candidates
    
    def _calculate_score(self, job: Dict, candidate: Dict) -> Dict[str, float]:
        """Calculate comprehensive matching score"""
        
        scores = {
            "skills_score": self._calculate_skills_score(job, candidate),
            "experience_score": self._calculate_experience_score(job, candidate),
            "education_score": self._calculate_education_score(job, candidate),
            "location_score": self._calculate_location_score(job, candidate),
            "recency_score": self._calculate_recency_score(candidate)
        }
        
        # Weighted total
        total = (
            scores["skills_score"] * self.weights.skills_match +
            scores["experience_score"] * self.weights.experience_match +
            scores["education_score"] * self.weights.education_match +
            scores["location_score"] * self.weights.location_match +
            scores["recency_score"] * self.weights.recency
        )
        
        scores["total_score"] = round(total * 100, 2)  # Convert to percentage
        
        return scores
    
    def _calculate_skills_score(self, job: Dict, candidate: Dict) -> float:
        """Calculate skill match score using TF-IDF similarity"""
        
        job_skills = self._extract_skills_text(job.get("skills", ""), job.get("description", ""))
        candidate_skills = self._extract_skills_text(
            candidate.get("skills", ""),
            candidate.get("experience", "")
        )
        
        if not job_skills or not candidate_skills:
            return 0.0
        
        if SKLEARN_AVAILABLE:
            try:
                # Use TF-IDF cosine similarity
                tfidf_matrix = self.vectorizer.fit_transform([job_skills, candidate_skills])
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return float(similarity)
            except Exception:
                pass
        
        # Fallback: Simple keyword matching
        return self._simple_keyword_match(job_skills, candidate_skills)
    
    def _calculate_experience_score(self, job: Dict, candidate: Dict) -> float:
        """Calculate experience relevance score"""
        
        # Parse candidate experience (JSON or text)
        candidate_exp = candidate.get("experience", "")
        if isinstance(candidate_exp, str):
            try:
                candidate_exp = json.loads(candidate_exp) if candidate_exp.startswith("[") else []
            except:
                candidate_exp = []
        
        # Extract years of experience
        total_years = 0
        relevance_score = 0
        
        job_keywords = self._extract_keywords(
            f"{job.get('title', '')} {job.get('description', '')} {job.get('skills', '')}"
        )
        
        for exp in candidate_exp:
            if isinstance(exp, dict):
                # Calculate duration
                start = exp.get("start_date", "")
                end = exp.get("end_date", "present")
                years = self._calculate_duration_years(start, end)
                total_years += years
                
                # Check relevance
                exp_text = f"{exp.get('title', '')} {exp.get('description', '')}"
                exp_keywords = self._extract_keywords(exp_text)
                
                # Calculate overlap
                if job_keywords and exp_keywords:
                    overlap = len(job_keywords & exp_keywords) / len(job_keywords)
                    relevance_score += overlap * years
        
        # Normalize score (0-1)
        if total_years > 0:
            relevance_ratio = relevance_score / total_years
            experience_factor = min(total_years / 5, 1.0)  # Cap at 5 years
            return (relevance_ratio * 0.6 + experience_factor * 0.4)
        
        return 0.0
    
    def _calculate_education_score(self, job: Dict, candidate: Dict) -> float:
        """Calculate education relevance score"""
        
        candidate_edu = candidate.get("education", "")
        if isinstance(candidate_edu, str):
            try:
                candidate_edu = json.loads(candidate_edu) if candidate_edu.startswith("[") else []
            except:
                candidate_edu = []
        
        if not candidate_edu:
            return 0.2  # Base score if no education listed
        
        job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
        
        # Education level scoring
        level_scores = {
            "doctorat": 1.0, "phd": 1.0,
            "master": 0.9, "magistère": 0.9, "ingénieur": 0.9,
            "licence": 0.7, "bachelor": 0.7,
            "bts": 0.5, "technicien": 0.5,
            "bac": 0.3, "baccalauréat": 0.3
        }
        
        max_level_score = 0.0
        relevance_score = 0.0
        
        for edu in candidate_edu:
            if isinstance(edu, dict):
                degree = edu.get("degree", "").lower()
                field = edu.get("field", "").lower()
                
                # Level score
                for level, score in level_scores.items():
                    if level in degree:
                        max_level_score = max(max_level_score, score)
                        break
                
                # Field relevance
                if field and field in job_text:
                    relevance_score = max(relevance_score, 1.0)
                elif field:
                    # Partial match
                    field_words = set(field.split())
                    job_words = set(job_text.split())
                    overlap = len(field_words & job_words) / max(len(field_words), 1)
                    relevance_score = max(relevance_score, overlap)
        
        return (max_level_score * 0.5 + relevance_score * 0.5)
    
    def _calculate_location_score(self, job: Dict, candidate: Dict) -> float:
        """Calculate location match score"""
        
        job_location = job.get("location", "").lower()
        candidate_location = candidate.get("wilaya", "").lower()
        
        if not job_location or not candidate_location:
            return 0.5  # Neutral if unknown
        
        # Exact match
        if candidate_location in job_location or job_location in candidate_location:
            return 1.0
        
        # Same region bonus (simplified)
        # Algerian region groupings
        regions = {
            "centre": ["alger", "blida", "tipaza", "boumerdes", "médéa", "bouira"],
            "est": ["constantine", "annaba", "sétif", "batna", "jijel", "béjaïa", "skikda", "guelma"],
            "ouest": ["oran", "tlemcen", "mostaganem", "mascara", "sidi bel abbès", "ain temouchent"],
            "sud": ["ouargla", "ghardaia", "biskra", "bechar", "adrar", "tamanrasset"]
        }
        
        job_region = None
        candidate_region = None
        
        for region, wilayas in regions.items():
            if any(w in job_location for w in wilayas):
                job_region = region
            if any(w in candidate_location for w in wilayas):
                candidate_region = region
        
        if job_region and candidate_region and job_region == candidate_region:
            return 0.7  # Same region
        
        return 0.3  # Different region
    
    def _calculate_recency_score(self, candidate: Dict) -> float:
        """Score based on application recency"""
        
        applied_at = candidate.get("applied_at") or candidate.get("created_at")
        
        if not applied_at:
            return 0.5
        
        try:
            if isinstance(applied_at, str):
                applied_at = datetime.fromisoformat(applied_at.replace("Z", "+00:00"))
            
            days_ago = (datetime.now(applied_at.tzinfo) - applied_at).days
            
            # Recent applications score higher
            if days_ago <= 7:
                return 1.0
            elif days_ago <= 14:
                return 0.8
            elif days_ago <= 30:
                return 0.6
            elif days_ago <= 60:
                return 0.4
            else:
                return 0.2
        except:
            return 0.5
    
    def _extract_skills_text(self, skills: str, additional_text: str = "") -> str:
        """Extract and normalize skills text"""
        
        text = f"{skills} {additional_text}".lower()
        
        # Clean and normalize
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_keywords(self, text: str) -> set:
        """Extract keywords from text"""
        
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        
        # Filter stop words (basic)
        stop_words = {'le', 'la', 'les', 'de', 'du', 'des', 'et', 'en', 'un', 'une',
                      'the', 'a', 'an', 'and', 'or', 'for', 'to', 'in', 'of', 'with'}
        
        return {w for w in words if len(w) > 2 and w not in stop_words}
    
    def _calculate_duration_years(self, start: str, end: str) -> float:
        """Calculate duration in years between two dates"""
        
        try:
            start_year = int(start[:4]) if start else datetime.now().year
            
            if end.lower() in ["present", "current", "actuel", "maintenant", ""]:
                end_year = datetime.now().year
            else:
                end_year = int(end[:4])
            
            return max(0, end_year - start_year)
        except:
            return 0
    
    def _simple_keyword_match(self, text1: str, text2: str) -> float:
        """Simple keyword matching fallback"""
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def get_ranking_explanation(self, score_breakdown: Dict) -> Dict[str, str]:
        """Generate human-readable explanation of ranking"""
        
        explanations = {
            "fr": {},
            "en": {},
            "ar": {}
        }
        
        # Skills
        skills_pct = round(score_breakdown.get("skills_score", 0) * 100)
        explanations["fr"]["skills"] = f"Correspondance compétences: {skills_pct}%"
        explanations["en"]["skills"] = f"Skills match: {skills_pct}%"
        explanations["ar"]["skills"] = f"تطابق المهارات: {skills_pct}%"
        
        # Experience
        exp_pct = round(score_breakdown.get("experience_score", 0) * 100)
        explanations["fr"]["experience"] = f"Pertinence expérience: {exp_pct}%"
        explanations["en"]["experience"] = f"Experience relevance: {exp_pct}%"
        explanations["ar"]["experience"] = f"ملاءمة الخبرة: {exp_pct}%"
        
        # Education
        edu_pct = round(score_breakdown.get("education_score", 0) * 100)
        explanations["fr"]["education"] = f"Pertinence formation: {edu_pct}%"
        explanations["en"]["education"] = f"Education relevance: {edu_pct}%"
        explanations["ar"]["education"] = f"ملاءمة التعليم: {edu_pct}%"
        
        # Location
        loc_pct = round(score_breakdown.get("location_score", 0) * 100)
        explanations["fr"]["location"] = f"Proximité géographique: {loc_pct}%"
        explanations["en"]["location"] = f"Location proximity: {loc_pct}%"
        explanations["ar"]["location"] = f"القرب الجغرافي: {loc_pct}%"
        
        # Total
        total = score_breakdown.get("total_score", 0)
        explanations["fr"]["total"] = f"Score global: {total}%"
        explanations["en"]["total"] = f"Overall score: {total}%"
        explanations["ar"]["total"] = f"النتيجة الإجمالية: {total}%"
        
        return explanations
    
    def suggest_improvements(self, job: Dict, candidate: Dict, lang: str = "fr") -> List[str]:
        """Suggest improvements for candidate profile"""
        
        suggestions = {
            "fr": [],
            "en": [],
            "ar": []
        }
        
        score_details = self._calculate_score(job, candidate)
        
        # Skills suggestions
        if score_details["skills_score"] < 0.5:
            job_skills = set(job.get("skills", "").lower().split(","))
            candidate_skills = set(candidate.get("skills", "").lower().split(","))
            missing = job_skills - candidate_skills
            
            if missing:
                missing_list = ", ".join(list(missing)[:3])
                suggestions["fr"].append(f"Ajouter les compétences: {missing_list}")
                suggestions["en"].append(f"Add skills: {missing_list}")
                suggestions["ar"].append(f"أضف المهارات: {missing_list}")
        
        # Experience suggestions
        if score_details["experience_score"] < 0.3:
            suggestions["fr"].append("Détaillez davantage votre expérience professionnelle")
            suggestions["en"].append("Provide more details about your work experience")
            suggestions["ar"].append("قدم مزيداً من التفاصيل عن خبرتك العملية")
        
        # Education suggestions
        if score_details["education_score"] < 0.5:
            suggestions["fr"].append("Ajoutez vos formations et certifications")
            suggestions["en"].append("Add your education and certifications")
            suggestions["ar"].append("أضف شهاداتك ومؤهلاتك التعليمية")
        
        return suggestions.get(lang, suggestions["fr"])


# Singleton instance
ranking_service = CandidateRankingService()
