# Cohort

A UAIS project

## Stack
- Frontend: React + TypeScript (Vite), Tailwind
- Backend: FastAPI (Python)
- Auth & Database: Supabase
- Deployment: Vercel & Render

## Run it locally

You need Node, Python 3, and git.

### 1. Clone
```bash
git clone https://github.com/UndergraduateArtificialIntelligenceClub/Cohort
(Already use SSH with GitHub? Clone with `git@github.com:UndergraduateArtificialIntelligenceClub/Cohort` instead.)
cd Cohort
```

### 2. Backend (terminal 1)
```bash
cd backend
python3 -m venv venv              # Windows: python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Frontend (terminal 2)
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

## Contributing
Read [CONTRIBUTING.md](CONTRIBUTING.md) before your first pull request.
