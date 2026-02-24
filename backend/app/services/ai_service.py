"""
AI Service for natural language processing
Handles job search queries, application commands, and general assistance
"""

import re
import json
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.models import Job, Application, User, ApplicationStatus


class AIService:
    """AI Service for processing chat messages"""

    def __init__(self):
        self.openai_client = None
        self._init_openai()

    def _init_openai(self):
        """Initialize OpenAI client if API key is available"""
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here":
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                pass

    def process_message(
        self,
        message: str,
        db: Session,
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and return appropriate response
        
        Returns:
            Dict with 'response', optional 'jobs', and optional 'action'
        """
        message_lower = message.lower().strip()

        # Check for specific intents
        intent, params = self._detect_intent(message_lower)

        if intent == "search_jobs":
            return self._handle_job_search(params, db)
        elif intent == "apply_job":
            return self._handle_apply(params, db, user)
        elif intent == "my_applications":
            return self._handle_my_applications(db, user)
        elif intent == "help":
            return self._handle_help()
        elif intent == "greeting":
            return self._handle_greeting(user)
        else:
            # Try OpenAI if available, otherwise use fallback
            return self._handle_general_query(message, db)

    def _detect_intent(self, message: str) -> Tuple[str, Dict]:
        """Detect the intent of the message"""
        params = {}

        # Greeting patterns
        greeting_patterns = ["hello", "hi", "hey", "bonjour", "salut", "good morning", "good afternoon"]
        if any(message.startswith(g) for g in greeting_patterns):
            return "greeting", params

        # Help patterns
        if any(word in message for word in ["help", "what can you do", "commands", "aide"]):
            return "help", params

        # Apply patterns
        apply_match = re.search(r"apply\s+(?:for\s+)?(?:job\s+)?#?(\d+)", message)
        if apply_match:
            params["job_id"] = int(apply_match.group(1))
            return "apply_job", params

        # My applications
        if any(phrase in message for phrase in ["my applications", "mes candidatures", "show my applications", "list my applications"]):
            return "my_applications", params

        # Job search patterns
        search_keywords = ["find", "search", "show", "list", "looking for", "cherche", "jobs", "job", "positions", "internship", "internships", "stage"]
        if any(keyword in message for keyword in search_keywords):
            # Extract search parameters
            params = self._extract_search_params(message)
            return "search_jobs", params

        return "general", params

    def _extract_search_params(self, message: str) -> Dict:
        """Extract search parameters from message"""
        params = {}

        # Extract location
        location_patterns = [
            r"in\s+([A-Za-z\s]+?)(?:\s+with|\s+for|\s*$|,|\.|!)",
            r"at\s+([A-Za-z\s]+?)(?:\s+with|\s+for|\s*$|,|\.|!)",
            r"à\s+([A-Za-z\s]+?)(?:\s+avec|\s+pour|\s*$|,|\.|!)"
        ]
        for pattern in location_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params["location"] = match.group(1).strip()
                break

        # Extract skills
        skill_keywords = ["python", "java", "javascript", "react", "node", "sql", "django", "fastapi", 
                         "machine learning", "ai", "data science", "devops", "aws", "docker", "kubernetes",
                         "php", "laravel", "vue", "angular", "typescript", "go", "rust", "c++", "c#", ".net"]
        found_skills = [skill for skill in skill_keywords if skill in message.lower()]
        if found_skills:
            params["skills"] = found_skills

        # Extract contract type
        if any(word in message for word in ["internship", "stage", "intern"]):
            params["contract_type"] = "internship"
        elif any(word in message for word in ["full-time", "full time", "temps plein", "cdi"]):
            params["contract_type"] = "full-time"
        elif any(word in message for word in ["part-time", "part time", "temps partiel"]):
            params["contract_type"] = "part-time"
        elif any(word in message for word in ["freelance", "remote"]):
            params["contract_type"] = "freelance"
        elif any(word in message for word in ["contract", "cdd"]):
            params["contract_type"] = "contract"

        return params

    def _handle_job_search(self, params: Dict, db: Session) -> Dict[str, Any]:
        """Handle job search request"""
        query = db.query(Job).filter(Job.is_active == True)

        # Apply filters
        if "location" in params:
            query = query.filter(Job.location.ilike(f"%{params['location']}%"))

        if "skills" in params:
            for skill in params["skills"]:
                query = query.filter(Job.skills.ilike(f"%{skill}%"))

        if "contract_type" in params:
            query = query.filter(Job.contract_type == params["contract_type"])

        jobs = query.limit(10).all()

        if not jobs:
            return {
                "response": "I couldn't find any jobs matching your criteria. Try broadening your search or check all available jobs.",
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
            filter_desc.append(f"in {params['location']}")
        if "skills" in params:
            filter_desc.append(f"with skills: {', '.join(params['skills'])}")
        if "contract_type" in params:
            filter_desc.append(f"type: {params['contract_type']}")

        filter_text = " ".join(filter_desc) if filter_desc else ""
        
        return {
            "response": f"I found {len(jobs)} job(s) {filter_text}. Here are the results:",
            "jobs": job_list,
            "action": "search"
        }

    def _handle_apply(self, params: Dict, db: Session, user: Optional[User]) -> Dict[str, Any]:
        """Handle job application request"""
        if not user:
            return {
                "response": "You need to be logged in to apply for jobs. Please sign in or create an account.",
                "action": "auth_required"
            }

        job_id = params.get("job_id")
        if not job_id:
            return {
                "response": "Please specify the job ID you want to apply for. For example: 'Apply for job #5'",
                "action": "clarify"
            }

        job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()
        if not job:
            return {
                "response": f"Job #{job_id} was not found or is no longer available.",
                "action": "not_found"
            }

        # Check if already applied
        existing = db.query(Application).filter(
            Application.job_id == job_id,
            Application.candidate_id == user.id
        ).first()

        if existing:
            return {
                "response": f"You have already applied for '{job.title}' at {job.company}. Your application status is: {existing.status}.",
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

        return {
            "response": f"🎉 Successfully applied for '{job.title}' at {job.company}! Your application is now pending review.",
            "action": "applied"
        }

    def _handle_my_applications(self, db: Session, user: Optional[User]) -> Dict[str, Any]:
        """Handle request to view user's applications"""
        if not user:
            return {
                "response": "You need to be logged in to view your applications. Please sign in.",
                "action": "auth_required"
            }

        applications = db.query(Application).filter(
            Application.candidate_id == user.id
        ).order_by(Application.created_at.desc()).all()

        if not applications:
            return {
                "response": "You haven't applied to any jobs yet. Search for jobs and apply using 'Apply for job #ID'.",
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

        response_text = f"You have {len(applications)} application(s):\n\n"
        for app in app_list:
            status_emoji = {"pending": "⏳", "reviewed": "👀", "accepted": "✅", "rejected": "❌"}.get(app["status"], "📋")
            response_text += f"{status_emoji} {app['job_title']} at {app['company']} - {app['status'].upper()}\n"

        return {
            "response": response_text,
            "action": "show_applications"
        }

    def _handle_help(self) -> Dict[str, Any]:
        """Handle help request"""
        return {
            "response": """I can help you with the following:

🔍 **Job Search:**
- "Find Python jobs in Algiers"
- "Show me internships"
- "Search for React developer positions"

📝 **Applications:**
- "Apply for job #5"
- "Show my applications"

💡 **Tips:**
- You can search by skills, location, or contract type
- Login to apply for jobs and track your applications

How can I assist you today?""",
            "action": "help"
        }

    def _handle_greeting(self, user: Optional[User]) -> Dict[str, Any]:
        """Handle greeting"""
        if user:
            return {
                "response": f"Hello {user.full_name}! 👋 Welcome back to the recruitment platform. How can I help you today? You can search for jobs, apply to positions, or check your applications.",
                "action": "greeting"
            }
        return {
            "response": "Hello! 👋 Welcome to the AI Recruitment Platform. I can help you find jobs, answer questions about positions, and more. What are you looking for today?",
            "action": "greeting"
        }

    def _handle_general_query(self, message: str, db: Session) -> Dict[str, Any]:
        """Handle general queries using OpenAI or fallback"""
        if self.openai_client:
            try:
                # Get some job context
                jobs = db.query(Job).filter(Job.is_active == True).limit(5).all()
                job_context = "\n".join([
                    f"- {j.title} at {j.company} ({j.location}, {j.contract_type})"
                    for j in jobs
                ])

                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""You are a helpful recruitment assistant. Help users find jobs and answer their questions.
Available jobs:
{job_context}

Keep responses concise and helpful. If users want to search for jobs, tell them they can say things like "Find Python jobs in Algiers" or "Show me internships"."""
                        },
                        {"role": "user", "content": message}
                    ],
                    max_tokens=300
                )
                return {
                    "response": response.choices[0].message.content,
                    "action": "ai_response"
                }
            except Exception as e:
                pass

        # Fallback response
        return {
            "response": "I'm here to help you find jobs! Try asking me to:\n- Search for jobs (e.g., 'Find Python jobs')\n- Apply for a position (e.g., 'Apply for job #5')\n- View your applications\n\nWhat would you like to do?",
            "action": "fallback"
        }


# Singleton instance
ai_service = AIService()
