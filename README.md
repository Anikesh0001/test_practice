# PDF-Based Online Test Generator & Evaluator

A full-stack web application that converts PDF assessment sets into timed online tests, evaluates answers using Gemini, and generates detailed results with explanations.

## Features

- Drag & drop PDF upload with automatic question extraction
- Timed test environment with fullscreen mode
- Question shuffle, bookmarks, and unanswered review
- Auto-submit on timer expiry
- Gemini-powered evaluation and explanations
- Results dashboard with analytics chart
- Retry test mode and downloadable PDF report
- Persistent state via localStorage to avoid refresh loss

## Tech Stack

**Frontend**: React (Vite), TypeScript, TailwindCSS, Recharts, jsPDF

**Backend**: FastAPI, SQLite, pdfplumber, Google Gemini API

## Project Structure

```
pdf-test-generator/
├── backend/
├── frontend/
└── README.md
```

## Environment Setup

### Backend

1. Create a virtual environment and install dependencies.
2. Copy `.env.example` to `.env` and set your API key.

Example `.env`:
```
GEMINI_API_KEY=YOUR_KEY
DATABASE_URL=sqlite:///./app.db
CORS_ORIGINS=http://localhost:5173
```

3. Run the backend server:
```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

1. Install dependencies and start the dev server:
```
cd frontend
npm install
npm run dev
```

2. If needed, set `VITE_API_BASE_URL` in a `.env` file inside the frontend directory.

## How to Use

1. Upload a PDF containing MCQs.
2. Choose test duration and start.
3. Answer questions, bookmark, and review.
4. Submit or auto-submit on timer end.
5. View results, explanations, and analytics.

## Gemini Prompting

The backend uses two prompts:

- **Answer Evaluation Prompt**: Returns JSON with correct option, correctness, and short explanation.
- **Explanation Prompt**: Explains the correct answer in simple terms (max 4 lines).

## Deployment (Free Tier)

### Frontend (Vercel)

1. Set the Vercel project root to `frontend`.
2. Add environment variable `VITE_API_BASE_URL` pointing to your backend URL.
3. Deploy.

### Backend (Render / Railway)

1. Set the service root to `backend`.
2. Add environment variable `GEMINI_API_KEY`.
3. Use the start command:
```
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Screenshots (placeholders)

- Upload page screenshot
- Test environment screenshot
- Results dashboard screenshot
- Explanation modal screenshot

Replace these placeholders with real images once available.
