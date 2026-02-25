"""
Chatbot Analytics Service
Tracks and evaluates chatbot performance metrics
Supports PFE requirement #7: Chatbot performance evaluation
"""

import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from pathlib import Path
from collections import defaultdict
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import func


class InteractionType(str, Enum):
    """Types of chatbot interactions"""
    JOB_SEARCH = "job_search"
    APPLICATION = "application"
    FAQ = "faq"
    GREETING = "greeting"
    HELP = "help"
    GENERAL = "general"
    ERROR = "error"


@dataclass
class InteractionMetric:
    """Single interaction metric"""
    timestamp: str
    user_id: Optional[int]
    session_id: Optional[str]
    interaction_type: str
    intent_detected: str
    confidence_score: float
    response_time_ms: float
    user_satisfied: Optional[bool] = None
    language: str = "fr"
    message_length: int = 0
    response_length: int = 0
    jobs_returned: int = 0
    action_completed: bool = False


@dataclass 
class PerformanceMetrics:
    """Aggregated performance metrics"""
    total_interactions: int = 0
    successful_interactions: int = 0
    failed_interactions: int = 0
    
    # Response metrics
    avg_response_time_ms: float = 0.0
    min_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    
    # Intent metrics
    intent_accuracy: float = 0.0
    avg_confidence_score: float = 0.0
    
    # User satisfaction
    satisfaction_rate: float = 0.0
    feedback_count: int = 0
    
    # Usage patterns
    interactions_by_type: Dict[str, int] = field(default_factory=dict)
    interactions_by_language: Dict[str, int] = field(default_factory=dict)
    interactions_by_hour: Dict[int, int] = field(default_factory=dict)
    
    # Job search metrics
    total_job_searches: int = 0
    avg_jobs_per_search: float = 0.0
    search_to_apply_rate: float = 0.0
    
    # Application metrics
    total_applications: int = 0
    application_success_rate: float = 0.0
    
    # Period
    period_start: str = ""
    period_end: str = ""


