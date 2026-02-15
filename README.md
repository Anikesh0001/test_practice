# PDF-Based Online Test Generator & Evaluator

A full-stack web application that converts PDF assessment sets into timed online tests, evaluates answers using Gemini, and generates detailed results with explanations.

## Features

- Drag & drop PDF upload with automatic question extraction
- Timed test environment with fullscreen mode
- PDF order questions, bookmarks, and unanswered review
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



## Screenshots

### Upload Page
![Upload Page](screenshot/1.png)

### Test Configuration
![Test Configuration](screenshot/2.png)

### Test Environment
![Test Environment](screenshot/3.png)

### Results Dashboard
![Results Dashboard](screenshot/4.png)

### Explanation Modal
![Explanation Modal](screenshot/5.png)

### Review Page
![Review Page](screenshot/6.png)
