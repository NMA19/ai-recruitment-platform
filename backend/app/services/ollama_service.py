"""
Local LLM Service using Ollama
Provides offline LLM capabilities without requiring cloud API keys
Supports multiple models: Llama 3, Mistral, Qwen, etc.
"""

import os
import json
import httpx
from typing import Optional, Dict, Any, List, Generator
from dataclasses import dataclass
from enum import Enum


class OllamaModel(str, Enum):
    """Supported Ollama models optimized for different use cases"""
    LLAMA3_8B = "llama3:8b"              # Best balance of speed/quality
    LLAMA3_70B = "llama3:70b"            # Highest quality (requires more RAM)
    MISTRAL_7B = "mistral:7b"            # Fast, good for chat
    MIXTRAL_8X7B = "mixtral:8x7b"        # High quality, multilingual
    QWEN2_7B = "qwen2:7b"                # Good for multilingual (Arabic/French)
    PHI3_MINI = "phi3:mini"              # Very fast, lightweight
    GEMMA2_9B = "gemma2:9b"              # Good quality, fast
    CODELLAMA_7B = "codellama:7b"        # Code-focused
    

@dataclass
class OllamaConfig:
    """Configuration for Ollama connection"""
    base_url: str = "http://localhost:11434"
    timeout: float = 120.0
    default_model: str = "llama3:8b"
    max_tokens: int = 500
    temperature: float = 0.7


class OllamaService:
    """
    Ollama LLM Service for local inference
    
    Features:
    - Multiple model support
    - Streaming responses
    - Context management
    - Automatic fallback
    """
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self.is_available = False
        self._check_availability()
        
        # System prompt for ANEM/Wassit context
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for ANEM assistant context"""
        return """أنت "وسيط" (Wassit) - مساعد ذكي للتوظيف من ANEM الجزائر.
You are "Wassit" - an intelligent recruitment assistant for ANEM Algeria.
Tu es "Wassit" - un assistant intelligent de recrutement pour l'ANEM Algérie.

CAPABILITIES:
- Help find jobs across all 58 Algerian Wilayas
- Explain ANEM registration, renewal, and programs (DAIP, CFI, CTA)
- Assist with job applications and CV advice
- Answer questions in French, Arabic (Darja), and English

ANEM CONTEXT:
- ANEM = Agence Nationale de l'Emploi (National Employment Agency)
- Wassit Online = wassitonline.anem.dz
- Registration renewal required every 6 months
- Programs: DAIP (insertion), CFI (formation), CTA (contrat aidé)

RESPONSE GUIDELINES:
- Detect the user's language and respond in the same language
- Be helpful, concise, and professional
- Provide practical information about job searching in Algeria
- If unsure, suggest contacting the local ANEM agency

