import os
import json
from google import genai

def analyze_resume(resume_text):
    """
    Analyze the resume for ATS friendliness, strengths, weaknesses,
    and recommend a job title.
    Uses Gemini API if available, else returns mock data.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return _mock_analyze_resume(resume_text)
        
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        Analyze the following text. First, determine if it is a resume.
        If the text is NOT a resume (e.g., a recipe, a generic article, random words), return ONLY this JSON:
        {{
            "is_resume": false,
            "error": "This document does not appear to be a resume. Please upload a valid resume."
        }}
        
        If it IS a resume, provide a JSON response with the following structure:
        {{
            "is_resume": true,
            "ats_score": (integer 0-100),
            "strengths": ["list of 3 key strengths"],
            "weaknesses": ["list of 3 areas for improvement"],
            "recommended_job_title": "Best matching general job title",
            "summary": "A short 2-sentence summary of the candidate's profile",
            "extracted_data": {{
                "name": "extracted name",
                "email": "extracted email",
                "phone": "extracted phone",
                "summary": "A highly improved, professional rewrite of their summary",
                "skills": "extracted hard skills",
                "experience": "extracted and professionally formatted experience",
                "education": "extracted education"
            }}
        }}
        
        Resume text:
        {resume_text}
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        # Parse the JSON response
        # We need to handle potential markdown formatting in the response (e.g., ```json ... ```)
        text_response = response.text
        if text_response.startswith('```json'):
            text_response = text_response[7:-3]
        elif text_response.startswith('```'):
            text_response = text_response[3:-3]
            
        return json.loads(text_response.strip())
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return _mock_analyze_resume(resume_text)

def generate_resume(data):
    """
    Format the resume data as a structured dictionary to be rendered beautifully by the frontend.
    If Gemini API is active, this function rewrites the descriptions professionally, 
    accounting for requested page limits (e.g. keeping content concise for 1-page resumes).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    pages = data.get('pages', 'auto')
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    linkedin = data.get('linkedin', '').strip()
    github = data.get('github', '').strip()
    portfolio = data.get('portfolio', '').strip()
    summary = data.get('summary', '').strip()
    skills = data.get('skills', '').strip()
    soft_skills = data.get('soft_skills', '').strip()
    languages = data.get('languages', '').strip()
    experience = data.get('experience', '').strip()
    internships = data.get('internships', '').strip()
    projects = data.get('projects', '').strip()
    education = data.get('education', '').strip()
    
    if not api_key:
        return {
            'name': name,
            'email': email,
            'phone': phone,
            'linkedin': linkedin,
            'github': github,
            'portfolio': portfolio,
            'summary': summary,
            'skills': skills,
            'soft_skills': soft_skills,
            'languages': languages,
            'experience': experience,
            'internships': internships,
            'projects': projects,
            'education': education,
            'pages': pages
        }
        
    try:
        client = genai.Client(api_key=api_key)
        
        page_instructions = ""
        if pages == '1':
            page_instructions = (
                "CRITICAL CONSTRAINT: The user needs a single-page (1-page) resume. "
                "Keep all summaries, descriptions, work experience bullet points, and project details "
                "extremely concise, punchy, and short. Remove any fluff or excessive wordiness. "
                "Ensure that the total word count is small enough to fit a single-page sheet (under 350-400 words total across the resume)."
            )
        elif pages == '2':
            page_instructions = (
                "CONSTRAINT: The user needs a 2-page resume. Professional experience can be slightly more detailed "
                "but make sure it fits a two-page layout cleanly. Target about 600-800 words."
            )
        else:
            page_instructions = (
                "Format the resume cleanly for standard/multi-page display. Rewrite the details to look professional."
            )

        prompt = f"""
        You are an expert AI Resume Writer. Your task is to professionally format and rewrite the provided resume information.
        Maintain all contact details and names exactly as provided, but polish the summary, skills, experience, internships, and education description.
        Make descriptions punchy, results-oriented, using active verbs and metrics where possible.
        
        {page_instructions}
        
        Input Resume Data:
        - Name: {name}
        - Email: {email}
        - Phone: {phone}
        - LinkedIn: {linkedin}
        - GitHub: {github}
        - Portfolio/Website: {portfolio}
        - Summary: {summary}
        - Technical/Hard Skills: {skills}
        - Soft Skills: {soft_skills}
        - Languages: {languages}
        - Work Experience: {experience}
        - Internships: {internships}
        - Projects: {projects}
        - Education: {education}
        
        Return ONLY a raw JSON object (do not wrap in markdown code blocks) with the following structure:
        {{
            "name": "polished name (usually unchanged)",
            "email": "email (unchanged)",
            "phone": "phone (unchanged)",
            "linkedin": "linkedin url (unchanged)",
            "github": "github url (unchanged)",
            "portfolio": "portfolio url (unchanged)",
            "summary": "professionally rewritten professional summary",
            "skills": "polished technical skills list",
            "soft_skills": "polished soft skills list",
            "languages": "polished languages list",
            "experience": "professionally rewritten work experience (using bullet points starting with - or * where appropriate)",
            "internships": "professionally rewritten internships (using bullet points where appropriate)",
            "projects": "professionally rewritten projects (using bullet points where appropriate)",
            "education": "professionally rewritten education details"
        }}
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        text_response = response.text.strip()
        if text_response.startswith('```json'):
            text_response = text_response[7:-3]
        elif text_response.startswith('```'):
            text_response = text_response[3:-3]
            
        parsed_res = json.loads(text_response.strip())
        parsed_res['pages'] = pages
        return parsed_res
        
    except Exception as e:
        print(f"Error calling Gemini in generate_resume: {e}")
        return {
            'name': name,
            'email': email,
            'phone': phone,
            'linkedin': linkedin,
            'github': github,
            'portfolio': portfolio,
            'summary': summary,
            'skills': skills,
            'soft_skills': soft_skills,
            'languages': languages,
            'experience': experience,
            'internships': internships,
            'projects': projects,
            'education': education,
            'pages': pages
        }

def _mock_analyze_resume(resume_text):
    text_lower = resume_text.lower()
    resume_keywords = ['experience', 'education', 'skills', 'work', 'project', 'university', 'college', 'school', 'degree', 'summary', 'profile', 'employment']
    
    # If the text is very short or lacks any common resume keywords, reject it
    if len(text_lower) < 50 or not any(kw in text_lower for kw in resume_keywords):
        return {
            "is_resume": False,
            "error": "This document does not appear to be a resume. Please upload a valid resume."
        }

    # Mock analysis based loosely on length
    score = min(40 + len(resume_text) // 100, 95)
    return {
        "is_resume": True,
        "ats_score": score,
        "strengths": ["Clear formatting", "Relevant keywords included", "Good action verbs used"],
        "weaknesses": ["Lacks quantifiable achievements", "Could improve summary section", "Some skills are not highlighted enough"],
        "recommended_job_title": "Software Developer",
        "summary": "A solid profile with good foundational skills. Adding more measurable impact would significantly improve ATS visibility.",
        "extracted_data": {
            "name": "Alex Applicant",
            "email": "alex.applicant@example.com",
            "phone": "+1 555 123 4567",
            "summary": "Dynamic and results-oriented professional with a proven track record. (This is an AI-improved version of your summary).",
            "skills": "Python, Agile Methodologies, Project Management",
            "experience": "Senior Specialist - Tech Innovations Inc.\n- Streamlined operations resulting in a 20% efficiency increase.\n- Managed cross-functional teams to deliver projects on time.",
            "education": "B.S. in Computer Science - Tech University (2020) - 3.8 CGPA"
        }
    }
