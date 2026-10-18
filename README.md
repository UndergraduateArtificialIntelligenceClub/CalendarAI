# CalendarAI

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
git clone https://github.com/UndergraduateArtificialIntelligenceClub/CalendarAI.git
(Already use SSH with GitHub? Clone with `git@github.com:UndergraduateArtificialIntelligenceClub/CalendarAI.git` instead.)
cd CalendarAI
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

## Team
- Matthew Wang (project lead)
- Wasi Abbas
- Mark Liu

## Contributing
Read [CONTRIBUTING.md](CONTRIBUTING.md) before your first pull request.