IMPORTANT: You are embedded in a recruitment platform. Focus on employment-related topics."""

    def _check_availability(self) -> bool:
        """Check if Ollama server is running"""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.config.base_url}/api/tags")
                if response.status_code == 200:
                    self.is_available = True
                    models = response.json().get("models", [])
                    if models:
                        print(f"Ollama available with models: {[m['name'] for m in models]}")
                    return True
        except Exception as e:
            print(f"Ollama not available: {e}")
            self.is_available = False
        return False
    
    def list_models(self) -> List[Dict]:
        """List available models on Ollama server"""
        if not self.is_available:
            return []
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{self.config.base_url}/api/tags")
                if response.status_code == 200:
                    return response.json().get("models", [])
        except Exception:
            pass
        return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull/download a model from Ollama registry"""
        try:
            with httpx.Client(timeout=300.0) as client:  # Long timeout for download
                response = client.post(
                    f"{self.config.base_url}/api/pull",
                    json={"name": model_name}
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Error pulling model {model_name}: {e}")
            return False
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        context: Optional[List[Dict]] = None,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from Ollama
        
        Args:
            prompt: User message
            model: Model name (defaults to config.default_model)
            system: System prompt (uses ANEM context by default)
            context: Previous conversation context
            options: Additional generation options
            
        Returns:
            Dict with 'response', 'model', 'done', etc.
        """
        if not self.is_available:
            return {
                "response": None,
                "error": "Ollama not available",
                "done": True
            }
        
        model = model or self.config.default_model
        system = system or self.system_prompt
        
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "num_predict": self.config.max_tokens,
                "temperature": self.config.temperature,
                **(options or {})
            }
        }
        
        # Add context if provided
        if context:
            payload["context"] = context
        
        try:
            with httpx.Client(timeout=self.config.timeout) as client:
                response = client.post(
                    f"{self.config.base_url}/api/generate",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "response": result.get("response", ""),
                        "model": result.get("model"),
                        "done": result.get("done", True),
                        "context": result.get("context"),  # For follow-up
                        "total_duration": result.get("total_duration"),
                        "eval_count": result.get("eval_count")
                    }
                else:
                    return {
                        "response": None,
                        "error": f"HTTP {response.status_code}",
                        "done": True
                    }
                    
        except httpx.TimeoutException:
            return {
                "response": None,
                "error": "Request timed out",
                "done": True
            }
        except Exception as e:
            return {
                "response": None,
                "error": str(e),
                "done": True
            }
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Chat API endpoint (maintains conversation history)
        
        Args:
            messages: List of {"role": "user|assistant|system", "content": "..."}
            model: Model name
            options: Generation options
        """
        if not self.is_available:
            return {
                "message": {"role": "assistant", "content": ""},
                "error": "Ollama not available",
                "done": True
            }
        
        model = model or self.config.default_model
        
        # Ensure system message is present
        if not any(m.get("role") == "system" for m in messages):
            messages = [{"role": "system", "content": self.system_prompt}] + messages
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": self.config.max_tokens,
                "temperature": self.config.temperature,
                **(options or {})
            }
        }
        
        try:
            with httpx.Client(timeout=self.config.timeout) as client:
                response = client.post(
                    f"{self.config.base_url}/api/chat",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "message": result.get("message", {}),
                        "model": result.get("model"),
                        "done": result.get("done", True),
                        "total_duration": result.get("total_duration"),
                        "eval_count": result.get("eval_count")
                    }
                else:
                    return {
                        "message": {"role": "assistant", "content": ""},
                        "error": f"HTTP {response.status_code}",
                        "done": True
                    }
                    
        except Exception as e:
            return {
                "message": {"role": "assistant", "content": ""},
                "error": str(e),
                "done": True
            }
    
    def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Stream response from Ollama (for real-time display)
        
        Yields:
            Text chunks as they are generated
        """
        if not self.is_available:
            yield ""
            return
        
        model = model or self.config.default_model
        system = system or self.system_prompt
        
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": True,
            "options": {
                "num_predict": self.config.max_tokens,
                "temperature": self.config.temperature
            }
        }
        
        try:
            with httpx.Client(timeout=self.config.timeout) as client:
                with client.stream(
                    "POST",
                    f"{self.config.base_url}/api/generate",
                    json=payload
                ) as response:
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                                if data.get("done"):
                                    break
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            print(f"Streaming error: {e}")
            yield ""
    
    def generate_job_insights(
        self,
        job_title: str,
        job_description: str,
        user_skills: Optional[str] = None,
        lang: str = "fr"
    ) -> str:
        """Generate AI insights about a job posting"""
        
        prompts = {
            "fr": f"""Analyse cette offre d'emploi et donne des conseils:

Titre: {job_title}
Description: {job_description}
Compétences du candidat: {user_skills or 'Non spécifiées'}

Fournis:
1. Points clés du poste (2-3 lignes)
2. Compétences requises principales
3. Conseils pour la candidature""",

            "en": f"""Analyze this job posting and provide insights:

Title: {job_title}
Description: {job_description}
Candidate skills: {user_skills or 'Not specified'}

Provide:
1. Key points about the position (2-3 lines)
2. Main required skills
3. Tips for applying""",

            "ar": f"""حلل هذا العرض الوظيفي وقدم نصائح:

العنوان: {job_title}
الوصف: {job_description}
مهارات المرشح: {user_skills or 'غير محددة'}

قدم:
1. النقاط الرئيسية للوظيفة (2-3 أسطر)
2. المهارات الأساسية المطلوبة
3. نصائح للتقديم"""
        }
        
        result = self.generate(prompts.get(lang, prompts["fr"]))
        return result.get("response", "")
    
    def generate_cv_suggestions(
        self,
        user_profile: Dict,
        target_job: Optional[Dict] = None,
        lang: str = "fr"
    ) -> str:
        """Generate CV improvement suggestions"""
        
        profile_text = json.dumps(user_profile, ensure_ascii=False, indent=2)
        job_text = json.dumps(target_job, ensure_ascii=False, indent=2) if target_job else "Non spécifié"
        
        prompts = {
            "fr": f"""Analyse ce profil et suggère des améliorations pour le CV:

Profil actuel:
{profile_text}

Poste ciblé:
{job_text}

Suggestions (format concis):""",

            "en": f"""Analyze this profile and suggest CV improvements:

Current profile:
{profile_text}

Target position:
{job_text}

Suggestions (concise format):""",

            "ar": f"""حلل هذا الملف واقترح تحسينات للسيرة الذاتية:

الملف الحالي:
{profile_text}

الوظيفة المستهدفة:
{job_text}

الاقتراحات (شكل مختصر):"""
        }
        
        result = self.generate(prompts.get(lang, prompts["fr"]))
        return result.get("response", "")
    
    def get_status(self) -> Dict[str, Any]:
        """Get Ollama service status"""
        self._check_availability()
        
        return {
            "available": self.is_available,
            "base_url": self.config.base_url,
            "default_model": self.config.default_model,
            "models": self.list_models() if self.is_available else []
        }


# Singleton instance
ollama_service = OllamaService()


def get_ollama_service(config: Optional[OllamaConfig] = None) -> OllamaService:
    """Factory function to get Ollama service instance"""
    global ollama_service
    if config:
        ollama_service = OllamaService(config)
    return ollama_service
