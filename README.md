# Sahayak

Sahayak turns meeting recordings into reviewable transcripts and a short list of follow-up tasks. It is designed for teams that work across Hindi, English, and Hinglish, with a small FastAPI service behind a React dashboard.

The repository is a monorepo with separate backend and frontend applications. The current reminder endpoint records a mock WhatsApp send; it does not contact WhatsApp.

## What it does

- Accepts audio and video meeting recordings.
- Transcribes recordings with OpenAI Whisper when an API key is configured.
- Extracts action items, assignees, deadlines, and status with an OpenAI chat model.
- Shows recent meetings and pending, completed, and overdue tasks in a dashboard.
- Supports Google sign-in and JWT-protected API routes.
- Provides Docker Compose configuration for local development and deployment manifests for Render, Railway, and Vercel.

When `OPENAI_API_KEY` is empty, the backend uses a small deterministic demo transcript and two demo tasks. This keeps the UI usable without external AI credentials; it is not a substitute for the production processing path.

## Repository layout

| Directory | Contents |
|---|---|
| `backend/` | FastAPI application, MongoDB access, authentication, upload processing, and AI service wrappers |
| `frontend/` | React 18, TypeScript, Vite, Tailwind CSS, and the dashboard UI |
| `docker-compose.yml` | Local MongoDB, backend, and frontend services |
| `SANITY_CHECK.md` | Previously documented build checks and remaining runtime validation |

## Local development

### Backend

The backend expects Python 3.11+ and MongoDB.

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Set these values in `backend/.env`:

| Variable | Purpose |
|---|---|
| `MONGODB_URI` | MongoDB connection string |
| `MONGODB_DB` | Database name |
| `OPENAI_API_KEY` | Enables real transcription and extraction; leave empty for demo mode |
| `OPENAI_WHISPER_MODEL` | Whisper model name |
| `OPENAI_ACTION_MODEL` | Chat model used for action-item extraction |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `JWT_SECRET` | Long random signing secret; required for a real deployment |
| `FRONTEND_URL` | Frontend origin allowed by CORS |

The API listens on `http://localhost:8000` by default. Health is available at `GET /health`.

### Frontend

The frontend expects Node.js 20+.

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Set `VITE_API_BASE_URL` to the backend API base URL and `VITE_GOOGLE_CLIENT_ID` to the same Google client ID used by the backend. The frontend runs on `http://localhost:5173` by default.

### Docker Compose

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```

The Compose setup starts MongoDB on port `27017`, the API on port `8000`, and the frontend on port `5173`.

## API surface

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness check; does not claim MongoDB readiness |
| `GET` | `/ready` | Readiness check requiring MongoDB connectivity |
| `POST` | `/api/auth/google` | Exchange a Google credential for an application JWT |
| `POST` | `/api/upload` | Upload and process a meeting recording |
| `GET` | `/api/meetings` | List the current user’s meetings |
| `GET` | `/api/meetings/{id}` | Read one meeting and its action items |
| `GET` | `/api/media/{filename}` | Stream one recording after authenticated ownership verification |
| `GET` | `/api/action-items?status=pending` | List action items, optionally filtered by status |
| `POST` | `/api/action-items/{id}/complete` | Mark an action item complete |
| `POST` | `/api/send-reminder/{id}` | Record a mock reminder send |

## Data model

The backend uses three MongoDB collections: `users`, `meetings`, and `action_items`. Startup creates indexes for Google identity, user meeting lookups, media filename lookups, and action-item lookups.

## Engineering notes

This is an actively shaped prototype rather than a claim of production readiness. Uploaded media remains on the local filesystem behind an authenticated ownership-checked media endpoint; it is not object storage. Docker Compose mounts a named upload volume for local restarts, but a durable object-storage integration or platform-backed persistent volume is still required for deployments that can restart, replace, or scale instances. Failed processing removes the newly stored local file.

The repository includes syntax checks, a frontend production build, seven backend security regression tests, and six frontend component tests, executed in CI on every push and pull request. Live MongoDB, Google OAuth, OpenAI, and end-to-end upload integrations still need environment-backed coverage before deployment.

## Deployment files

- `backend/render.yaml` describes a Render web service.
- `backend/railway.json` describes a Railway deployment.
- `frontend/vercel.json` provides SPA fallback routing for Vercel.

Before deploying, use real secrets, restrict CORS to the actual frontend origin, and confirm that media storage and access control meet the privacy requirements of the recordings being processed.
