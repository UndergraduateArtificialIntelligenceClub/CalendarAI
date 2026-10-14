# How we work

## The flow
1. Pick an issue assigned to you on the project board.
2. Start from the latest main:
   ```bash
   git checkout main
   git pull
   ```
3. Make a branch named after the work:
   ```bash
   git checkout -b feat/short-name     # new feature
   git checkout -b fix/short-name      # bug fix
   ```
4. Commit small and often. Check `git status` first so you only add what you meant to:
   ```bash
   git status
   git add .
   git commit -m "Add syllabus upload button"
   ```
5. Push your branch:
   ```bash
   git push -u origin feat/short-name
   ```
6. On GitHub, open a pull request into `main`. Write `Closes #<issue number>` in the description.
7. Get 1 approval and fix any comments. Anyone on the team can review, so ask your pair partner first.
8. Click **Squash and merge**. The branch deletes itself.
9. Go back to main and pull:
   ```bash
   git checkout main
   git pull
   ```

## If main changed while you were working
If GitHub says your branch is out of date or has conflicts:
```bash
git checkout main
git pull
git checkout feat/short-name
git merge main
```
Fix any conflicts, commit, and push again. Stuck? Ask in the team chat.

## After you pull
If someone added packages, install them or the app won't start:
```bash
cd backend && pip install -r requirements.txt    # with your venv active
cd frontend && npm install
```

## Rules
- Never commit `.env` files or API keys. This repo is public.
- One pull request per issue. Keep them small.
- Run the app locally before opening a pull request.
- Installed a Python package? From the `backend` folder with your venv active, run `pip freeze > requirements.txt` and commit it.
- Installed an npm package? `package.json` updates on its own. Commit it and `package-lock.json`.
- Stuck for more than 30 minutes? Ask in the team chat.
