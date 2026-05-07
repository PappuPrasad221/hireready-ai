import re
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

try:
    import spacy
    SPACY_AVAILABLE = True
    nlp = spacy.load("en_core_web_sm")
except:
    SPACY_AVAILABLE = False
    nlp = None

import pdfplumber
import PyPDF2
import fitz  # PyMuPDF

from utils.logger import log_error, log_ai_interaction, log_file_operation
from utils.exceptions import FileProcessingError, AIServiceError, ValidationError
from services.gemini_service import GeminiService


class ResumeAnalyzer:
    """Enhanced resume analyzer with improved PDF parsing and structured extraction"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
        self.logger = logging.getLogger(__name__)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Using basic analysis.")
            self.nlp = None
        
        # Common tech skills and keywords
        self.tech_skills = {
            'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby'],
            'web': ['react', 'vue', 'angular', 'nodejs', 'express', 'django', 'flask', 'spring', 'laravel'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd'],
            'mobile': 'ios android swift kotlin reactnative flutter xamarin'.split(),
            'ai_ml': 'machine learning tensorflow pytorch scikit-learn nlp computer vision deep learning'.split(),
            'tools': ['git', 'jira', 'slack', 'trello', 'figma', 'postman', 'vscode', 'intellij']
        }
    
    def extract_resume_text(self, file_path: str) -> str:
        """Enhanced text extraction with multiple methods and quality assessment"""
        text = ""
        method_used = ""
        extraction_quality = "unknown"
        
        try:
            # Method 1: Try pdfplumber first
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                
                if len(text.strip()) > 500:
                    method_used = "pdfplumber"
                    extraction_quality = "high"
                    self.logger.info(f"Extracted {len(text)} characters using pdfplumber (high quality)")
                elif len(text.strip()) > 100:
                    method_used = "pdfplumber"
                    extraction_quality = "medium"
                    self.logger.info(f"Extracted {len(text)} characters using pdfplumber (medium quality)")
            except Exception as e:
                self.logger.warning(f"pdfplumber failed: {e}")
            
            # Method 2: Try PyMuPDF
            if len(text.strip()) < 500:
                try:
                    doc = fitz.open(file_path)
                    pymupdf_text = ""
                    for page in doc:
                        pymupdf_text += page.get_text() + "\n"
                    doc.close()
                    
                    if len(pymupdf_text.strip()) > len(text.strip()):
                        text = pymupdf_text
                        method_used = "PyMuPDF"
                        extraction_quality = "high" if len(pymupdf_text.strip()) > 500 else "medium"
                        self.logger.info(f"Switched to PyMuPDF: extracted {len(text)} characters")
                except Exception as e:
                    self.logger.warning(f"PyMuPDF failed: {e}")
            
            # Method 3: Fallback to PyPDF2
            if len(text.strip()) < 200:
                try:
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        pypdf2_text = ""
                        for page in pdf_reader.pages:
                            pypdf2_text += page.extract_text() + "\n"
                        
                        if len(pypdf2_text.strip()) > len(text.strip()):
                            text = pypdf2_text
                            method_used = "PyPDF2"
                            extraction_quality = "low"
                            self.logger.info(f"Switched to PyPDF2: extracted {len(text)} characters")
                except Exception as e:
                    self.logger.warning(f"PyPDF2 failed: {e}")
            
            if not text.strip():
                raise FileProcessingError("Could not extract any text from PDF")
            
            self.logger.info(f"Final extraction: {method_used} method, {len(text)} characters")
            log_file_operation("resume_text_extraction", "PDF", len(text), "system")
            
            cleaned_text = self.clean_resume_text(text)
            self.logger.info(f"Text cleaning: {len(text)} -> {len(cleaned_text)} characters")
            
            return cleaned_text
            
        except Exception as e:
            log_error(e, "Resume text extraction")
            raise FileProcessingError(f"Failed to extract text from PDF: {str(e)}")
    
    def clean_resume_text(self, text: str) -> str:
        """Enhanced text cleaning with section preservation"""
        if not text:
            return ""

        # Join PDF hyphenation before preserving lines.
        text = re.sub(r'([A-Za-z])-\s*\n\s*([A-Za-z])', r'\1\2', text)
        
        # Normalize lines without destroying PDF line boundaries.
        lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.splitlines()]
        text = '\n'.join(line for line in lines if line)
        
        # Normalize bullet points
        text = re.sub(r'[\u2022\u00B7\u25AA\u25AB\u25E6\u2023\u2043]', ' ', text)
        
        # Remove common headers/footers
        text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\b\d{1,2}[/]\d{1,2}[/]\d{4}\b', '', text)
        
        # Preserve likely section headings only when they appear as short standalone lines.
        section_names = [
            "EDUCATION", "EDUCATIONAL BACKGROUND", "SKILLS", "TECHNICAL SKILLS",
            "EXPERIENCE", "WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE",
            "PROJECTS", "AI PROJECTS", "PROJECT EXPERIENCE", "CERTIFICATIONS",
            "CERTIFICATES", "ACHIEVEMENTS", "ACCOMPLISHMENTS", "AWARDS",
            "INTERNSHIP", "INTERNSHIP EXPERIENCE"
        ]
        normalized_lines = []
        for line in text.splitlines():
            line_clean = line.strip()
            line_upper = re.sub(r'[^A-Z ]', '', line_clean.upper()).strip()
            is_heading = any(
                line_upper == name or (line_upper.startswith(name) and len(line_upper.split()) <= 4)
                for name in section_names
            )
            if is_heading:
                normalized_lines.extend(["", line_upper, ""])
            else:
                normalized_lines.append(line_clean)
        text = '\n'.join(normalized_lines)
        
        # Clean up excessive line breaks
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove special characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text.strip()
    
    def parse_resume_sections(self, text: str) -> Dict[str, str]:
        """Parse resume into sections before AI processing"""
        sections = {
            'education': '',
            'skills': '',
            'experience': '',
            'projects': '',
            'certifications': '',
            'achievements': '',
            'internship': '',
            'contact': ''
        }
        
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        section_keywords = {
            'education': ['EDUCATION', 'EDUCATIONAL BACKGROUND'],
            'skills': ['SKILLS', 'TECHNICAL SKILLS', 'TECHNICAL EXPERTISE', 'COMPETENCIES', 'TECHNOLOGIES'],
            'experience': ['EXPERIENCE', 'WORK EXPERIENCE', 'PROFESSIONAL EXPERIENCE', 'EMPLOYMENT'],
            'projects': ['PROJECTS', 'AI PROJECTS', 'PROJECT EXPERIENCE', 'PERSONAL PROJECTS'],
            'certifications': ['CERTIFICATIONS', 'CERTIFICATES', 'LICENSES', 'PROFESSIONAL CERTIFICATION'],
            'achievements': ['ACHIEVEMENTS', 'ACCOMPLISHMENTS', 'AWARDS', 'HONORS', 'RECOGNITION'],
            'internship': ['INTERNSHIP', 'INTERNS', 'TRAINEE', 'INTERNSHIP EXPERIENCE'],
            'contact': ['CONTACT', 'EMAIL', 'PHONE', 'LINKEDIN', 'GITHUB', 'PORTFOLIO']
        }
        
        for line in lines:
            line_upper = line.upper().strip()
            
            found_section = None
            for section, keywords in section_keywords.items():
                if any(
                    line_upper == keyword
                    or (line_upper.startswith(keyword + ':'))
                    or (line_upper.startswith(keyword) and len(line_upper.split()) <= 4)
                    for keyword in keywords
                ):
                    found_section = section
                    break
            
            if found_section:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                current_section = found_section
                current_content = []
            elif current_section and line.strip():
                current_content.append(line)
        
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        self.logger.info(f"Parsed {len([s for s in sections.values() if s.strip()])} sections from resume")
        return sections
    
    async def analyze_resume(self, file_path: str) -> Dict[str, Any]:
        """Enhanced main method with section-based parsing and strict validation"""
        try:
            raw_text = self.extract_resume_text(file_path)
            sections = self.parse_resume_sections(raw_text)
            
            self.logger.info(f"Section parsing completed: {len([s for s in sections.values() if s.strip()])} sections found")
            
            local_analysis = self.analyze_resume_locally(raw_text, sections)
            gemini_analysis = await self.analyze_resume_with_gemini(raw_text, sections)
            analysis = self.clean_resume_analysis_data(
                self.merge_resume_analysis(local_analysis, gemini_analysis)
            )
            
            detected_sections = [section for section, content in sections.items() if content.strip()]
            target_sections = ["education", "skills", "experience", "projects", "certifications", "achievements"]
            detected_for_missing = detected_sections + (["experience"] if "internship" in detected_sections else [])
            missing_sections = [section for section in target_sections if section not in detected_for_missing]
            parsing_confidence = self._calculate_parsing_confidence(analysis, raw_text, detected_sections)

            analysis["parsingConfidence"] = parsing_confidence
            analysis["metadata"] = {
                "textLength": len(raw_text),
                "rawTextLength": len(raw_text),
                "cleanedTextLength": len(raw_text),
                "parsingQuality": "high" if len(raw_text) > 1000 else "medium" if len(raw_text) > 500 else "low",
                "extractionMethod": "enhanced_pdf_parsing",
                "analysisTimestamp": datetime.now().isoformat(),
                "detectedSections": detected_sections,
                "missingSections": missing_sections,
                "parsingConfidence": parsing_confidence
            }
            
            self.logger.info(f"Resume analysis completed: {analysis.get('parsingConfidence', 0)}% confidence")
            
            return analysis
            
        except Exception as e:
            log_error(e, "Resume analysis main method")
            raise FileProcessingError(f"Resume analysis failed: {str(e)}")
    
    async def analyze_resume_with_gemini(self, text: str, sections: Dict[str, str] = None) -> Dict[str, Any]:
        """Analyze resume text using Gemini with strict JSON output and section awareness"""
        if not text or len(text.strip()) < 50:
            self.logger.warning(f"Resume text too short: {len(text)} characters")
            return self._get_empty_analysis("Resume text too short for analysis")

        if not getattr(self.gemini_service, "model", None):
            return self._get_empty_analysis("Gemini unavailable; local extraction used")
        
        # Build section-aware prompt
        section_context = ""
        if sections:
            section_context = "\n\nDetected Resume Sections:\n"
            for section_name, content in sections.items():
                if content.strip():
                    section_context += f"{section_name.upper()}: {len(content)} characters\n"
        
        # Create prompt using string concatenation to avoid f-string conflicts
        prompt = "You are an expert ATS resume parser.\n\n"
        prompt += "Analyze the resume text carefully and extract exact details.\n\n"
        prompt += "Return ONLY valid JSON. Do not use markdown. Do not explain anything.\n\n"
        prompt += "Schema:\n"
        prompt += "{\n"
        prompt += '  "candidateName": "",\n'
        prompt += '  "email": "",\n'
        prompt += '  "phone": "",\n'
        prompt += '  "linkedin": "",\n'
        prompt += '  "github": "",\n'
        prompt += '  "portfolio": "",\n'
        prompt += '  "education": [\n'
        prompt += "    {\n"
        prompt += '      "degree": "",\n'
        prompt += '      "institution": "",\n'
        prompt += '      "year": "",\n'
        prompt += '      "score": ""\n'
        prompt += "    }\n"
        prompt += "  ],\n"
        prompt += '  "skills": {\n'
        prompt += '    "programmingLanguages": [],\n'
        prompt += '    "frameworks": [],\n'
        prompt += '    "databases": [],\n'
        prompt += '    "aiMlSkills": [],\n'
        prompt += '    "tools": [],\n'
        prompt += '    "softSkills": []\n'
        prompt += "  },\n"
        prompt += '  "projects": [\n'
        prompt += "    {\n"
        prompt += '      "title": "",\n'
        prompt += '      "description": "",\n'
        prompt += '      "technologies": [],\n'
        prompt += '      "impact": "",\n'
        prompt += '      "role": ""\n'
        prompt += "    }\n"
        prompt += "  ],\n"
        prompt += '  "experience": [\n'
        prompt += "    {\n"
        prompt += '      "role": "",\n'
        prompt += '      "company": "",\n'
        prompt += '      "duration": "",\n'
        prompt += '      "responsibilities": []\n'
        prompt += "    }\n"
        prompt += "  ],\n"
        prompt += '  "certifications": [],\n'
        prompt += '  "achievements": [],\n'
        prompt += '  "resumeSummary": "",\n'
        prompt += '  "interviewTopics": []\n'
        prompt += "}\n\n"
        prompt += "Rules:\n"
        prompt += "- Extract only what is present in resume.\n"
        prompt += "- Do not hallucinate.\n"
        prompt += "- If any field is missing, keep it empty.\n"
        prompt += "- Do not mix projects with experience.\n"
        prompt += "- Do not mix education with certifications.\n"
        prompt += "- Preserve exact project names.\n"
        prompt += "- Preserve exact institution names.\n"
        prompt += "- Extract all technical skills separately.\n"
        prompt += "- Return valid JSON only.\n"
        prompt += section_context
        prompt += "\n\nResume Text:\n"
        prompt += text[:8000]
        
        try:
            log_ai_interaction(
                service="Gemini",
                operation="Resume Analysis",
                user_id="system",
                input_data=f"Resume text length: {len(text)}",
                output_data="Processing..."
            )
            
            response = await self.gemini_service.generate_content(prompt)
            
            if not response or "candidates" not in response:
                self.logger.error("No response from Gemini service")
                return self._get_empty_analysis("No response from Gemini")
            
            content = response["candidates"][0]["content"]["parts"][0]["text"] if response["candidates"] else ""
            
            if not content:
                self.logger.error("Empty response from Gemini service")
                return self._get_empty_analysis("Empty response from Gemini")
            
            try:
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    parsed_data = json.loads(json_str)
                else:
                    parsed_data = json.loads(content)
                
                validated_data = self.validate_resume_json(parsed_data)
                validated_data["extractionQuality"] = self._assess_extraction_quality(validated_data, text)
                
                self.logger.info(f"Successfully parsed resume data with {len(validated_data)} sections")
                
                log_ai_interaction(
                    service="Gemini",
                    operation="Resume Analysis",
                    user_id="system",
                    input_data=f"Resume text length: {len(text)}",
                    output_data=f"Parsed {len(validated_data)} sections"
                )
                
                return validated_data
                
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON parsing failed: {e}")
                self.logger.error(f"Raw response: {content[:500]}...")
                return await self._retry_gemini_analysis(text, content)
                
        except Exception as e:
            log_error(e, "Resume Gemini analysis")
            return self._get_empty_analysis(f"Analysis failed: {str(e)}")
    
    def _get_empty_analysis(self, reason: str) -> Dict[str, Any]:
        """Get empty analysis structure"""
        empty_analysis = self.validate_resume_json({})
        empty_analysis["extractionQuality"] = reason
        empty_analysis["parsingConfidence"] = 0
        return empty_analysis
    
    def _assess_extraction_quality(self, data: Dict[str, Any], text: str) -> str:
        """Assess the quality of resume extraction"""
        quality_score = 0
        
        if data.get("candidateName"):
            quality_score += 20
        
        skills = data.get("skills", {})
        total_skills = sum(len(skills.get(key, [])) for key in skills)
        if total_skills > 0:
            quality_score += 20
        
        if data.get("experience") and len(data["experience"]) > 0:
            quality_score += 20
        
        if data.get("education") and len(data["education"]) > 0:
            quality_score += 20
        
        if data.get("projects") and len(data["projects"]) > 0:
            quality_score += 20
        
        if quality_score >= 80:
            return "high"
        elif quality_score >= 60:
            return "medium"
        elif quality_score >= 40:
            return "low"
        else:
            return "very_low"

    def _calculate_parsing_confidence(self, data: Dict[str, Any], text: str, detected_sections: List[str]) -> int:
        """Calculate a conservative confidence score from text volume and extracted fields."""
        score = 0
        if len(text) > 500:
            score += 15
        if len(text) > 1200:
            score += 10

        score += min(25, len(detected_sections) * 4)

        if data.get("candidateName"):
            score += 8
        if data.get("email") or data.get("phone"):
            score += 8
        if data.get("education"):
            score += 12
        if data.get("experience"):
            score += 12
        if data.get("projects"):
            score += 10

        skills = data.get("skills", {})
        if isinstance(skills, dict):
            skill_count = sum(len(value) for value in skills.values() if isinstance(value, list))
        else:
            skill_count = len(skills) if isinstance(skills, list) else 0
        score += min(15, skill_count * 2)

        return max(0, min(100, int(score)))
    
    async def _retry_gemini_analysis(self, original_text: str, failed_response: str) -> Dict[str, Any]:
        """Retry Gemini analysis with correction prompt"""
        retry_prompt = "The previous response was not valid JSON. Please fix it and return ONLY valid JSON.\n\n"
        retry_prompt += f"Previous response:\n{failed_response[:500]}\n\n"
        retry_prompt += "Use this exact schema and return valid JSON only:\n"
        retry_prompt += "{\n"
        retry_prompt += '  "candidateName": "",\n'
        retry_prompt += '  "email": "",\n'
        retry_prompt += '  "phone": "",\n'
        retry_prompt += '  "education": [],\n'
        retry_prompt += '  "skills": {\n'
        retry_prompt += '    "programmingLanguages": [],\n'
        retry_prompt += '    "frameworks": [],\n'
        retry_prompt += '    "databases": [],\n'
        retry_prompt += '    "aiMlSkills": [],\n'
        retry_prompt += '    "tools": [],\n'
        retry_prompt += '    "softSkills": []\n'
        retry_prompt += "  },\n"
        retry_prompt += '  "projects": [],\n'
        retry_prompt += '  "experience": [],\n'
        retry_prompt += '  "certifications": [],\n'
        retry_prompt += '  "achievements": [],\n'
        retry_prompt += '  "resumeSummary": "",\n'
        retry_prompt += '  "interviewTopics": []\n'
        retry_prompt += "}\n\n"
        retry_prompt += f"Resume Text:\n{original_text[:8000]}"
        
        try:
            response = await self.gemini_service.generate_content(retry_prompt)
            content = response["candidates"][0]["content"]["parts"][0]["text"] if response["candidates"] else ""
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_data = json.loads(json_str)
                return self.validate_resume_json(parsed_data)
            else:
                self.logger.error("Retry failed - no JSON found")
                return self._get_empty_analysis("Retry failed - invalid JSON")
                
        except Exception as e:
            self.logger.error(f"Retry failed: {e}")
            return self._get_empty_analysis("Retry failed")
    
    def validate_resume_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize resume JSON structure"""
        expected_schema = {
            "candidateName": "",
            "email": "",
            "phone": "",
            "linkedin": "",
            "github": "",
            "portfolio": "",
            "education": [],
            "skills": {
                "programmingLanguages": [],
                "frameworks": [],
                "databases": [],
                "aiMlSkills": [],
                "tools": [],
                "softSkills": []
            },
            "projects": [],
            "experience": [],
            "certifications": [],
            "achievements": [],
            "resumeSummary": "",
            "interviewTopics": []
        }
        
        validated_data = expected_schema.copy()
        
        for key, expected_value in expected_schema.items():
            if key in data:
                if isinstance(expected_value, list):
                    validated_data[key] = data[key] if isinstance(data[key], list) else []
                elif isinstance(expected_value, dict):
                    validated_data[key] = data[key] if isinstance(data[key], dict) else expected_value
                else:
                    validated_data[key] = str(data[key]) if data[key] else ""
        
        return validated_data

    def analyze_resume_locally(self, text: str, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract resume details without AI so invalid Gemini keys do not blank the UI."""
        data = self.validate_resume_json({})
        data["candidateName"] = self._extract_candidate_name(text)
        contact = self._extract_contact_info_sync(text)
        data.update(contact)
        data["skills"] = self._extract_categorized_skills(text, sections.get("skills", ""))
        data["education"] = self._extract_education_records(sections.get("education", "") or text)
        experience_text = "\n".join([sections.get("experience", ""), sections.get("internship", "")])
        data["experience"] = self._extract_experience_records(experience_text)
        data["projects"] = self._extract_project_records(sections.get("projects", ""))
        data["certifications"] = self._extract_list_section(sections.get("certifications", ""))
        data["achievements"] = self._extract_list_section(sections.get("achievements", ""))
        data["resumeSummary"] = self._build_local_summary(text, data)
        data["interviewTopics"] = self._build_interview_topics(data)
        data["extractionQuality"] = self._assess_extraction_quality(data, text)
        return data

    def merge_resume_analysis(self, local_data: Dict[str, Any], ai_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prefer non-empty AI fields, but keep deterministic local extraction as fallback."""
        merged = self.validate_resume_json(local_data or {})
        ai_data = self.validate_resume_json(ai_data or {})

        for key in ["candidateName", "email", "phone", "linkedin", "github", "portfolio", "resumeSummary"]:
            if ai_data.get(key):
                merged[key] = ai_data[key]

        for key in ["education", "projects", "experience", "certifications", "achievements", "interviewTopics"]:
            merged[key] = self._merge_lists(merged.get(key, []), ai_data.get(key, []))

        merged["skills"] = self._merge_skill_dicts(merged.get("skills", {}), ai_data.get("skills", {}))

        ai_quality = ai_data.get("extractionQuality")
        local_quality = local_data.get("extractionQuality")
        merged["extractionQuality"] = ai_quality if ai_quality not in [None, "", "very_low"] else local_quality
        return merged

    def normalizeText(self, value: Any) -> str:
        """Normalize extracted text for professional display and comparisons."""
        if value is None:
            return ""
        text = str(value)
        text = text.replace("â€¢", " ").replace("•", " ").replace("▸", " ").replace("▪", " ")
        text = text.replace("Â·", " ").replace("|", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip(" -;,.")

    def removeUrls(self, value: Any) -> str:
        text = self.normalizeText(value)
        text = re.sub(r"https?://\S+|www\.\S+", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(?:github|gitlab|bitbucket)\s*:\s*\S+", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\bgithub\.com/\S+", "", text, flags=re.IGNORECASE)
        return self.normalizeText(text)

    def removeDuplicateSentences(self, value: Any) -> str:
        text = self.normalizeText(value)
        if not text:
            return ""
        raw_sentences = re.split(r"(?<=[.!?])\s+|(?:\s+-\s+)", text)
        seen = set()
        sentences = []
        for sentence in raw_sentences:
            cleaned = self.normalizeText(sentence)
            if not cleaned:
                continue
            key = re.sub(r"[^a-z0-9]+", " ", cleaned.lower()).strip()
            if key and key not in seen:
                seen.add(key)
                sentences.append(cleaned)
        return " ".join(sentences)

    def cleanProjectDescription(self, value: Any, title: str = "") -> str:
        text = self.removeUrls(value)
        title = self.normalizeText(title)
        if title:
            text = re.sub(re.escape(title), "", text, count=1, flags=re.IGNORECASE)

        cleanup_patterns = [
            r"\btech\s*stack\s*[:\-]\s*[^.]+",
            r"\btechnologies\s*(?:used)?\s*[:\-]\s*[^.]+",
            r"\btools\s*[:\-]\s*[^.]+",
            r"\bgithub\s*[:\-]?",
            r"\blink\s*[:\-]?",
            r"\brepository\s*[:\-]?",
        ]
        for pattern in cleanup_patterns:
            text = re.sub(pattern, " ", text, flags=re.IGNORECASE)

        text = re.sub(r"\s*(?:,|;)\s*(?:React|Python|JavaScript|Firebase|FastAPI|MongoDB|SQL|HTML|CSS|Node\.?js)\b", " ", text, flags=re.IGNORECASE)
        text = self.removeDuplicateSentences(text)
        words = text.split()
        if len(words) > 45:
            text = " ".join(words[:45]).rstrip(" ,;") + "."
        return self.normalizeText(text)

    def _clean_project_title(self, value: Any) -> str:
        title = self.removeUrls(value)
        title = re.sub(r"\b(?:project|github|tech stack|technologies|tools)\s*[:\-]\s*", "", title, flags=re.IGNORECASE)
        title = re.sub(
            r"^(?:JavaScript|HTML|CSS|React|Python|C\+\+|Java|Firebase|FastAPI|MongoDB|SQL|Node\.?js)\s+",
            "",
            title,
            flags=re.IGNORECASE,
        )
        title = re.sub(r"\b(?:built|developed|implemented|created)\b.*$", "", title, flags=re.IGNORECASE)
        return self.normalizeText(title)[:90]

    def _project_quality_score(self, project: Dict[str, Any]) -> int:
        title = self.normalizeText(project.get("title", ""))
        description = self.normalizeText(project.get("description", ""))
        score = 0
        if 2 <= len(title.split()) <= 8:
            score += 7
        if len(title.split()) > 9:
            score -= 6
        if re.search(r"\b(?:built|developed|implemented|created|operations|demonstrated)\b", title, re.IGNORECASE):
            score -= 5
        if re.search(r"\b(?:JavaScript|HTML|CSS|React|Python|C\+\+|Firebase|FastAPI|MongoDB)\b", title, re.IGNORECASE):
            score -= 2
        if 8 <= len(description.split()) <= 55:
            score += 5
        if re.search(r"\b(?:github|http|tech stack|technologies)\b", title + " " + description, re.IGNORECASE):
            score -= 8
        return score

    def _text_similarity(self, left: str, right: str) -> float:
        stop = {
            "the", "and", "with", "that", "this", "from", "for", "used", "using",
            "html", "css", "javascript", "react", "python", "java", "project",
        }
        left_tokens = {
            token for token in re.findall(r"[a-z0-9]+", left.lower())
            if len(token) > 2 and token not in stop
        }
        right_tokens = {
            token for token in re.findall(r"[a-z0-9]+", right.lower())
            if len(token) > 2 and token not in stop
        }
        if not left_tokens or not right_tokens:
            return 0
        return len(left_tokens & right_tokens) / min(len(left_tokens), len(right_tokens))

    def deduplicateEducation(self, education: List[Any]) -> List[Dict[str, str]]:
        unique = {}
        for item in education or []:
            if isinstance(item, dict):
                record = {
                    "degree": self.normalizeText(item.get("degree", "")),
                    "institution": self.normalizeText(item.get("institution", "")),
                    "year": self.normalizeText(item.get("year", "")),
                    "score": self.normalizeText(item.get("score", "")),
                }
            else:
                text = self.normalizeText(item)
                record = {"degree": text, "institution": "", "year": "", "score": ""}

            if not any(record.values()):
                continue

            degree_key = re.sub(r"[^a-z0-9]+", "", record["degree"].lower())
            year_key = re.sub(r"[^0-9]+", "", record["year"])
            score_key = re.sub(r"[^0-9.]+", "", record["score"])
            institution_key = re.sub(r"[^a-z0-9]+", "", record["institution"].lower())[:18]
            key = f"{degree_key}|{year_key}|{score_key or institution_key}"
            unique.setdefault(key, record)
        return list(unique.values())

    def deduplicateProjects(self, projects: List[Any]) -> List[Dict[str, Any]]:
        unique: Dict[str, Dict[str, Any]] = {}
        for item in projects or []:
            if isinstance(item, dict):
                raw_title = item.get("title") or item.get("name") or ""
                raw_description = item.get("description") or item.get("summary") or item.get("impact") or ""
                if not raw_description:
                    raw_description = " ".join(
                        str(item.get(field, ""))
                        for field in ["title", "technologies", "role"]
                        if item.get(field)
                    )
            else:
                raw_title = ""
                raw_description = str(item)

            title = self._clean_project_title(raw_title)

            description = self.cleanProjectDescription(raw_description, title)
            if not title and description:
                title = self.normalizeText(re.split(r"[:.]", description, maxsplit=1)[0])[:80]
                title = self._clean_project_title(title)
                description = self.cleanProjectDescription(description, title)
            if not title and not description:
                continue

            record = {
                "title": title or "Project",
                "description": description,
                "technologies": [],
                "impact": "",
                "role": "",
            }
            record_text = f"{record['title']} {record['description']}"
            record_score = self._project_quality_score(record)
            replaced = False

            for key, existing in list(unique.items()):
                existing_text = f"{existing['title']} {existing['description']}"
                same_title = self._text_similarity(record["title"], existing["title"]) >= 0.75
                same_content = self._text_similarity(record_text, existing_text) >= 0.45
                if same_title or same_content:
                    if record_score > self._project_quality_score(existing):
                        unique[key] = record
                    replaced = True
                    break

            if not replaced:
                key = re.sub(r"[^a-z0-9]+", "", record_text.lower())[:220]
                unique[key] = record

        return sorted(unique.values(), key=self._project_quality_score, reverse=True)

    def deduplicateSkills(self, skills: Any) -> Dict[str, List[str]]:
        schema = self.validate_resume_json({})["skills"]
        if isinstance(skills, list):
            skills = {"tools": skills}
        if not isinstance(skills, dict):
            return schema

        cleaned = {}
        for category in schema:
            values = skills.get(category, [])
            if not isinstance(values, list):
                values = []
            seen = set()
            cleaned[category] = []
            for value in values:
                skill = self.normalizeText(value)
                key = skill.lower()
                if skill and key not in seen:
                    seen.add(key)
                    cleaned[category].append(skill)
        return cleaned

    def _deduplicate_text_list(self, values: List[Any]) -> List[str]:
        seen = set()
        result = []
        for value in values or []:
            text = self.removeDuplicateSentences(self.removeUrls(value))
            key = re.sub(r"[^a-z0-9]+", "", text.lower())
            if text and key not in seen:
                seen.add(key)
                result.append(text)
        return result

    def clean_resume_analysis_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = self.validate_resume_json(data or {})
        cleaned["education"] = self.deduplicateEducation(cleaned.get("education", []))
        cleaned["projects"] = self.deduplicateProjects(cleaned.get("projects", []))
        cleaned["skills"] = self.deduplicateSkills(cleaned.get("skills", {}))
        cleaned["certifications"] = self._deduplicate_text_list(cleaned.get("certifications", []))
        cleaned["achievements"] = self._deduplicate_text_list(cleaned.get("achievements", []))
        cleaned["interviewTopics"] = self._deduplicate_text_list(cleaned.get("interviewTopics", []))
        return cleaned

    def _extract_candidate_name(self, text: str) -> str:
        first_chunk = re.split(r'\b(?:EDUCATION|SKILLS|EXPERIENCE|PROJECTS|CERTIFICATIONS)\b', text, flags=re.IGNORECASE)[0]
        candidates = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}\b', first_chunk[:500])
        blocked = {"Computer Science", "Software Engineer", "Full Stack", "Machine Learning"}
        for candidate in candidates:
            if candidate not in blocked and "University" not in candidate and "College" not in candidate:
                return candidate
        return ""

    def _extract_contact_info_sync(self, text: str) -> Dict[str, str]:
        contact = {}
        email = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text)
        phone = re.search(r'(?<!cid:)(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3,5}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{4,6}', text)
        linkedin = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
        github = re.search(r'(?:https?://)?(?:www\.)?github\.com/[\w-]+', text, re.IGNORECASE)
        portfolio = re.search(r'https?://(?!.*(?:linkedin|github))[\w.-]+\.[A-Za-z]{2,}(?:/[^\s]*)?', text, re.IGNORECASE)
        if email:
            contact["email"] = email.group(0)
        if phone:
            digits = re.sub(r'\D', '', phone.group(0))
            contact["phone"] = digits[-10:] if len(digits) >= 10 else phone.group(0).strip()
        if linkedin:
            contact["linkedin"] = self._ensure_url(linkedin.group(0))
        if github:
            contact["github"] = self._ensure_url(github.group(0))
        if portfolio:
            contact["portfolio"] = portfolio.group(0)
        return contact

    def _extract_categorized_skills(self, text: str, skills_section: str = "") -> Dict[str, List[str]]:
        source = f"{skills_section}\n{text}".lower()
        catalog = {
            "programmingLanguages": ["Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "PHP", "Ruby", "Kotlin", "Swift", "HTML", "CSS"],
            "frameworks": ["React", "Vue", "Angular", "Node.js", "Express", "Django", "Flask", "Spring", "Laravel", "Next.js", "Tailwind"],
            "databases": ["SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "Firebase", "Firestore", "SQLite"],
            "aiMlSkills": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy"],
            "tools": ["Git", "GitHub", "VS Code", "Overleaf", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Jenkins", "Postman", "Figma", "Linux"],
            "softSkills": ["Leadership", "Communication", "Teamwork", "Problem Solving", "Collaboration", "Adaptability"]
        }
        found = {}
        for category, values in catalog.items():
            found[category] = []
            for skill in values:
                pattern = r'(?<![A-Za-z0-9+#.])' + re.escape(skill.lower()) + r'(?![A-Za-z0-9+#.])'
                if re.search(pattern, source):
                    found[category].append(skill)
        return found

    def _extract_education_records(self, section: str) -> List[Dict[str, str]]:
        records = []
        if not section.strip():
            return records
        lines = [line.strip() for line in section.splitlines() if line.strip()]
        degree_start = re.compile(r'(Bachelor|Master|PhD|MBA|B\.?\s?Tech|M\.?\s?Tech|B\.?E\.?|M\.?E\.?|B\.?S\.?|M\.?S\.?|BCA|MCA|Diploma|Higher Secondary|Class XII)', re.IGNORECASE)
        i = 0
        while i < len(lines):
            line = lines[i]
            if not degree_start.search(line):
                i += 1
                continue

            chunk = [line]
            i += 1
            while i < len(lines) and not degree_start.search(lines[i]):
                chunk.append(lines[i])
                i += 1

            text = " ".join(chunk)
            degree = chunk[0]
            institution = self._first_match(r'([A-Z][A-Za-z&.\s]{2,}(?:University|College|Institute|School|Council|Board)[A-Za-z&.\s]*)', text)
            board = self._first_match(r'Board:\s*([^,]+?)(?:\s+Percentage|\s+CGPA|$)', text)
            year_range = self._first_match(r'\b(20\d{2}\s*[–-]\s*(?:20\d{2}|Present|Current))\b', text)
            year = year_range or self._first_match(r'\b(20\d{2}|19\d{2})\b', text)
            score = self._first_match(r'\b(?:CGPA|GPA|Percentage|Score)[:\s-]*([0-9.]+%?)', text, group=1)
            records.append({
                "degree": degree,
                "institution": institution or board,
                "year": year,
                "score": score
            })
        return records[:6]

    def _extract_experience_records(self, section: str) -> List[Dict[str, Any]]:
        records = []
        lines = [line.strip() for line in section.splitlines() if line.strip()]
        if lines and any("intern" in line.lower() for line in lines[:2]):
            first = lines[0]
            role = self._first_match(r'\b[A-Za-z ]*Intern\b[A-Za-z ]*', first, flags=re.IGNORECASE) or "Intern"
            company = self._first_match(r'Intern\s+[–-]\s*([^(\n]+)', first, group=1, flags=re.IGNORECASE)
            duration = self._first_match(r'(\d{1,2}\s+[A-Za-z]{3,}\s*[–-]\s*\d{1,2}\s+[A-Za-z]{3,})', first)
            records.append({
                "role": role.strip(),
                "company": company.strip(),
                "duration": duration,
                "responsibilities": lines[1:5]
            })
            return records
        for chunk in self._split_section_items(section):
            role = self._first_match(r'\b(?:Intern|Trainee|Developer|Engineer|Analyst|Manager|Designer|Consultant|Lead|Associate)[A-Za-z\s-]*', chunk)
            company = self._first_match(r'(?:at|@)\s*([A-Z][A-Za-z0-9&.\s-]{2,})', chunk, group=1)
            duration = self._first_match(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\.?\s*20\d{2}\s*[-–]\s*(?:Present|Current|20\d{2}))', chunk)
            responsibilities = self._extract_bullets(chunk)
            if role or company or responsibilities:
                records.append({
                    "role": role,
                    "company": company,
                    "duration": duration,
                    "responsibilities": responsibilities[:4]
                })
        return records[:6]

    def _extract_project_records(self, section: str) -> List[Dict[str, Any]]:
        records = []
        for chunk in self._project_chunks(section):
            title = self._first_match(r'^([^:]{3,90}):', chunk.strip())
            description = self.cleanProjectDescription(chunk, title)
            if title or description:
                records.append({
                    "title": self.removeUrls(title) or description[:60],
                    "description": description,
                    "technologies": [],
                    "impact": "",
                    "role": ""
                })
        return self.deduplicateProjects(records)[:8]

    def _project_chunks(self, section: str) -> List[str]:
        lines = [line.strip() for line in section.splitlines() if line.strip()]
        chunks = []
        current = []
        title_line = re.compile(r'^[A-Z][A-Za-z0-9 &/().-]{3,90}:')
        stop_headings = {"Research & Publications", "Research and Publications"}
        for line in lines:
            if line in stop_headings:
                if current:
                    chunks.append(" ".join(current))
                    current = []
                continue
            if title_line.search(line):
                if current:
                    chunks.append(" ".join(current))
                current = [line]
            elif current:
                current.append(line)
        if current:
            chunks.append(" ".join(current))
        if not chunks:
            return self._split_section_items(section)
        return chunks

    def _extract_list_section(self, section: str) -> List[str]:
        return self._split_section_items(section)[:10]

    def _split_section_items(self, section: str) -> List[str]:
        if not section or not section.strip():
            return []
        normalized = section.replace("•", "\n").replace("·", "\n")
        items = re.split(r'\n+|(?<=\.)\s+(?=[A-Z][A-Za-z0-9 ]{2,}:?)', normalized)
        cleaned = [re.sub(r'^[\-\*\u2022\d.)\s]+', '', item).strip(" ;,") for item in items]
        return [item for item in cleaned if len(item) > 8]

    def _extract_bullets(self, text: str) -> List[str]:
        items = self._split_section_items(text)
        return [item for item in items if len(item.split()) >= 4]

    def _extract_flat_skills(self, text: str) -> List[str]:
        categorized = self._extract_categorized_skills(text)
        skills = []
        for values in categorized.values():
            skills.extend(values)
        return list(dict.fromkeys(skills))

    def _build_local_summary(self, text: str, data: Dict[str, Any]) -> str:
        skills = []
        for values in data.get("skills", {}).values():
            skills.extend(values)
        parts = []
        if data.get("candidateName"):
            parts.append(data["candidateName"])
        if skills:
            parts.append("Skills: " + ", ".join(skills[:8]))
        if data.get("projects"):
            parts.append(f"{len(data['projects'])} project(s) identified")
        if data.get("experience"):
            parts.append(f"{len(data['experience'])} experience item(s) identified")
        return ". ".join(parts) or text[:300]

    def _build_interview_topics(self, data: Dict[str, Any]) -> List[str]:
        topics = []
        for values in data.get("skills", {}).values():
            topics.extend(values[:4])
        topics.extend([project.get("title", "") for project in data.get("projects", []) if isinstance(project, dict)])
        return [topic for topic in dict.fromkeys(topics) if topic][:12]

    def _merge_lists(self, base: List[Any], extra: List[Any]) -> List[Any]:
        merged = []
        seen = set()
        for item in (base or []) + (extra or []):
            key = json.dumps(item, sort_keys=True) if isinstance(item, (dict, list)) else str(item)
            if item and key not in seen:
                seen.add(key)
                merged.append(item)
        return merged

    def _merge_skill_dicts(self, base: Dict[str, List[str]], extra: Dict[str, List[str]]) -> Dict[str, List[str]]:
        schema = self.validate_resume_json({})["skills"]
        merged = {}
        for key in schema:
            merged[key] = []
            for source in [base or {}, extra or {}]:
                values = source.get(key, []) if isinstance(source, dict) else []
                for value in values:
                    if value and value not in merged[key]:
                        merged[key].append(value)
        return merged

    def _first_match(self, pattern: str, text: str, group: int = 0, flags: int = 0) -> str:
        match = re.search(pattern, text or "", flags)
        return match.group(group).strip() if match else ""

    def _ensure_url(self, value: str) -> str:
        return value if value.startswith("http") else f"https://{value}"
    
    async def extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from resume text"""
        text_lower = text.lower()
        found_skills = set()
        
        for category, skills in self.tech_skills.items():
            for skill in skills:
                if skill in text_lower:
                    found_skills.add(skill.title())
        
        patterns = [
            r'\b(?:react|vue|angular|node|express|django|flask)\b',
            r'\b(?:aws|azure|gcp|docker|kubernetes)\b',
            r'\b(?:python|java|javascript|typescript|c\+\+|c#)\b',
            r'\b(?:sql|mysql|postgresql|mongodb|redis)\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            found_skills.update([match.title() for match in matches])
        
        return sorted(list(found_skills))
    
    async def extract_experience(self, text: str) -> List[str]:
        """Extract work experience information"""
        experiences = []
        
        experience_patterns = [
            r'(\d{1,2}\+?\s*years?\s*(?:of\s*)?experience)',
            r'([A-Z][a-z]+\s+(?:Inc|Corp|LLC|Ltd|Company))',
            r'(\b(?:Senior|Junior|Lead|Principal|Staff)\s+[A-Za-z\s]+)',
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            experiences.extend(matches)
        
        return list(set(experiences))[:10]
    
    async def extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        education = []
        
        education_patterns = [
            r'(Bachelor|Master|PhD|MBA|B\.S\.|M\.S\.|B\.Tech|M\.Tech)',
            r'(?:University|College|Institute|School)\s+(?:of\s+)?([A-Za-z\s]+)',
            r'(GPA|CGPA)[\s:]*(\d+\.\d+)',
        ]
        
        for pattern in education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            education.extend([str(match) for match in matches])
        
        return list(set(education))
    
    async def extract_projects(self, text: str) -> List[str]:
        """Extract project information"""
        projects = []
        
        project_patterns = [
            r'(?:Project|Portfolio)[:\s]+([A-Za-z\s]+)',
            r'(?:Developed|Built|Created)\s+([A-Za-z\s]+)(?:application|system|platform)',
        ]
        
        for pattern in project_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            projects.extend(matches)
        
        # Extract sentences that mention project-related keywords
        sentences = sent_tokenize(text)
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in ['project', 'developed', 'built', 'created', 'implemented']):
                if len(sentence) > 20:
                    projects.append(sentence.strip())
        
        return projects[:5]
    
    async def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information"""
        contact_info = {}
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = '-'.join(phones[0])
        
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin:
            contact_info['linkedin'] = f"https://{linkedin[0]}"
        
        return contact_info
    
    async def generate_summary(self, text: str) -> str:
        """Generate a brief summary of the resume"""
        sentences = sent_tokenize(text)
        
        if len(sentences) > 3:
            summary = ' '.join(sentences[:3])
        else:
            summary = text[:500] + '...' if len(text) > 500 else text
        
        return summary
    
    async def extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from resume"""
        words = word_tokenize(text.lower())
        words = [word for word in words if word.isalpha() and word not in stopwords.words('english')]
        
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer(max_features=20, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            keyword_scores = list(zip(feature_names, tfidf_scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            keywords = [keyword for keyword, score in keyword_scores[:15]]
        except:
            from collections import Counter
            word_freq = Counter(words)
            keywords = [word for word, freq in word_freq.most_common(15)]
        
        return keywords
