"""
LLM-based Test Generator
Generates realistic company assessments using Groq (Free & Fast)
"""
import os
import json
import logging
from typing import Dict, Any, List
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Try Groq first (free and fast), fallback to Perplexity
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def _safe_json_parse(text: str) -> Dict:
    """Safely parse JSON from LLM response, handling markdown code blocks."""
    if not text or not text.strip():
        raise ValueError("Empty response text")
    
    cleaned = text.strip()
    
    # Remove markdown code blocks
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned:
        parts = cleaned.split("```")
        if len(parts) >= 2:
            cleaned = parts[1].strip()
    
    # Try to parse as-is first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find JSON object boundaries
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}. Text: {cleaned[:500]}")
                raise
        raise ValueError(f"Could not find valid JSON in response. Text preview: {cleaned[:200]}")


async def generate_company_assessment(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a realistic company assessment using Groq (Free & Fast).
    
    Args:
        profile: Company hiring profile with difficulty, topics, patterns
        
    Returns:
        Dictionary containing generated assessment with questions
    """
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY not found in environment. Get free API key from https://console.groq.com")
    
    company_name = profile.get("company_name", "Unknown Company")
    difficulty = profile.get("difficulty_level", "Medium")
    dsa_topics = profile.get("dsa_topics", [])
    sections = profile.get("sections", {})
    coding_style = profile.get("coding_style", "Problem-solving focused")
    
    logger.info(f"Generating assessment for {company_name} using Groq (Free)")
    
    # Build comprehensive prompt
    prompt = _build_assessment_prompt(
        company_name=company_name,
        difficulty=difficulty,
        sections=sections,
        dsa_topics=dsa_topics,
        coding_style=coding_style
    )
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            request_payload = {
                "model": "llama-3.3-70b-versatile",  # Free Groq model (updated)
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert at creating realistic campus online assessments. You MUST respond with ONLY valid JSON, no other text. Generate exactly what is requested. Keep explanations concise (max 2 sentences)."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 32000  # Increased for 50 questions
            }
            
            logger.info(f"Sending request to Groq API with model: llama-3.3-70b-versatile (max_tokens: 32000)")
            
            response = await client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=request_payload
            )
            
            if response.status_code != 200:
                logger.error(f"Groq API error {response.status_code}: {response.text}")
            
            response.raise_for_status()
            data = response.json()
            
            # Extract content
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            logger.info(f"Generated content length: {len(content)} chars")
            
            if not content or len(content) < 100:
                logger.error(f"Content too short. Full response: {data}")
                raise Exception(f"Groq returned empty response")
            
            # Parse the response
            assessment_data = _safe_json_parse(content)
        
        # Validate and structure the assessment
        structured_assessment = _structure_assessment(assessment_data, profile)
        
        logger.info(f"Successfully generated {len(structured_assessment.get('questions', []))} questions")
        return structured_assessment
        
    except httpx.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        raise Exception(f"Failed to generate assessment: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating assessment: {e}")
        raise Exception(f"Failed to generate assessment: {str(e)}")


def _build_assessment_prompt(
    company_name: str,
    difficulty: str,
    sections: Dict,
    dsa_topics: List[str],
    coding_style: str
) -> str:
    """Build detailed prompt for LLM to generate realistic assessment - ALL MCQs."""
    
    prompt = f"""You are an expert at creating realistic campus online assessments.

Generate a complete online assessment test similar to {company_name}'s actual campus hiring process.

**CRITICAL REQUIREMENT: ALL 50 QUESTIONS MUST BE MULTIPLE CHOICE QUESTIONS (MCQ) ONLY**

**Requirements:**

1. **Total Questions:** 50 MCQ questions exactly
2. **Question Type:** Multiple Choice ONLY (4 options: A, B, C, D)
3. **Overall Difficulty:** {difficulty}

**Section Distribution:**

**Aptitude Section** ({sections.get('aptitude', {}).get('count', 15)} MCQs):
- Logical Reasoning (pattern recognition, series, puzzles)
- Quantitative Aptitude (numbers, percentages, profit/loss, ratios)
- Verbal Ability (synonyms, antonyms, sentence completion, reading)
- Mix of Easy/Medium difficulty
- Each question has exactly 4 options with 1 correct answer
- Real campus interview-style questions

**Core CS Fundamentals Section** ({sections.get('core_cs', {}).get('count', 15)} MCQs):
- Operating Systems (processes, scheduling, memory management, deadlock)
- Database Management (SQL queries, normalization, transactions, indexes)
- Computer Networks (TCP/IP layers, HTTP status codes, protocols)
- Object-Oriented Programming (inheritance, polymorphism, encapsulation, patterns)
- Data Structures (arrays, linked lists, trees, graphs concepts)
- Medium difficulty, concept-based questions
- Each question has exactly 4 options with 1 correct answer

**DSA & Problem Solving Section** ({sections.get('dsa_coding', {}).get('count', 20)} MCQs):
Focus on these topics:
{chr(10).join([f"- {topic}" for topic in dsa_topics[:10]])}

- Time & Space Complexity analysis (identify complexity of given code)
- Algorithm analysis ("What is the output?" type questions)
- Data structure operations (what happens when X operation is performed)
- Problem-solving patterns and optimization
- Each question has exactly 4 options with 1 correct answer
- {difficulty} difficulty level
- Mix of conceptual and coding problems
- Include time/space complexity questions
- Real problem-solving scenarios
- {difficulty} difficulty level

**OUTPUT FORMAT (STRICT JSON - ALL MCQ):**

You MUST respond with ONLY this exact JSON structure, no extra text:

{{
  "company_name": "{company_name}",
  "difficulty": "{difficulty}",
  "total_questions": 50,
  "questions": [
    {{
      "id": 1,
      "section": "aptitude" | "core_cs" | "dsa_coding",
      "type": "mcq",
      "difficulty": "Easy" | "Medium" | "Hard",
      "question": "Full question text here",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "correct_answer": "A" | "B" | "C" | "D",
      "explanation": "Brief explanation in 1-2 sentences",
      "topic": "Specific topic",
      "time_estimate": 2
    }}
  ]
}}

**IMPORTANT RULES:**
1. Generate EXACTLY 50 MCQ questions (no coding, no fill-in-the-blank, MCQ ONLY)
2. ALL questions MUST have type: "mcq"
3. ALL questions MUST have exactly 4 options (A, B, C, D)
4. Distribute questions as specified in sections
5. Make questions realistic and relevant to {company_name}
6. Each question MUST have all required fields
7. Keep explanations concise (max 2 sentences each)
8. DO NOT include any text outside the JSON structure
9. Ensure valid JSON syntax (no trailing commas, proper quotes)
10. Escape special characters in strings (quotes, newlines, etc.)
11. NEVER generate coding-type questions, ALL must be MCQ
"""
    
    return prompt


def _structure_assessment(raw_data: Dict, profile: Dict[str, Any]) -> Dict[str, Any]:
    """Structure and validate the generated assessment."""
    
    if "questions" not in raw_data:
        raise Exception("Invalid assessment format: missing 'questions' key")
    
    questions = raw_data["questions"]
    
    if len(questions) < 40:
        logger.warning(f"Only {len(questions)} questions generated, expected 50")
    
    # Ensure each question has required fields
    structured_questions = []
    for i, q in enumerate(questions, 1):
        structured_q = {
            "id": i,
            "section": q.get("section", "dsa_coding"),
            "type": q.get("type", "mcq"),
            "difficulty": q.get("difficulty", "Medium"),
            "question": q.get("question", f"Question {i}"),
            "options": q.get("options", ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"]),
            "correct_answer": q.get("correct_answer", "A"),
            "explanation": q.get("explanation", "No explanation provided"),
            "topic": q.get("topic", "General"),
            "time_estimate": q.get("time_estimate", 2)
        }
        structured_questions.append(structured_q)
    
    return {
        "company_name": profile.get("company_name", "Unknown"),
        "difficulty": profile.get("difficulty_level", "Medium"),
        "total_questions": len(structured_questions),
        "time_limit_minutes": 90,
        "questions": structured_questions,
        "sections": {
            "aptitude": len([q for q in structured_questions if q["section"] == "aptitude"]),
            "core_cs": len([q for q in structured_questions if q["section"] == "core_cs"]),
            "dsa_coding": len([q for q in structured_questions if q["section"] == "dsa_coding"])
        }
    }
