import requests
import json
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

from utils.logger import log_error, log_ai_interaction, log_api_call
from utils.exceptions import AIServiceError, ValidationError
from services.gemini_service import GeminiService

class JobInsightsService:
    """Enhanced job insights service with real API integration and company-specific filtering"""
    
    def __init__(self):
        self.the_muse_api_key = os.getenv("THE_MUSE_API_KEY")
        self.adzuna_app_id = os.getenv("ADZUNA_APP_ID")
        self.adzuna_api_key = os.getenv("ADZUNA_API_KEY")
        self.adzuna_country = os.getenv("ADZUNA_COUNTRY", "us")
        self.base_url = "https://www.themuse.com/api/public"
        self.gemini_service = GeminiService()
        self.logger = logging.getLogger(__name__)
        
        # Role to category mapping for The Muse API
        self.role_categories = {
            "Software Engineer": "Software Engineering",
            "Frontend Developer": "Software Engineering", 
            "Backend Developer": "Software Engineering",
            "Full Stack Developer": "Software Engineering",
            "Product Manager": "Product Management",
            "Data Scientist": "Data Science",
            "Data Analyst": "Data Science",
            "DevOps Engineer": "Engineering",
            "UI/UX Designer": "Design",
            "Marketing Manager": "Marketing",
            "Sales Manager": "Sales"
        }
        
        # Mock job data for development
        self.mock_job_data = {
            'Software Engineer': {
                'skills': ['JavaScript', 'Python', 'React', 'Node.js', 'Git', 'SQL', 'AWS', 'Docker'],
                'responsibilities': [
                    'Develop and maintain web applications using modern frameworks',
                    'Write clean, scalable, and well-documented code',
                    'Collaborate with cross-functional teams to define requirements',
                    'Participate in code reviews and maintain code quality',
                    'Troubleshoot and debug applications',
                    'Optimize application performance and scalability'
                ],
                'requirements': [
                    'Bachelor\'s degree in Computer Science or related field',
                    '3+ years of experience in software development',
                    'Proficiency in at least one modern programming language',
                    'Experience with version control systems',
                    'Strong problem-solving skills',
                    'Excellent communication and teamwork abilities'
                ],
                'salary_range': '$80,000 - $150,000',
                'growth_potential': 'High',
                'work_environment': 'Collaborative, fast-paced, innovative'
            },
            'Product Manager': {
                'skills': ['Product Strategy', 'Data Analysis', 'User Research', 'Agile', 'Communication', 'Roadmapping'],
                'responsibilities': [
                    'Define product vision and strategy',
                    'Conduct market research and user interviews',
                    'Create and maintain product roadmaps',
                    'Work with engineering teams to deliver features',
                    'Analyze product metrics and user feedback',
                    'Collaborate with stakeholders across the organization'
                ],
                'requirements': [
                    '5+ years of product management experience',
                    'Strong analytical and data-driven mindset',
                    'Experience with agile development methodologies',
                    'Excellent communication and presentation skills',
                    'Ability to work with technical and non-technical teams',
                    'MBA or equivalent experience preferred'
                ],
                'salary_range': '$100,000 - $180,000',
                'growth_potential': 'Very High',
                'work_environment': 'Strategic, collaborative, customer-focused'
            },
            'Data Scientist': {
                'skills': ['Python', 'Machine Learning', 'Statistics', 'SQL', 'TensorFlow', 'Data Visualization', 'R'],
                'responsibilities': [
                    'Develop machine learning models and algorithms',
                    'Analyze large datasets to extract insights',
                    'Create data visualizations and reports',
                    'Work with stakeholders to understand business needs',
                    'Implement and deploy ML solutions',
                    'Stay updated with latest ML research and techniques'
                ],
                'requirements': [
                    'Advanced degree in Computer Science, Statistics, or related field',
                    '3+ years of experience in data science or machine learning',
                    'Proficiency in Python and ML frameworks',
                    'Strong statistical and mathematical background',
                    'Experience with big data technologies',
                    'Excellent problem-solving abilities'
                ],
                'salary_range': '$90,000 - $160,000',
                'growth_potential': 'Very High',
                'work_environment': 'Research-oriented, analytical, innovative'
            }
        }
    
    async def get_job_insights(self, company: str, role: str, location: str) -> Dict[str, Any]:
        """Get comprehensive job insights for a specific role and company"""
        try:
            # Always try real API first
            real_insights = await self._fetch_from_api(company, role, location)
            if real_insights:
                return real_insights
            
            adzuna_insights = await self._fetch_from_adzuna(company, role, location)
            if adzuna_insights:
                return adzuna_insights

            return self._low_confidence_insights(company, role, location, "no_matching_sources")
            
        except Exception as e:
            log_error(e, "Job insights fetching")
            return self._low_confidence_insights(company, role, location, "source_error")
    
    async def _fetch_from_api(self, company: str, role: str, location: str) -> Dict[str, Any]:
        """Fetch real job data from The Muse API"""
        try:
            # Search for jobs with multiple strategies
            all_jobs = []
            
            # Strategy 1: Search by company
            try:
                company_url = f"{self.base_url}/jobs"
                company_params = {
                    'page': 1,
                    'descending': True,
                    'company': company,
                    'location': location
                }
                
                response = requests.get(company_url, params=company_params)
                if response.status_code == 200:
                    data = response.json()
                    company_jobs = data.get('results', [])
                    all_jobs.extend(company_jobs)
                    
            except Exception as e:
                self.logger.warning(f"Company search failed: {e}")
            
            # Strategy 2: Search by role keywords
            try:
                role_keywords = role.lower().replace(' ', '+')
                role_url = f"{self.base_url}/jobs"
                role_params = {
                    'page': 1,
                    'descending': True,
                    'location': location
                }
                
                response = requests.get(role_url, params=role_params)
                if response.status_code == 200:
                    data = response.json()
                    role_jobs = data.get('results', [])
                    all_jobs.extend(role_jobs)
                    
            except Exception as e:
                self.logger.warning(f"Role search failed: {e}")
            
            if all_jobs:
                # Filter jobs by company and role match
                filtered_jobs = []
                company_lower = company.lower()
                role_lower = role.lower()
                
                for job in all_jobs:
                    job_title = job.get('name', '').lower()
                    job_company = job.get('company', {}).get('name', '').lower()
                    
                    # Check if job matches both company and role
                    company_match = company_lower in job_company or job_company in company_lower
                    role_match = any(keyword in job_title for keyword in role_lower.split())
                    
                    if company_match or role_match:
                        job['match_score'] = (10 if company_match else 0) + (10 if role_match else 0)
                        filtered_jobs.append(job)
                
                if filtered_jobs:
                    # Sort by match score
                    filtered_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
                    
                    # Extract insights from matching jobs
                    insights = self._extract_insights_from_jobs(filtered_jobs, role, company)
                    insights['sourceCount'] = len(filtered_jobs)
                    insights['sourceLinks'] = [f"https://www.themuse.com/jobs/{job.get('id')}" for job in filtered_jobs[:5]]
                    insights['confidenceWarning'] = insights.get('confidence', 0) < 50
                    insights['warningMessage'] = "Please paste job description for better accuracy." if insights['confidenceWarning'] else ""
                    
                    log_api_call(
                        endpoint=f"{self.base_url}/jobs",
                        method="GET",
                        user_id="system",
                        request_data={"company": company, "role": role, "location": location},
                        response_data={"jobs_found": len(filtered_jobs), "confidence": "high"}
                    )
                    
                    return insights
            
        except Exception as e:
            log_error(e, "Job API fetching")
        
        return None

    async def _fetch_from_adzuna(self, company: str, role: str, location: str) -> Optional[Dict[str, Any]]:
        """Fetch real job data from Adzuna when credentials are configured."""
        if not self.adzuna_app_id or not self.adzuna_api_key:
            return None

        try:
            url = f"https://api.adzuna.com/v1/api/jobs/{self.adzuna_country}/search/1"
            params = {
                "app_id": self.adzuna_app_id,
                "app_key": self.adzuna_api_key,
                "what": role,
                "where": location,
                "results_per_page": 25,
                "content-type": "application/json",
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return None

            jobs = response.json().get("results", [])
            filtered = []
            company_lower = company.lower()
            role_terms = set(role.lower().split())
            for job in jobs:
                title = job.get("title", "").lower()
                org = job.get("company", {}).get("display_name", "").lower()
                description = job.get("description", "")
                company_match = company_lower and (company_lower in org or org in company_lower)
                role_match = bool(role_terms & set(title.split()))
                if company_match or role_match:
                    filtered.append({
                        "name": job.get("title", ""),
                        "company": {"name": job.get("company", {}).get("display_name", "")},
                        "contents": description,
                        "id": job.get("id"),
                        "redirect_url": job.get("redirect_url"),
                        "match_score": (10 if company_match else 0) + (10 if role_match else 0),
                    })

            if not filtered:
                return None

            filtered.sort(key=lambda item: item.get("match_score", 0), reverse=True)
            insights = self._extract_insights_from_jobs(filtered, role, company)
            insights["source"] = "adzuna"
            insights["sourceCount"] = len(filtered)
            insights["sourceLinks"] = [job.get("redirect_url") for job in filtered[:5] if job.get("redirect_url")]
            insights["confidenceWarning"] = insights.get("confidence", 0) < 50
            insights["warningMessage"] = "Please paste job description for better accuracy." if insights["confidenceWarning"] else ""
            return insights
        except Exception as e:
            self.logger.warning(f"Adzuna search failed: {e}")
            return None
    
    def _extract_insights_from_jobs(self, jobs: List[Dict], target_role: str, target_company: str) -> Dict[str, Any]:
        """Extract insights from job listings"""
        all_skills = []
        all_responsibilities = []
        all_requirements = []
        matched_companies = []
        matched_roles = []
        
        for job in jobs:
            job_title = job.get('name', '').lower()
            job_company = job.get('company', {}).get('name', '').lower()
            
            # Track matched companies and roles
            if target_company.lower() in job_company or job_company in target_company.lower():
                matched_companies.append(job_company)
            
            if target_role.lower() in job_title or any(keyword in job_title for keyword in target_role.lower().split()):
                matched_roles.append(job_title)
            
            # Extract skills from job description
            contents = job.get('contents', '')
            if contents:
                skills = self._extract_skills_from_text(contents)
                all_skills.extend(skills)
                
                # Extract responsibilities and requirements
                categories = job.get('categories', [])
                for category in categories:
                    if category.get('name') == 'Responsibilities':
                        all_responsibilities.extend(category.get('subcategories', []))
                    elif category.get('name') == 'Requirements':
                        all_requirements.extend(category.get('subcategories', []))
        
        # Calculate confidence based on matches
        company_confidence = min(100, len(matched_companies) * 20)
        role_confidence = min(100, len(matched_roles) * 20)
        overall_confidence = (company_confidence + role_confidence) / 2
        
        return {
            'company': target_company,
            'role': target_role,
            'location': '',  # Will be set by caller
            'matchedJobTitles': list(set(matched_roles))[:5],
            'sourceCount': len(jobs),
            'requiredSkills': list(set(all_skills))[:15],
            'preferredSkills': list(set(all_skills))[15:30],
            'tools': list(set(all_skills))[30:45],
            'responsibilities': all_responsibilities[:8],
            'experienceLevel': self._determine_experience_level(target_role),
            'interviewTopics': self._generate_interview_topics(target_role, all_skills),
            'companySpecificExpectations': self._get_company_expectations(target_company),
            'confidence': overall_confidence,
            'sourceLinks': [f"https://www.themuse.com/jobs/{job.get('id')}" for job in jobs[:3]],
            'confidenceWarning': overall_confidence < 50,
            'warningMessage': "Please paste job description for better accuracy." if overall_confidence < 50 else ""
        }

    def _low_confidence_insights(self, company: str, role: str, location: str, source: str) -> Dict[str, Any]:
        """Return transparent empty insights instead of hallucinated job data."""
        return {
            "company": company,
            "role": role,
            "location": location,
            "matchedJobTitles": [],
            "requiredSkills": [],
            "preferredSkills": [],
            "tools": [],
            "responsibilities": [],
            "requirements": [],
            "experienceLevel": self._determine_experience_level(role),
            "interviewTopics": [],
            "companySpecificExpectations": [],
            "sourceCount": 0,
            "sourceLinks": [],
            "confidence": 0,
            "source": source,
            "confidenceWarning": True,
            "warningMessage": "Please paste job description for better accuracy."
        }
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract technical skills from job description text"""
        common_skills = [
            'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'AWS',
            'Docker', 'Git', 'Agile', 'Scrum', 'REST API', 'MongoDB', 'PostgreSQL',
            'Machine Learning', 'TensorFlow', 'PyTorch', 'Data Analysis', 'Tableau'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _determine_experience_level(self, role: str) -> str:
        """Determine experience level based on role"""
        junior_roles = ['junior', 'entry', 'associate', 'intern']
        senior_roles = ['senior', 'lead', 'principal', 'staff', 'sr']
        
        role_lower = role.lower()
        if any(jr in role_lower for jr in junior_roles):
            return 'Junior (0-2 years)'
        elif any(sr in role_lower for sr in senior_roles):
            return 'Senior (5+ years)'
        else:
            return 'Mid-level (2-5 years)'
    
    def _generate_interview_topics(self, role: str, skills: List[str]) -> List[str]:
        """Generate interview topics based on role and skills"""
        topics = []
        
        # Role-specific topics
        if 'engineer' in role.lower():
            topics.extend(['System Design', 'Algorithms', 'Data Structures', 'Problem Solving'])
        elif 'manager' in role.lower():
            topics.extend(['Leadership', 'Project Management', 'Team Collaboration', 'Strategic Planning'])
        elif 'designer' in role.lower():
            topics.extend(['UI/UX Principles', 'User Research', 'Design Systems', 'Prototyping'])
        elif 'data' in role.lower():
            topics.extend(['Data Analysis', 'Machine Learning', 'Statistics', 'Data Visualization'])
        
        # Skill-specific topics
        if 'Python' in skills:
            topics.append('Python Programming')
        if 'React' in skills:
            topics.append('React Development')
        if 'AWS' in skills:
            topics.append('Cloud Computing')
        
        return list(set(topics))[:8]
    
    def _get_company_expectations(self, company: str) -> List[str]:
        """Get company-specific expectations"""
        company_expectations = {
            'google': ['Innovation', 'Technical Excellence', 'Collaboration', 'Scale'],
            'microsoft': ['Professionalism', 'Enterprise Solutions', 'Security', 'Reliability'],
            'amazon': ['Customer Obsession', 'Ownership', 'Bias for Action', 'Deliver Results'],
            'apple': ['Design Excellence', 'User Privacy', 'Innovation', 'Quality'],
            'microsoft': ['Team Collaboration', 'Growth Mindset', 'Enterprise Solutions'],
            'netflix': ['Freedom & Responsibility', 'Context not Control', 'High Performance']
        }
        
        return company_expectations.get(company.lower(), ['Professionalism', 'Technical Skills', 'Teamwork'])
    
    async def _get_mock_insights(self, company: str, role: str, location: str) -> Dict[str, Any]:
        """Get mock job insights when API is not available"""
        # Find matching role or use default
        role_key = None
        for key in self.mock_job_data:
            if key.lower() in role.lower() or role.lower() in key.lower():
                role_key = key
                break
        
        if not role_key:
            role_key = 'Software Engineer'  # Default
        
        base_insights = self.mock_job_data[role_key].copy()
        
        # Customize for company
        company_specific = self._get_company_specific_insights(company)
        base_insights.update(company_specific)
        
        # Adjust for location
        location_adjustment = self._get_location_adjustment(location)
        base_insights['salary_range'] = self._adjust_salary(base_insights['salary_range'], location_adjustment)
        
        return base_insights
    
    def _get_company_specific_insights(self, company: str) -> Dict[str, Any]:
        """Get company-specific insights"""
        company_insights = {
            'Google': {
                'additional_skills': ['Go', 'Kubernetes', 'TensorFlow', 'BigQuery'],
                'culture': 'Innovative, data-driven, collaborative',
                'benefits': 'Excellent health benefits, free meals, gym access'
            },
            'Microsoft': {
                'additional_skills': ['.NET', 'Azure', 'C#', 'Power BI'],
                'culture': 'Professional, growth-oriented, team-focused',
                'benefits': 'Great healthcare, stock options, work-life balance'
            },
            'Amazon': {
                'additional_skills': ['AWS', 'Lambda', 'DynamoDB', 'S3'],
                'culture': 'Customer-obsessed, fast-paced, leadership principles',
                'benefits': 'Competitive salary, career growth, global impact'
            },
            'Apple': {
                'additional_skills': ['Swift', 'iOS', 'macOS', 'Objective-C'],
                'culture': 'Design-focused, innovative, detail-oriented',
                'benefits': 'Premium healthcare, product discounts, creative environment'
            }
        }
        
        return company_insights.get(company, {
            'additional_skills': [],
            'culture': 'Professional, innovative, collaborative',
            'benefits': 'Competitive benefits package'
        })
    
    def _get_location_adjustment(self, location: str) -> float:
        """Get salary adjustment factor based on location"""
        location_multipliers = {
            'San Francisco': 1.4,
            'New York': 1.3,
            'Seattle': 1.2,
            'Austin': 1.1,
            'Boston': 1.15,
            'Los Angeles': 1.25,
            'Chicago': 1.1,
            'Denver': 1.05,
            'Remote': 1.0
        }
        
        for loc, multiplier in location_multipliers.items():
            if loc.lower() in location.lower():
                return multiplier
        
        return 1.0  # Default multiplier
    
    def _adjust_salary(self, salary_range: str, multiplier: float) -> str:
        """Adjust salary range based on location multiplier"""
        try:
            # Parse salary range
            range_parts = salary_range.replace('$', '').replace(',', '').split(' - ')
            if len(range_parts) == 2:
                low = int(range_parts[0]) * multiplier
                high = int(range_parts[1]) * multiplier
                return f"${int(low):,} - ${int(high):,}"
        except:
            pass
        
        return salary_range
    
    async def search_jobs(self, query: str, location: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for jobs using query and location"""
        try:
            if self.the_muse_api_key:
                # Try real API search
                search_url = f"{self.base_url}/jobs"
                params = {
                    'page': 1,
                    'descending': True,
                    'location': location
                }
                
                response = requests.get(search_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    jobs = data.get('results', [])
                    
                    # Filter by query
                    filtered_jobs = []
                    for job in jobs:
                        if query.lower() in job.get('name', '').lower():
                            filtered_jobs.append({
                                'id': job.get('id'),
                                'title': job.get('name'),
                                'company': job.get('company', {}).get('name'),
                                'location': job.get('locations', [{}])[0].get('name'),
                                'publication_date': job.get('publication_date'),
                                'categories': job.get('categories', [])
                            })
                    
                    return filtered_jobs[:limit]
            
            # Fallback to mock search results
            return self._get_mock_search_results(query, location, limit)
            
        except Exception as e:
            print(f"Error searching jobs: {e}")
            return self._get_mock_search_results(query, location, limit)
    
    def _get_mock_search_results(self, query: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """Get mock search results"""
        mock_jobs = [
            {
                'id': '1',
                'title': 'Senior Software Engineer',
                'company': 'TechCorp',
                'location': location,
                'publication_date': '2024-01-15',
                'categories': [{'name': 'Engineering'}, {'name': 'Full Stack'}]
            },
            {
                'id': '2',
                'title': 'Frontend Developer',
                'company': 'WebSolutions',
                'location': location,
                'publication_date': '2024-01-14',
                'categories': [{'name': 'Engineering'}, {'name': 'Frontend'}]
            },
            {
                'id': '3',
                'title': 'Full Stack Developer',
                'company': 'StartupXYZ',
                'location': location,
                'publication_date': '2024-01-13',
                'categories': [{'name': 'Engineering'}, {'name': 'Full Stack'}]
            }
        ]
        
        # Filter by query
        if query:
            mock_jobs = [job for job in mock_jobs if query.lower() in job['title'].lower()]
        
        return mock_jobs[:limit]
