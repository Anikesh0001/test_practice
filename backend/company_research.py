"""
Company Research Module using Perplexity API
Performs deep research about company hiring patterns and assessment styles
"""
import os
import logging
from typing import Dict, Any
import httpx

logger = logging.getLogger(__name__)

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


async def research_company(company_name: str) -> Dict[str, Any]:
    """
    Perform deep research about company's online assessment pattern using Perplexity API.
    
    Args:
        company_name: Name of the company to research
        
    Returns:
        Structured company profile with hiring patterns
        
    Raises:
        Exception: If API call fails or no API key is configured
    """
    if not PERPLEXITY_API_KEY:
        raise Exception("PERPLEXITY_API_KEY not configured in environment variables")
    
    # Construct research prompt
    prompt = f"""Research {company_name}'s campus recruitment and online assessment pattern.

Provide detailed information about:
1. Overall difficulty level (Easy/Medium/Hard)
2. Question distribution across sections (Aptitude, Core CS, DSA, Coding)
3. Common Data Structures & Algorithms topics they focus on
4. Aptitude questions ratio and type
5. Coding problem style (implementation, optimization, problem-solving)
6. Key hiring focus areas (algorithms, system design, problem solving, etc.)
7. Time constraints and test structure
8. Recent patterns from campus placements

Return the information in a structured format covering all aspects of their technical assessment."""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                PERPLEXITY_API_URL,
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar-pro",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert at analyzing company hiring patterns and technical assessments. Provide detailed, accurate information about campus recruitment processes."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
            )
            response.raise_for_status()
            data = response.json()
            
            research_content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Parse and structure the research data
            profile = _parse_research_content(company_name, research_content)
            
            logger.info(f"Successfully researched company: {company_name}")
            return profile
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error during company research: {e}")
        raise Exception(f"Failed to research company: {str(e)}")
    except Exception as e:
        logger.error(f"Error researching company {company_name}: {e}")
        raise


def _parse_research_content(company_name: str, content: str) -> Dict[str, Any]:
    """
    Parse raw research content into structured company profile.
    
    Args:
        company_name: Name of the company
        content: Raw research content from Perplexity
        
    Returns:
        Structured company profile dictionary
    """
    # Extract key information from content using heuristics
    content_lower = content.lower()
    
    # Determine difficulty level
    if "hard" in content_lower or "difficult" in content_lower or "challenging" in content_lower:
        difficulty = "Hard"
    elif "easy" in content_lower or "beginner" in content_lower:
        difficulty = "Easy"
    else:
        difficulty = "Medium"
    
    # Default distribution that can be refined based on content
    question_distribution = {
        "aptitude": 15,
        "core_cs": 15,
        "dsa": 10,
        "coding": 10
    }
    
    # Common DSA topics
    dsa_topics = []
    common_topics = [
        "arrays", "strings", "linked lists", "trees", "graphs", "dynamic programming",
        "greedy", "backtracking", "searching", "sorting", "hashing", "stack", "queue",
        "heap", "recursion", "binary search", "sliding window", "two pointers"
    ]
    
    for topic in common_topics:
        if topic in content_lower:
            dsa_topics.append(topic.title())
    
    # If no specific topics found, add default ones
    if not dsa_topics:
        dsa_topics = ["Arrays", "Strings", "Dynamic Programming", "Trees", "Graphs"]
    
    # Determine aptitude focus
    aptitude_ratio = 0.3  # Default 30%
    if "aptitude" in content_lower and ("high" in content_lower or "significant" in content_lower):
        aptitude_ratio = 0.4
    elif "less aptitude" in content_lower or "minimal aptitude" in content_lower:
        aptitude_ratio = 0.2
    
    # Coding style analysis
    coding_style = "Problem-solving focused"
    if "optimization" in content_lower:
        coding_style = "Optimization and efficiency focused"
    elif "implementation" in content_lower:
        coding_style = "Implementation heavy"
    
    # Build structured profile
    profile = {
        "company_name": company_name,
        "difficulty_level": difficulty,
        "question_distribution": question_distribution,
        "dsa_topics": dsa_topics[:8],  # Top 8 topics
        "aptitude_ratio": aptitude_ratio,
        "coding_style": coding_style,
        "hiring_focus": [
            "Problem Solving",
            "Data Structures & Algorithms",
            "Coding Proficiency",
            "Analytical Thinking"
        ],
        "test_duration_minutes": 90,
        "total_questions": 50,
        "research_summary": content[:500],  # Store first 500 chars of research
        "sections": {
            "aptitude": {
                "count": question_distribution["aptitude"],
                "types": ["Logical Reasoning", "Quantitative Aptitude", "Verbal Ability"]
            },
            "core_cs": {
                "count": question_distribution["core_cs"],
                "topics": ["Operating Systems", "DBMS", "Networks", "OOP"]
            },
            "dsa": {
                "count": question_distribution["dsa"],
                "topics": dsa_topics[:5]
            },
            "coding": {
                "count": question_distribution["coding"],
                "difficulty": difficulty,
                "style": coding_style
            }
        }
    }
    
    return profile
