import io
import re
from typing import Dict, List
import pdfplumber

OPTION_PATTERN = re.compile(r"^([A-D])[\)\.:]\s*(.*)$", re.MULTILINE)
QUESTION_SPLIT = re.compile(r"\n(?=\d+\.)")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        pages_text = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages_text)


def parse_questions_from_text(text: str) -> List[Dict]:
    cleaned = re.sub(r"\r", "", text)
    blocks = [b.strip() for b in QUESTION_SPLIT.split(cleaned) if b.strip()]
    questions: List[Dict] = []

    for block in blocks:
        match = re.match(r"(?P<number>\d+)\.\s*(?P<body>.*)", block, re.S)
        if not match:
            continue
        number = int(match.group("number"))
        body = match.group("body").strip()

        option_lines = OPTION_PATTERN.findall(body)
        options: Dict[str, str] = {}
        for key, value in option_lines:
            options[key.strip()] = value.strip()

        question_text = body
        if options:
            question_text = OPTION_PATTERN.sub("", body).strip()

        if question_text and len(options) >= 2:
            questions.append(
                {
                    "number": number,
                    "text": question_text,
                    "options": options,
                }
            )
    return questions
