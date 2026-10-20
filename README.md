# Cohort

A UAIS project

## Stack
- Frontend: React + TypeScript (Vite), Tailwind
- Backend: FastAPI (Python)
- Auth & Database: Supabase
- Deployment: Vercel & Render

## Run it locally

You need Node 22 or newer (check with `node -v`), Python 3.10 or newer, and git.

### 1. Clone
```bash
git clone https://github.com/UndergraduateArtificialIntelligenceClub/Cohort
cd Cohort
```
Already use SSH with GitHub? Clone with `git@github.com:UndergraduateArtificialIntelligenceClub/Cohort` instead.

### 2. Env files
Copy the two example files. The copies are where your keys go, and git ignores them so they never get committed.
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```
- `GEMINI_API_KEY` (backend): make your own free key at [Google AI Studio](https://aistudio.google.com/apikey). Only needed for parsing work.
- `SUPABASE_*` (both files): ask the project lead on Discord. They're in Supabase under Project Settings → API. Only needed for database and login work.
- Never paste keys into code, issues, PRs or public channels. This repo is public.

The app runs without any keys filled in. You only need the ones for the issue you're working on.

### 3. Backend (terminal 1)
```bash
cd backend
python3 -m venv venv              # Windows: python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 4. Frontend (terminal 2)
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. If it says "Backend is alive", you're set up.

### Next time you work on it
You only need to create the venv and install once. After that:
```bash
cd backend
source venv/bin/activate          # Windows: venv\Scripts\activate
uvicorn main:app --reload
```
and in a second terminal:
```bash
cd frontend
npm run dev
```

## Data shape
Every deadline looks like this, in both the frontend ([frontend/src/types.ts](frontend/src/types.ts)) and the backend ([backend/models.py](backend/models.py)). If you change it, change both files in the same pull request.

| Field | Type | Example |
|---|---|---|
| `course` | string | `"CMPUT 174"` |
| `title` | string | `"Assignment 2"` |
| `date` | string, `YYYY-MM-DD` | `"2026-10-15"` |
| `category` | `assignment`, `lab`, `quiz`, `midterm`, `final`, or `other` | `"assignment"` |
| `source_text` | string, the exact sentence from the syllabus | `"Assignment 2 is due October 15."` |
| `weight` | number or null (optional), percent of final grade | `15` |

```json
{
  "course": "CMPUT 174",
  "title": "Assignment 2",
  "date": "2026-10-15",
  "category": "assignment",
  "source_text": "Assignment 2 is due October 15 and is worth 15% of your final grade.",
  "weight": 15
}
```

## Team
- Matthew Wang (project lead)
- Wasi Abbas
- Mark Liu
- Omer Abdelwahab
- Kyle
- Ruba Abbasi
- Alice Yin

## Contributing
Read [CONTRIBUTING.md](CONTRIBUTING.md) before your first pull request.
