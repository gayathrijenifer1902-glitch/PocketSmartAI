# PocketSmart AI

PocketSmart AI is a complete FastAPI web app for budget-aware home, party, and jewelry planning. It supports local fallback recommendations by default and Gemini-powered structured recommendations when configured. It stores accounts and planning history in SQLite.

## Quick start in VS Code

1. Open this folder in VS Code and open its integrated terminal.
2. Create an environment: `python -m venv .venv`
3. Activate it on Windows: `.venv\\Scripts\\Activate.ps1`
4. Install: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env`. For Gemini, set `GEMINI_API_KEY`; otherwise fallback plans work immediately. Use a long unique `SECRET_KEY` outside development.
6. Run: `uvicorn app.main:app --reload`
7. Visit http://127.0.0.1:8000. Interactive API docs are at `/docs`.

## Test

Run `pytest`. Tests cover health, registration/login, authenticated planner generation, fallback output, history, and validation.

## API

`POST /register`, `POST /login`, `POST /token`, `POST /logout`, `GET /session-info`, `GET /session-data`, `POST /generate-home`, `POST /generate-party`, `POST /generate-jewelry`, `POST /generate-jewelry/upload`, `GET /history`, and `GET /recommendations-details/{history_id}`.

Planner calls require `Authorization: Bearer <token>`. The browser UI manages this after login. `generate-jewelry/upload` accepts multipart fields plus an optional image; Gemini receives image bytes only when configured. Gemini requests use the maintained `google-genai` SDK and JSON response mode. Any API error, missing key, or malformed model response safely falls back to non-live planning data.

## Notes

The application intentionally does not scrape or represent live vendor pricing. Platform names are discovery suggestions; validate prices, inventory, authenticity, delivery, taxes, and vendor terms before spending.