class ChatbotAnalytics:
    """
    Analytics service for tracking chatbot performance
    
    Metrics tracked:
    - Response time (precision)
    - User satisfaction rate
    - Intent detection accuracy
    - Search to application conversion
    - Usage patterns by language/time
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path(__file__).parent / "data" / "analytics.json"
        self.storage_path.parent.mkdir(exist_ok=True)
        
        self.interactions: List[InteractionMetric] = []
        self.feedback: Dict[str, bool] = {}  # message_id -> satisfied
        
        self._load_data()
    
    def record_interaction(
        self,
        user_id: Optional[int],
        session_id: Optional[str],
        message: str,
        response: str,
        intent: str,
        confidence: float,
        response_time_ms: float,
        language: str = "fr",
        jobs_returned: int = 0,
        action_completed: bool = False
    ) -> InteractionMetric:
        """Record a single chatbot interaction"""
        
        # Determine interaction type
        interaction_type = self._categorize_interaction(intent)
        
        metric = InteractionMetric(
            timestamp=datetime.utcnow().isoformat(),
            user_id=user_id,
            session_id=session_id,
            interaction_type=interaction_type,
            intent_detected=intent,
            confidence_score=confidence,
            response_time_ms=response_time_ms,
            language=language,
            message_length=len(message),
            response_length=len(response),
            jobs_returned=jobs_returned,
            action_completed=action_completed
        )
        
        self.interactions.append(metric)
        self._save_data()
        
        return metric
    
    def record_feedback(
        self,
        interaction_timestamp: str,
        satisfied: bool,
        feedback_text: Optional[str] = None
    ):
        """Record user feedback for an interaction"""
        
        self.feedback[interaction_timestamp] = satisfied
        
        # Update corresponding interaction
        for interaction in self.interactions:
            if interaction.timestamp == interaction_timestamp:
                interaction.user_satisfied = satisfied
                break
        
        self._save_data()
    
    def get_metrics(
        self,
        period_days: int = 30,
        user_id: Optional[int] = None
    ) -> PerformanceMetrics:
        """Calculate aggregated performance metrics"""
        
        # Filter by period
        cutoff = datetime.utcnow() - timedelta(days=period_days)
        cutoff_str = cutoff.isoformat()
        
        filtered = [
            i for i in self.interactions 
            if i.timestamp >= cutoff_str
        ]
        
        # Filter by user if specified
        if user_id:
            filtered = [i for i in filtered if i.user_id == user_id]
        
        if not filtered:
            return PerformanceMetrics(
                period_start=cutoff_str,
                period_end=datetime.utcnow().isoformat()
            )
        
        # Calculate metrics
        metrics = PerformanceMetrics()
        metrics.total_interactions = len(filtered)
        metrics.period_start = cutoff_str
        metrics.period_end = datetime.utcnow().isoformat()
        
        # Response time stats
        response_times = [i.response_time_ms for i in filtered]
        metrics.avg_response_time_ms = sum(response_times) / len(response_times)
        metrics.min_response_time_ms = min(response_times)
        metrics.max_response_time_ms = max(response_times)
        
        # Confidence/accuracy
        confidences = [i.confidence_score for i in filtered]
        metrics.avg_confidence_score = sum(confidences) / len(confidences)
        
        # High confidence = successful intent detection
        high_confidence = [i for i in filtered if i.confidence_score >= 0.5]
        metrics.successful_interactions = len(high_confidence)
        metrics.failed_interactions = metrics.total_interactions - metrics.successful_interactions
        metrics.intent_accuracy = len(high_confidence) / len(filtered)
        
        # Satisfaction
        with_feedback = [i for i in filtered if i.user_satisfied is not None]
        metrics.feedback_count = len(with_feedback)
        if with_feedback:
            satisfied = [i for i in with_feedback if i.user_satisfied]
            metrics.satisfaction_rate = len(satisfied) / len(with_feedback)
        
        # By type
        for i in filtered:
            itype = i.interaction_type
            metrics.interactions_by_type[itype] = metrics.interactions_by_type.get(itype, 0) + 1
        
        # By language
        for i in filtered:
            lang = i.language
            metrics.interactions_by_language[lang] = metrics.interactions_by_language.get(lang, 0) + 1
        
        # By hour
        for i in filtered:
            try:
                hour = datetime.fromisoformat(i.timestamp).hour
                metrics.interactions_by_hour[hour] = metrics.interactions_by_hour.get(hour, 0) + 1
            except:
                pass
        
        # Job search metrics
        searches = [i for i in filtered if i.interaction_type == InteractionType.JOB_SEARCH]
        metrics.total_job_searches = len(searches)
        if searches:
            metrics.avg_jobs_per_search = sum(i.jobs_returned for i in searches) / len(searches)
        
        # Application metrics
        applications = [i for i in filtered if i.interaction_type == InteractionType.APPLICATION]
        metrics.total_applications = len(applications)
        if applications:
            successful = [i for i in applications if i.action_completed]
            metrics.application_success_rate = len(successful) / len(applications)
        
        # Search to apply conversion
        if metrics.total_job_searches > 0:
            metrics.search_to_apply_rate = metrics.total_applications / metrics.total_job_searches
        
        return metrics
    
    def get_daily_stats(self, days: int = 7) -> List[Dict]:
        """Get daily interaction statistics"""
        
        stats = []
        
        for i in range(days):
            date = datetime.utcnow().date() - timedelta(days=i)
            date_str = date.isoformat()
            
            day_interactions = [
                inter for inter in self.interactions
                if inter.timestamp.startswith(date_str)
            ]
            
            if day_interactions:
                stats.append({
                    "date": date_str,
                    "total": len(day_interactions),
                    "avg_confidence": sum(i.confidence_score for i in day_interactions) / len(day_interactions),
                    "avg_response_time": sum(i.response_time_ms for i in day_interactions) / len(day_interactions),
                    "by_type": self._count_by_type(day_interactions)
                })
            else:
                stats.append({
                    "date": date_str,
                    "total": 0,
                    "avg_confidence": 0,
                    "avg_response_time": 0,
                    "by_type": {}
                })
        
        return stats
    
    def get_top_intents(self, limit: int = 10) -> List[Dict]:
        """Get most common intents"""
        
        intent_counts = defaultdict(int)
        intent_confidence = defaultdict(list)
        
        for i in self.interactions:
            intent_counts[i.intent_detected] += 1
            intent_confidence[i.intent_detected].append(i.confidence_score)
        
        result = []
        for intent, count in sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)[:limit]:
            avg_conf = sum(intent_confidence[intent]) / len(intent_confidence[intent])
            result.append({
                "intent": intent,
                "count": count,
                "avg_confidence": round(avg_conf, 3)
            })
        
        return result
    
    def get_language_distribution(self) -> Dict[str, float]:
        """Get percentage distribution by language"""
        
        if not self.interactions:
            return {}
        
        lang_counts = defaultdict(int)
        for i in self.interactions:
            lang_counts[i.language] += 1
        
        total = len(self.interactions)
        return {lang: round(count / total * 100, 2) for lang, count in lang_counts.items()}
    
    def get_performance_summary(self, lang: str = "fr") -> Dict[str, str]:
        """Get human-readable performance summary"""
        
        metrics = self.get_metrics(period_days=30)
        
        summaries = {
            "fr": {
                "total": f"Total interactions: {metrics.total_interactions}",
                "success_rate": f"Taux de réussite: {metrics.intent_accuracy * 100:.1f}%",
                "avg_response": f"Temps de réponse moyen: {metrics.avg_response_time_ms:.0f}ms",
                "satisfaction": f"Satisfaction utilisateur: {metrics.satisfaction_rate * 100:.1f}%",
                "job_searches": f"Recherches d'emploi: {metrics.total_job_searches}",
                "applications": f"Candidatures: {metrics.total_applications}",
                "conversion": f"Taux de conversion: {metrics.search_to_apply_rate * 100:.1f}%"
            },
            "en": {
                "total": f"Total interactions: {metrics.total_interactions}",
                "success_rate": f"Success rate: {metrics.intent_accuracy * 100:.1f}%",
                "avg_response": f"Average response time: {metrics.avg_response_time_ms:.0f}ms",
                "satisfaction": f"User satisfaction: {metrics.satisfaction_rate * 100:.1f}%",
                "job_searches": f"Job searches: {metrics.total_job_searches}",
                "applications": f"Applications: {metrics.total_applications}",
                "conversion": f"Conversion rate: {metrics.search_to_apply_rate * 100:.1f}%"
            },
            "ar": {
                "total": f"إجمالي التفاعلات: {metrics.total_interactions}",
                "success_rate": f"معدل النجاح: {metrics.intent_accuracy * 100:.1f}%",
                "avg_response": f"متوسط وقت الاستجابة: {metrics.avg_response_time_ms:.0f}ms",
                "satisfaction": f"رضا المستخدم: {metrics.satisfaction_rate * 100:.1f}%",
                "job_searches": f"عمليات البحث عن عمل: {metrics.total_job_searches}",
                "applications": f"التقديمات: {metrics.total_applications}",
                "conversion": f"معدل التحويل: {metrics.search_to_apply_rate * 100:.1f}%"
            }
        }
        
        return summaries.get(lang, summaries["fr"])
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics for reporting"""
        
        metrics = self.get_metrics()
        
        if format == "json":
            return json.dumps(asdict(metrics), indent=2, ensure_ascii=False)
        
        # Simple text format
        lines = [
            "=== Chatbot Performance Report ===",
            f"Period: {metrics.period_start[:10]} to {metrics.period_end[:10]}",
            f"",
            f"Total Interactions: {metrics.total_interactions}",
            f"Successful: {metrics.successful_interactions}",
            f"Failed: {metrics.failed_interactions}",
            f"",
            f"Response Time:",
            f"  Average: {metrics.avg_response_time_ms:.2f}ms",
            f"  Min: {metrics.min_response_time_ms:.2f}ms",
            f"  Max: {metrics.max_response_time_ms:.2f}ms",
            f"",
            f"Intent Detection:",
            f"  Accuracy: {metrics.intent_accuracy * 100:.1f}%",
            f"  Avg Confidence: {metrics.avg_confidence_score * 100:.1f}%",
            f"",
            f"User Satisfaction: {metrics.satisfaction_rate * 100:.1f}%",
            f"",
            f"Job Search:",
            f"  Total Searches: {metrics.total_job_searches}",
            f"  Avg Jobs/Search: {metrics.avg_jobs_per_search:.1f}",
            f"",
            f"Applications:",
            f"  Total: {metrics.total_applications}",
            f"  Success Rate: {metrics.application_success_rate * 100:.1f}%",
            f"  Conversion: {metrics.search_to_apply_rate * 100:.1f}%"
        ]
        
        return "\n".join(lines)
    
    def _categorize_interaction(self, intent: str) -> str:
        """Categorize interaction type from intent"""
        
        mapping = {
            "search_jobs": InteractionType.JOB_SEARCH,
            "apply_job": InteractionType.APPLICATION,
            "my_applications": InteractionType.APPLICATION,
            "anem_faq": InteractionType.FAQ,
            "greeting": InteractionType.GREETING,
            "help": InteractionType.HELP,
        }
        
        return mapping.get(intent, InteractionType.GENERAL).value
    
    def _count_by_type(self, interactions: List[InteractionMetric]) -> Dict[str, int]:
        """Count interactions by type"""
        
        counts = defaultdict(int)
        for i in interactions:
            counts[i.interaction_type] += 1
        return dict(counts)
    
    def _load_data(self):
        """Load analytics data from storage"""
        
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                self.interactions = [
                    InteractionMetric(**i) for i in data.get("interactions", [])
                ]
                self.feedback = data.get("feedback", {})
        except Exception as e:
            print(f"Error loading analytics: {e}")
            self.interactions = []
            self.feedback = {}
    
    def _save_data(self):
        """Save analytics data to storage"""
        
        try:
            data = {
                "interactions": [asdict(i) for i in self.interactions[-10000:]],  # Keep last 10k
                "feedback": self.feedback,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving analytics: {e}")
    
    def clear_old_data(self, days: int = 90):
        """Clear interactions older than specified days"""
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        self.interactions = [
            i for i in self.interactions
            if i.timestamp >= cutoff_str
        ]
        
        self._save_data()


# Singleton instance
chatbot_analytics = ChatbotAnalytics()
