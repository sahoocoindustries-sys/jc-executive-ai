# JC Live Agent Planner — Windows setup

This setup runs JC locally on your Windows PC. It provides real model-backed chat and a supervised planner that saves task plans to the database. It does not yet perform external actions autonomously.

## Option A: Docker Desktop (recommended)

1. Install and start Docker Desktop for Windows.
2. In the repository folder, copy `.env.example` to `.env`.
3. Open `.env` and set `GEMINI_API_KEY` to your own key. Keep this file private; never commit it or paste the key into the browser.
4. Open PowerShell in the repository folder and run:

       docker compose up --build -d
       docker compose ps

5. Open `http://127.0.0.1:8000/web/chat.html` in your browser. Click **Connect**, then try chat or **Plan task**.
6. Check the service logs with `docker compose logs -f jc`. Stop the app with `docker compose down`.

The Docker Compose port is bound to 127.0.0.1, so it is not intentionally exposed to other devices on your network. Keep that local-only setting until authentication is implemented.

## Option B: Run Python directly

Use Python 3.11 or newer. In PowerShell at the repository root:

       py -3.11 -m venv .venv
       .venv\\Scripts\\Activate.ps1
       python -m pip install -r requirements.txt
       Copy-Item .env.example .env

Edit `.env` to add your real Gemini API key, then run:

       python -m uvicorn jc.api.main:app --host 127.0.0.1 --port 8000

Open `http://127.0.0.1:8000/web/chat.html`.

## How to use the planner

- Click **Connect** to create or restore a conversation.
- Use **Send** for ordinary model-backed chat.
- Enter a goal and click **Plan task** to ask JC to break it into up to eight specialist-assigned steps.
- JC saves the plan in the database with status `pending_approval`. The UI clearly states that no external actions were performed.

## Current limitations — important

- The planner generates and saves a proposed plan; it does not execute its steps yet.
- Voice, live web search, GitHub operations, Netlify deployment, Windows control, background scheduling, payment/bank integrations, and a real multi-agent execution engine are not yet implemented.
- API endpoints currently do not require user authentication. Keep the server bound to localhost and do not publish this backend or forward port 8000 publicly.
- AI provider requests may cost money. There is no exact per-request price calculation in the current build.
- If Docker fails, run `docker compose logs --no-color jc` and review the first error rather than ignoring it.
