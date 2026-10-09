# JC Live Chat — local setup

This page connects to the existing FastAPI backend. It is a local-first developer preview, not a public production deployment.

## 1. Configure the AI provider

From the repository root, create or edit the .env file (never commit this file):

    GEMINI_API_KEY=your_real_gemini_api_key
    HOST=127.0.0.1
    PORT=8000

Keep the key only in the backend environment. Do not paste it into web/chat.html, browser developer tools, or GitHub.

The default chat model is gemini-2.5-flash. Choose Gemini or OpenAI in the chat model selector after configuring the matching backend API key. Ollama requires a locally running Ollama service and a model installed on the computer.

## 2. Install and start the backend

Use a supported Python virtual environment, then install the repository's dependencies and start the FastAPI app:

    python -m venv .venv
    .venv\\Scripts\\Activate.ps1
    python -m pip install -r requirements.txt
    uvicorn jc.api.main:app --host 127.0.0.1 --port 8000

If dependency installation fails, do not skip the error; fix the dependency list or use the project's documented container workflow first.

## 3. Open the chat

Open web/chat.html in a browser. Leave the backend address set to http://127.0.0.1:8000, choose a reply language, and click Connect. Send a message to test the model connection.

The page creates a backend session and restores its history on later visits using a session ID saved in this browser. Messages are stored in the backend database. Clearing browser storage loses the saved session pointer but does not delete database records.

## Current boundaries

- This connects text chat to real model inference; it does not make JC a general autonomous agent yet.
- The backend's session endpoints currently have no authentication. Keep the server bound to loopback and do not expose it to the public internet.
- Tool execution and streaming endpoints intentionally report that they are not implemented.
- Provider usage can cost money. No exact per-request cost is calculated in this build.
- Voice, web search, GitHub write access, Netlify deployment, Windows automation, and 24/7 scheduling remain separate implementation stages.
