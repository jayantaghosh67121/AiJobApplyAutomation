"""Claude AI integration for job matching and cover letter generation"""

from anthropic import Anthropic
import json
from app.config import settings

client = Anthropic()


def score_job_match(
    resume_text: str,
    job_title: str,
    job_description: str,
    job_company: str,
    user_preferences: dict
) -> dict:
    """
    Use Claude to score how well a job matches a user's resume and preferences.
    
    Returns:
    {
        "match_score": float (0.0-1.0),
        "match_reasons": [list of reasons],
        "required_skills_match": float,
        "preferred_skills_match": float,
        "salary_match": float,
        "location_match": float,
        "recommendation": str
    }
    """
    
    prompt = f"""Analyze how well this job matches the candidate's profile.

CANDIDATE RESUME:
{resume_text}

TARGET ROLES: {', '.join(user_preferences.get('target_roles', []))}
BLACKLIST COMPANIES: {', '.join(user_preferences.get('blacklist_companies', []))}
PREFERRED LOCATIONS: {', '.join(user_preferences.get('preferred_locations', []))}
MIN SALARY: ${user_preferences.get('min_salary', 0)}

JOB POSTING:
Title: {job_title}
Company: {job_company}
Description:
{job_description}

Provide a detailed match analysis in JSON format with:
1. match_score (0.0-1.0): Overall match percentage
2. match_reasons: List of specific reasons for the score
3. required_skills_match (0.0-1.0): How many required skills does the candidate have
4. preferred_skills_match (0.0-1.0): How many preferred skills does the candidate have
5. salary_match (0.0-1.0): Does salary range fit expectations (if mentioned)
6. location_match (0.0-1.0): Does location match preferences
7. recommendation: "APPLY", "CONSIDER", or "SKIP" with brief explanation

Return ONLY valid JSON."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    try:
        # Extract JSON from response
        response_text = message.content[0].text
        # Find JSON in response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        json_str = response_text[start_idx:end_idx]
        result = json.loads(json_str)
        return result
    except (json.JSONDecodeError, IndexError, AttributeError) as e:
        # Fallback if Claude response isn't valid JSON
        return {
            "match_score": 0.5,
            "match_reasons": ["Could not parse AI response"],
            "required_skills_match": 0.5,
            "preferred_skills_match": 0.5,
            "salary_match": 0.5,
            "location_match": 0.5,
            "recommendation": "CONSIDER"
        }


def generate_cover_letter(
    resume_text: str,
    job_title: str,
    job_description: str,
    job_company: str,
    user_name: str
) -> str:
    """Generate a customized cover letter for a job using Claude"""
    
    prompt = f"""Write a professional, compelling cover letter for this job application.

CANDIDATE NAME: {user_name}
CANDIDATE RESUME/BACKGROUND:
{resume_text}

JOB DETAILS:
Position: {job_title}
Company: {job_company}
Description:
{job_description}

Requirements:
- Personalize with specific details from the job posting
- Highlight relevant experience from the resume
- Show enthusiasm for the role and company
- Keep it to 3-4 paragraphs
- Professional tone
- Ready to send via email

Write ONLY the cover letter body, no header."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text.strip()


def tailor_resume(
    original_resume: str,
    job_title: str,
    job_description: str,
    job_company: str
) -> str:
    """Create a tailored resume version for a specific job"""
    
    prompt = f"""Create a tailored resume version optimized for this job opportunity.

ORIGINAL RESUME:
{original_resume}

TARGET JOB:
Position: {job_title}
Company: {job_company}
Description:
{job_description}

Guidelines:
- Reorder experience to highlight most relevant sections first
- Rephrase achievements to match job keywords and requirements
- Remove or de-emphasize irrelevant experience
- Maintain professional formatting
- Keep all important details
- Use action verbs that match job description
- Format as markdown

Return ONLY the tailored resume in markdown format."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text.strip()


def extract_job_keywords(job_description: str) -> dict:
    """Extract key skills and requirements from a job posting"""
    
    prompt = f"""Extract structured information from this job posting:

{job_description}

Return JSON with:
- required_skills: [list of required technical skills]
- preferred_skills: [list of nice-to-have skills]
- experience_years: estimated years of experience needed
- seniority_level: "Junior", "Mid-level", or "Senior"
- key_responsibilities: [top 3-4 main responsibilities]

Return ONLY valid JSON."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=512,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    try:
        response_text = message.content[0].text
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        json_str = response_text[start_idx:end_idx]
        return json.loads(json_str)
    except (json.JSONDecodeError, IndexError):
        return {
            "required_skills": [],
            "preferred_skills": [],
            "experience_years": 0,
            "seniority_level": "Mid-level",
            "key_responsibilities": []
        }
