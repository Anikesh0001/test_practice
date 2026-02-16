"""
Company-based Assessment API Routes
Handles generation of AI-powered company assessments
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Question, TestSession, TestQuestion
from company_research import research_company
from company_cache import get_or_fetch_profile, list_cached_companies
from llm_test_generator import generate_company_assessment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["company-assessment"])


def _convert_options_to_dict(options_list):
    """Convert list of options ['A) text', 'B) text'] to dict {'A': 'text', 'B': 'text'}"""
    if not options_list:
        return {}  # Return empty dict for empty lists
    if isinstance(options_list, dict):
        return options_list
    
    options_dict = {}
    for option in options_list:
        if isinstance(option, str) and ')' in option:
            key, value = option.split(')', 1)
            options_dict[key.strip()] = value.strip()
    
    return options_dict if options_dict else {}


# Request/Response Models
class CompanyTestRequest(BaseModel):
    """Request model for generating company-based test."""
    company: str
    use_cache: bool = True


class CompanyTestResponse(BaseModel):
    """Response model for company test generation."""
    test_id: int
    company_name: str
    total_questions: int
    difficulty: str
    duration_minutes: int
    message: str


class CachedCompaniesResponse(BaseModel):
    """Response model for listing cached companies."""
    companies: list[str]
    count: int


# Endpoints
@router.post("/generate-company-test", response_model=CompanyTestResponse)
async def generate_company_test(
    request: CompanyTestRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a new assessment test based on company hiring pattern.
    
    Flow:
    1. Get company profile (from cache or research via Perplexity)
    2. Generate assessment using LLM based on profile
    3. Store questions in database
    4. Create test session
    5. Return test details
    """
    try:
        company_name = request.company.strip()
        
        if not company_name:
            raise HTTPException(status_code=400, detail="Company name is required")
        
        logger.info(f"Generating test for company: {company_name}")
        
        # Step 1: Get or fetch company profile
        if request.use_cache:
            profile = await get_or_fetch_profile(company_name, research_company)
        else:
            profile = await research_company(company_name)
        
        logger.info(f"Retrieved profile for {company_name}: {profile.get('difficulty_level')}")
        
        # Step 2: Generate assessment using LLM
        assessment = await generate_company_assessment(profile)
        
        logger.info(f"Generated {len(assessment['questions'])} questions")
        
        # Step 3: Store questions in database
        question_objects = []
        for idx, q_data in enumerate(assessment["questions"]):
            # Check if question already exists (avoid duplicates)
            existing = db.query(Question).filter(
                Question.text == q_data["question"],
                Question.source_name == company_name
            ).first()
            
            if existing:
                # Update options format if needed
                if isinstance(existing.options, list):
                    existing.options = _convert_options_to_dict(existing.options)
                    db.add(existing)
                question_objects.append(existing)
            else:
                question = Question(
                    number=idx + 1,
                    text=q_data["question"],
                    options=_convert_options_to_dict(q_data.get("options")),
                    source_name=company_name
                )
                db.add(question)
                db.flush()
                question_objects.append(question)
        
        db.commit()
        
        # Step 4: Create test session
        test_session = TestSession(
            total_questions=len(question_objects),
            duration_minutes=assessment.get("duration_minutes", 90)
        )
        db.add(test_session)
        db.flush()
        
        # Link questions to test in order
        for idx, question in enumerate(question_objects):
            link = TestQuestion(
                test_id=test_session.id,
                question_id=question.id,
                order_index=idx
            )
            db.add(link)
        
        db.commit()
        db.refresh(test_session)
        
        logger.info(f"Created test session {test_session.id} for {company_name}")
        
        return CompanyTestResponse(
            test_id=test_session.id,
            company_name=company_name,
            total_questions=len(question_objects),
            difficulty=assessment.get("difficulty_level", "Medium"),
            duration_minutes=assessment.get("duration_minutes", 90),
            message=f"Successfully generated {company_name} assessment with {len(question_objects)} questions"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating company test: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate company assessment: {str(e)}"
        )


@router.get("/cached-companies", response_model=CachedCompaniesResponse)
async def get_cached_companies():
    """
    Get list of all companies with cached profiles.
    Useful for frontend autocomplete/suggestions.
    """
    try:
        companies = list_cached_companies()
        return CachedCompaniesResponse(
            companies=companies,
            count=len(companies)
        )
    except Exception as e:
        logger.error(f"Error fetching cached companies: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch cached companies"
        )


@router.get("/company-profile/{company_name}")
async def get_company_profile_details(company_name: str):
    """
    Get detailed profile information for a specific company.
    Returns cached profile if available, otherwise performs research.
    """
    try:
        profile = await get_or_fetch_profile(company_name, research_company)
        return profile
    except Exception as e:
        logger.error(f"Error fetching company profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch profile for {company_name}"
        )
