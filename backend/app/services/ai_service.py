"""
AI Service Layer
Handles natural language understanding using OpenAI API
Converts human language → structured recruitment data

This is the INTELLIGENCE LAYER of the system.
"""

import json
from typing import Optional

from app.core.config import settings
from app.schemas.chat import AIExtraction, ChatIntent

# Try to import OpenAI, but make it optional
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIService:
    """
    AI Service for Natural Language Understanding
    Extracts intent and parameters from user messages
    """
    
    def __init__(self):
        self.client = None
        # Only initialize if we have a valid API key (not the placeholder)
        if (OPENAI_AVAILABLE and 
            settings.OPENAI_API_KEY and 
            settings.OPENAI_API_KEY != "your-openai-api-key-here"):
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
                self.client = None
        
        # System prompt for intent extraction
        self.system_prompt = """You are an AI assistant for a job recruitment platform.
Your job is to analyze user messages and extract structured data.

You must respond ONLY with valid JSON in this exact format:
{
    "intent": "one of: search_job, apply_job, get_job_details, list_applications, general_question, greeting, help, unknown",
    "role": "job role/title if mentioned (e.g., backend developer, data scientist)",
    "location": "location if mentioned (e.g., Algiers, Paris, remote)",
    "contract_type": "one of: internship, full_time, part_time, contract, freelance (if mentioned)",
    "skills": ["list", "of", "skills", "if", "mentioned"],
    "company": "company name if mentioned",
    "job_id": null or integer if user references a specific job number,
    "confidence": 0.0 to 1.0 how confident you are in the extraction
}

Examples:
User: "I want a backend internship in Algiers"
Response: {"intent": "search_job", "role": "backend", "location": "Algiers", "contract_type": "internship", "skills": [], "company": null, "job_id": null, "confidence": 0.95}

User: "Show me Python developer jobs"
Response: {"intent": "search_job", "role": "developer", "location": null, "contract_type": null, "skills": ["Python"], "company": null, "job_id": null, "confidence": 0.9}

User: "I want to apply for job number 5"
Response: {"intent": "apply_job", "role": null, "location": null, "contract_type": null, "skills": [], "company": null, "job_id": 5, "confidence": 0.95}

User: "Hello"
Response: {"intent": "greeting", "role": null, "location": null, "contract_type": null, "skills": [], "company": null, "job_id": null, "confidence": 1.0}

User: "What jobs do you have?"
Response: {"intent": "search_job", "role": null, "location": null, "contract_type": null, "skills": [], "company": null, "job_id": null, "confidence": 0.85}

Always respond with ONLY the JSON, no other text."""

    async def extract_intent(self, user_message: str) -> AIExtraction:
        """
        Extract intent and parameters from user message using OpenAI
        
        Args:
            user_message: The user's natural language message
            
        Returns:
            AIExtraction object with intent and extracted parameters
        """
        
        # If no API key, use fallback extraction
        if not self.client:
            return self._fallback_extraction(user_message)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            # Parse the response
            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)
            
            return AIExtraction(
                intent=ChatIntent(result.get("intent", "unknown")),
                role=result.get("role"),
                location=result.get("location"),
                contract_type=result.get("contract_type"),
                skills=result.get("skills", []),
                company=result.get("company"),
                job_id=result.get("job_id"),
                confidence=result.get("confidence", 0.5)
            )
            
        except Exception as e:
            print(f"AI extraction error: {e}")
            return self._fallback_extraction(user_message)
    
    def _fallback_extraction(self, message: str) -> AIExtraction:
        """
        Fallback extraction using simple keyword matching
        Used when OpenAI API is not available
        """
        message_lower = message.lower()
        
        # Detect intent
        intent = ChatIntent.UNKNOWN
        if any(word in message_lower for word in ["hi", "hello", "hey", "bonjour", "salut"]):
            intent = ChatIntent.GREETING
        elif any(word in message_lower for word in ["help", "aide", "how"]):
            intent = ChatIntent.HELP
        elif any(word in message_lower for word in ["apply", "postuler", "candidate"]):
            intent = ChatIntent.APPLY_JOB
        elif any(word in message_lower for word in ["job", "work", "emploi", "position", "stage", "internship", "developer", "engineer"]):
            intent = ChatIntent.SEARCH_JOB
        elif any(word in message_lower for word in ["my application", "mes candidatures", "status"]):
            intent = ChatIntent.LIST_APPLICATIONS
        else:
            intent = ChatIntent.GENERAL_QUESTION
        
        # Extract location (common cities)
        location = None
        locations = ["algiers", "alger", "oran", "constantine", "paris", "london", "remote", "à distance"]
        for loc in locations:
            if loc in message_lower:
                location = loc.title()
                break
        
        # Extract contract type
        contract_type = None
        if "internship" in message_lower or "stage" in message_lower:
            contract_type = "internship"
        elif "full-time" in message_lower or "temps plein" in message_lower or "cdi" in message_lower:
            contract_type = "full_time"
        elif "part-time" in message_lower or "temps partiel" in message_lower:
            contract_type = "part_time"
        elif "freelance" in message_lower:
            contract_type = "freelance"
        
        # Extract skills
        skills = []
        skill_keywords = ["python", "javascript", "react", "node", "java", "sql", "docker", "aws", "machine learning", "ai"]
        for skill in skill_keywords:
            if skill in message_lower:
                skills.append(skill.title())
        
        # Extract role
        role = None
        roles = ["backend", "frontend", "fullstack", "full stack", "data scientist", "devops", "designer", "developer"]
        for r in roles:
            if r in message_lower:
                role = r.title()
                break
        
        return AIExtraction(
            intent=intent,
            role=role,
            location=location,
            contract_type=contract_type,
            skills=skills,
            company=None,
            job_id=None,
            confidence=0.6
        )
    
    async def generate_response(self, intent: ChatIntent, context: dict = None) -> str:
        """
        Generate a natural language response based on intent and context
        """
        context = context or {}
        
        responses = {
            ChatIntent.GREETING: "Hello! 👋 I'm your AI recruitment assistant. I can help you find jobs, apply for positions, and track your applications. What are you looking for?",
            
            ChatIntent.HELP: """I can help you with:
• **Search for jobs** - Just tell me what you're looking for (e.g., "Show me Python developer jobs in Algiers")
• **Apply for jobs** - Say "I want to apply for job #5"
• **Check applications** - Ask "Show my applications"

What would you like to do?""",
            
            ChatIntent.SEARCH_JOB: self._format_job_search_response(context),
            
            ChatIntent.APPLY_JOB: self._format_apply_response(context),
            
            ChatIntent.LIST_APPLICATIONS: self._format_applications_response(context),
            
            ChatIntent.GENERAL_QUESTION: "I'm here to help with job searching and applications. Could you tell me more about what you're looking for?",
            
            ChatIntent.UNKNOWN: "I'm not sure I understood that. You can ask me to find jobs, apply for positions, or check your applications. How can I help?"
        }
        
        return responses.get(intent, responses[ChatIntent.UNKNOWN])
    
    def _format_job_search_response(self, context: dict) -> str:
        """Format response for job search results"""
        jobs = context.get("jobs", [])
        
        if not jobs:
            params = context.get("params", {})
            criteria = []
            if params.get("role"):
                criteria.append(params["role"])
            if params.get("location"):
                criteria.append(f"in {params['location']}")
            if params.get("contract_type"):
                criteria.append(params["contract_type"])
            
            criteria_str = " ".join(criteria) if criteria else "your criteria"
            return f"I couldn't find any jobs matching {criteria_str}. Would you like to try different criteria?"
        
        count = len(jobs)
        return f"I found {count} job{'s' if count > 1 else ''} matching your criteria! Here they are:"
    
    def _format_apply_response(self, context: dict) -> str:
        """Format response for job application"""
        success = context.get("success", False)
        job = context.get("job")
        
        if success and job:
            return f"✅ Great! Your application for **{job.title}** at **{job.company}** has been submitted. Good luck!"
        elif context.get("already_applied"):
            return "You've already applied for this job. Check 'My Applications' to see its status."
        else:
            return "I couldn't process your application. Please make sure the job ID is valid."
    
    def _format_applications_response(self, context: dict) -> str:
        """Format response for listing applications"""
        applications = context.get("applications", [])
        
        if not applications:
            return "You haven't applied to any jobs yet. Would you like me to help you find some?"
        
        count = len(applications)
        return f"You have {count} application{'s' if count > 1 else ''}:"


# Singleton instance
ai_service = AIService()
