import json
import os
from typing import Dict, List
from dotenv import load_dotenv
import google.generativeai as genai
import httpx

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-002")
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")

if API_KEY:
    genai.configure(api_key=API_KEY)


def _get_model():
    return genai.GenerativeModel(MODEL_NAME)


def _fallback_model():
    for candidate in ["gemini-1.5-flash-002", "gemini-1.5-flash", "gemini-1.5-pro"]:
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


def evaluate_answer(question: str, options: Dict[str, str], user_answer: str) -> Dict:
    if AI_PROVIDER == "perplexity" and not PERPLEXITY_API_KEY:
        return {
            "correct_answer": "A",
            "is_correct": user_answer == "A",
            "explanation": "Perplexity API key not configured. Using placeholder evaluation.",
        }

    if AI_PROVIDER != "perplexity" and not API_KEY:
        return {
            "correct_answer": "A",
            "is_correct": user_answer == "A",
            "explanation": "Gemini API key not configured. Using placeholder evaluation.",
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

    return {
        "correct_answer": str(data.get("correct_answer", "")).strip().upper(),
        "is_correct": bool(data.get("is_correct")),
        "explanation": str(data.get("explanation", "")).strip(),
    }


def explain_answer(question: str, options: Dict[str, str], correct_answer: str) -> str:
    if AI_PROVIDER == "perplexity" and not PERPLEXITY_API_KEY:
        return "Perplexity API key not configured. Explanation unavailable."

    if AI_PROVIDER != "perplexity" and not API_KEY:
        return "Gemini API key not configured. Explanation unavailable."

    prompt = (
        "Explain the correct answer simply for students. Max 4 lines.\n"
        f"Question: {question}\n"
        f"Options: {options}\n"
        f"Correct Answer: {correct_answer}\n"
    )

    if AI_PROVIDER == "perplexity":
        return _perplexity_chat(prompt).strip()

    try:
        model = _get_model()
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.4},
        )
        return response.text.strip()
    except Exception:
        model = _fallback_model()
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.4},
        )
        return response.text.strip()


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
