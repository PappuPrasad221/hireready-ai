import google.generativeai as genai
import os
from typing import Dict, Any, List
import json
import inspect
import re
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key and self._looks_like_valid_key(self.api_key):
            genai.configure(api_key=self.api_key)
            self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            self.model = genai.GenerativeModel(self.model_name)
        else:
            print("Warning: Gemini API key missing or placeholder. Using local/mock AI responses.")
            self.model = None

    def _looks_like_valid_key(self, api_key: str) -> bool:
        lowered = api_key.lower()
        if "your" in lowered or "demo" in lowered or "placeholder" in lowered:
            return False
        return len(api_key) >= 30 and api_key.startswith("AIza")
    
    async def generate_questions(self, resume_data: Dict[str, Any], job_insights: Dict[str, Any], role: str, company: str) -> List[str]:
        """Generate interview questions based on resume and job insights"""
        if not self.model:
            return self._get_mock_questions()
        
        try:
            prompt = f"""
            Generate 5 personalized interview questions for a {role} position at {company}.
            
            Resume Data:
            - Skills: {', '.join(resume_data.get('skills', []))}
            - Experience: {', '.join(resume_data.get('experience', []))}
            - Education: {', '.join(resume_data.get('education', []))}
            
            Job Insights:
            - Required Skills: {', '.join(job_insights.get('skills', []))}
            - Responsibilities: {', '.join(job_insights.get('responsibilities', []))}
            
            Generate a mix of:
            1. Technical questions
            2. Behavioral questions  
            3. Experience-based questions
            4. Problem-solving questions
            5. Company-specific questions
            
            Make questions specific and challenging. Return as a JSON array of strings.
            """
            
            content = await self.generate_content_text(prompt)
            questions = self._parse_json(content)
            return questions
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._get_mock_questions()
    
    async def evaluate_answer(self, question: str, answer: str, question_type: str) -> Dict[str, Any]:
        """Evaluate user's answer using AI"""
        if not self.model:
            return self._get_mock_evaluation()
        
        try:
            prompt = f"""
            Evaluate this interview answer:
            
            Question: {question}
            Question Type: {question_type}
            Answer: {answer}
            
            Provide evaluation in JSON format with:
            - score (0-100)
            - strengths (list of strings)
            - improvements (list of strings)
            - feedback (detailed feedback string)
            - suggested_answer (ideal answer)
            """
            
            content = await self.generate_content_text(prompt)
            evaluation = self._parse_json(content)
            return evaluation
            
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return self._get_mock_evaluation()
    
    async def generate_followup_question(self, original_question: str, answer: str, evaluation_score: float) -> str:
        """Generate follow-up question based on weak answer"""
        if not self.model:
            return "Can you provide a specific example where you faced a similar challenge?"
        
        try:
            prompt = f"""
            Generate a follow-up question based on:
            
            Original Question: {original_question}
            User's Answer: {answer}
            Evaluation Score: {evaluation_score}
            
            If the score is below 70, generate a question that helps the user provide a better answer.
            The follow-up should guide them to be more specific, provide examples, or address gaps.
            
            Return just the question as a string.
            """
            
            content = await self.generate_content_text(prompt)
            return content.strip()
            
        except Exception as e:
            print(f"Error generating follow-up: {e}")
            return "Can you provide a specific example where you faced a similar challenge?"
    
    async def evaluate_resume(self, resume_text: str) -> Dict[str, Any]:
        """Evaluate resume and provide score"""
        if not self.model:
            return {"score": 75, "feedback": "Resume looks good"}
        
        try:
            prompt = f"""
            Evaluate this resume and provide:
            - Overall score (0-100)
            - Key strengths
            - Areas for improvement
            - Missing skills or experience
            
            Resume Text:
            {resume_text}
            
            Return as JSON with keys: score, feedback, strengths, improvements, missing_skills
            """
            
            content = await self.generate_content_text(prompt)
            evaluation = self._parse_json(content)
            return evaluation
            
        except Exception as e:
            print(f"Error evaluating resume: {e}")
            return {"score": 75, "feedback": "Resume looks good"}
    
    def _get_mock_questions(self) -> List[str]:
        """Return mock questions when API is not available"""
        return [
            "Tell me about yourself and your experience relevant to this role.",
            "What interests you most about this position and our company?",
            "Describe a challenging project you've worked on and how you overcame obstacles.",
            "How do you stay updated with the latest technologies and industry trends?",
            "Where do you see yourself professionally in the next 3-5 years?"
        ]

    async def generate_content_text(self, prompt: str) -> str:
        """Generate plain text from Gemini, supporting sync or async SDK clients."""
        if not self.model:
            return ""

        try:
            response = self.model.generate_content(
                prompt,
                request_options={"timeout": 20}
            )
            if inspect.isawaitable(response):
                response = await response

            return getattr(response, "text", "") or ""
        except Exception as e:
            if "API key not valid" in str(e) or "API_KEY_INVALID" in str(e):
                print("Gemini API key is invalid. Disabling Gemini calls for this process.")
                self.model = None
            raise

    async def generate_content(self, prompt: str) -> Dict[str, Any]:
        """Compatibility wrapper for services expecting the raw REST-like shape."""
        text = await self.generate_content_text(prompt)
        return {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": text}
                        ]
                    }
                }
            ]
        }

    def _parse_json(self, content: str) -> Any:
        """Parse Gemini JSON, tolerating fenced or explanatory responses."""
        if not content:
            raise ValueError("Empty Gemini response")

        json_match = re.search(r"\{.*\}|\[.*\]", content, re.DOTALL)
        payload = json_match.group(0) if json_match else content
        return json.loads(payload)
    
    def _get_mock_evaluation(self) -> Dict[str, Any]:
        """Return mock evaluation when API is not available"""
        return {
            "score": 78,
            "strengths": [
                "Good technical knowledge",
                "Clear communication",
                "Relevant experience"
            ],
            "improvements": [
                "Provide more specific examples",
                "Add quantifiable results",
                "Be more concise"
            ],
            "feedback": "Good answer overall, but could be more specific with examples.",
            "suggested_answer": "In my previous role, I implemented a solution that reduced processing time by 40%..."
        }
