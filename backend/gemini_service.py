import json
import os
from typing import Dict, List
from dotenv import load_dotenv
import google.generativeai as genai
import httpx

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq").lower()  # Default to Groq for explanations
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")

if API_KEY:
    genai.configure(api_key=API_KEY)


def _get_model():
    return genai.GenerativeModel(MODEL_NAME)


def _fallback_model():
    for candidate in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]:
        try:
            return genai.GenerativeModel(candidate)
        except Exception:
            continue
    return genai.GenerativeModel(MODEL_NAME)


def _safe_json_loads(text: str):
    cleaned = text.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            return json.loads(cleaned[start : end + 1])
        raise


def _perplexity_chat(prompt: str) -> str:
    if not PERPLEXITY_API_KEY:
        raise RuntimeError("Perplexity API key not configured.")

    headers = {"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": [
            {"role": "system", "content": "You are a precise exam evaluator."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    with httpx.Client(timeout=30) as client:
        response = client.post("https://api.perplexity.ai/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def _groq_chat(prompt: str) -> str:
    """Use Groq for fast, free explanations"""
    if not GROQ_API_KEY:
        raise RuntimeError("Groq API key not configured.")

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a concise exam explanation expert. Answer in 2-3 sentences."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 300,
    }

    with httpx.Client(timeout=30) as client:
        response = client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def _groq_evaluate(question: str, options: Dict[str, str], user_answer: str) -> Dict:
    """Evaluate using Groq - fast and free"""
    prompt = (
        "You are an exam evaluator. Given a question, options, and user answer, "
        "return ONLY valid JSON in this exact format with no extra text:\n"
        "{\"correct_answer\":\"A\",\"is_correct\":true,\"explanation\":\"brief explanation\"}\n\n"
        f"Question: {question}\n"
        f"Options: {options}\n"
        f"User Answer: {user_answer}\n"
        "Respond with only the JSON."
    )
    
    raw = _groq_chat(prompt)
    try:
        data = _safe_json_loads(raw)
        return data
    except Exception as e:
        print(f"Failed to parse Groq response: {e}. Raw: {raw}")
        return {
            "correct_answer": "A",
            "is_correct": user_answer == "A",
            "explanation": "Evaluation unavailable"
        }


def evaluate_answer(question: str, options: Dict[str, str], user_answer: str) -> Dict:
    """Evaluate answer - uses original method for PDF (Gemini or fallback)"""
    return _gemini_evaluate(question, options, user_answer)


def _gemini_evaluate(question: str, options: Dict[str, str], user_answer: str) -> Dict:
    """Original evaluation method for PDF mode - uses Gemini"""
    if not API_KEY:
        return {
            "correct_answer": "A",
            "is_correct": user_answer == "A",
            "explanation": "API key not configured. Using placeholder evaluation.",
        }

    prompt = (
        "You are an exam evaluator.\n"
        "Given the question, options, and a user answer, return ONLY JSON in this format:"
        "{\"correct_answer\":\"A\",\"is_correct\":true,\"explanation\":\"...\"}.\n"
        "Choose the correct option letter. Keep explanation to 3-4 lines.\n\n"
        f"Question: {question}\n"
        f"Options: {options}\n"
        f"User Answer: {user_answer}\n"
    )

    try:
        model = _get_model()
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.2, "response_mime_type": "application/json"},
        )
        data = _safe_json_loads(response.text)
    except Exception:
        try:
            model = _fallback_model()
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.2, "response_mime_type": "application/json"},
            )
            data = _safe_json_loads(response.text)
        except Exception as e:
            print(f"Gemini evaluation failed: {e}. Using placeholder.")
            return {
                "correct_answer": "A",
                "is_correct": user_answer == "A",
                "explanation": "Evaluation unavailable"
            }

    return {
        "correct_answer": str(data.get("correct_answer", "")).strip().upper(),
        "is_correct": bool(data.get("is_correct")),
        "explanation": str(data.get("explanation", "")).strip(),
    }


def explain_answer(question: str, options: Dict[str, str], correct_answer: str) -> str:
    """Generate explanation using Groq (fast and free)"""
    if GROQ_API_KEY:
        try:
            prompt = (
                "Explain why this answer is correct. Max 3 sentences, simple language.\n"
                f"Question: {question}\n"
                f"Options: {options}\n"
                f"Correct Answer: {correct_answer}\n"
            )
            return _groq_chat(prompt).strip()
        except Exception as e:
            print(f"Groq explanation failed: {e}")
    
    # Fallback
    return "Explanation unavailable. Please review the question and options."


def extract_questions_llm(text: str) -> List[Dict]:
    if AI_PROVIDER == "perplexity" and not PERPLEXITY_API_KEY:
        return []

    if AI_PROVIDER != "perplexity" and not API_KEY:
        return []

    prompt = (
        "Extract all multiple-choice questions from the given text.\n"
        "Return ONLY JSON as a list of objects with keys: number, text, options.\n"
        "options must be an object with keys A, B, C, D.\n"
        f"Text: {text[:12000]}"
    )

    if AI_PROVIDER == "perplexity":
        raw = _perplexity_chat(prompt)
        data = _safe_json_loads(raw)
    else:
        try:
            model = _get_model()
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.2, "response_mime_type": "application/json"},
            )
            data = _safe_json_loads(response.text)
        except Exception:
            model = _fallback_model()
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.2, "response_mime_type": "application/json"},
            )
            data = _safe_json_loads(response.text)
    return data if isinstance(data, list) else []
