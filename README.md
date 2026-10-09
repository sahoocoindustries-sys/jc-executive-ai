# JC Executive AI

JC is a local-first personal AI workspace under active development. This repository contains a FastAPI backend, SQLite persistence, a browser chat interface, and a supervised AI task planner. The complete autonomous agent vision is not implemented yet; see the capability boundaries below.

## Run on Windows (recommended: Docker Desktop)

1. Install Docker Desktop and start it.
2. Clone this repository and open PowerShell in the project folder.
3. Copy `.env.example` to `.env` and add your own `GEMINI_API_KEY` (or configure `OPENAI_API_KEY`). Never commit `.env` or put a key in frontend code.
4. Run:

       docker compose up --build -d
       docker compose ps

5. Open `http://127.0.0.1:8000/web/chat.html` and click **Connect**.
6. Use **Send** for chat or **Plan task** to create an approval-gated task plan.
7. View logs with `docker compose logs -f jc`; stop with `docker compose down`.

The Compose port binds to loopback only. Do not expose this backend publicly: authentication and production deployment hardening are not complete.

## Run directly with Python 3.11+

PowerShell at the repository root:

       py -3.11 -m venv .venv
       .venv\\Scripts\\Activate.ps1
       python -m pip install -r requirements.txt
       Copy-Item .env.example .env

Edit `.env`, then start the server:

       python -m uvicorn jc.api.main:app --host 127.0.0.1 --port 8000

Open `http://127.0.0.1:8000/web/chat.html`.

## What works in this build

- Real text inference through configured Gemini, OpenAI, or Ollama providers.
- Conversation sessions and messages persisted in the configured SQLAlchemy database.
- Structured agent planning that produces up to eight specialist-assigned steps and saves them as a task with `pending_approval` status.
- Plan validation, basic provider error handling, and automated unit/regression tests.
- Local chat UI with model selection, English/Hindi/Odia response-language selection, conversation restoration, and plan-task action.

## What is not implemented yet

Planning is not execution. The app does not yet have a governed tool registry or a real multi-agent runtime. Live web research, GitHub writes, Netlify deployment, Windows desktop automation, voice conversation, recurring 24/7 jobs, bank/payment integrations, production authentication, and a production cloud deployment remain future work. Some existing endpoints are scaffolding and must not be treated as proof that these features work.

## API quick reference

- `GET /api/health/` — basic health response
- `POST /api/sessions/` — create a conversation session
- `GET /api/sessions/{session_id}/messages` — load saved messages
- `POST /api/inference/` — request a model response
- `POST /api/agent/plan` — create and save an approval-gated plan
- `GET /docs` — FastAPI interactive API docs

## Tests

       python -m pip install pytest requests sqlalchemy pydantic-settings
       python -m pytest tests/ -v

GitHub Actions also runs the focused provider, database mapping, and planner validation tests. Review the latest checks on the pull request before merging.

## Safety and cost

- Keep the backend local until authentication and authorization are implemented.
- Store provider keys in `.env` or server environment variables only; do not commit secrets.
- Review any generated plan before approving future execution features.
- AI provider calls may incur charges; the app does not currently calculate exact per-request cost.

## Project status

This is an incremental MVP, not a production-ready AGI or fully autonomous system. Build and runtime checks must pass before deployment or merging.
