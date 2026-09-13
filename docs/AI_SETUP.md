# Gemini pilot setup

Implemented: server-side Writing assessment, validated criterion scores, verbatim evidence checks, database-backed jobs with a lease and up to three attempts, rate-limit backoff, result polling, and a Speaking practice studio with microphone/speaker checks and timed stages.

No real API key is stored in this repository. No live Gemini call or microphone/browser test has yet been completed. Tests use mocked provider responses. Free-tier eligibility and quotas must be checked in your own AI Studio project; code cannot ensure a model is free. The worker does not change billing tiers or select paid fallbacks.

## Enable Writing

Set these in the **server** environment (or the root .env consumed by Compose):

```
AI_ENABLED=1
GEMINI_API_KEY=YOUR_NEW_PRIVATE_KEY
GEMINI_WRITING_MODEL=gemini-2.5-flash
GEMINI_LIVE_MODEL=gemini-3.1-flash-live-preview
```

Django does not automatically load .env for local commands: export variables in your shell or use your deployment secret manager. Never use NEXT_PUBLIC_ for a provider secret. Rotate keys that were shared in chat or public repositories.

Run migrations, then restart the backend and start the worker:

```
docker compose run --rm backend python manage.py migrate
docker compose up -d --build backend frontend
docker compose --profile ai up -d --build ai_worker
```

For local development: `python manage.py assess_pending --watch`. Without `--watch`, the command drains currently eligible jobs and exits. Jobs are created when a Writing attempt is submitted, even when AI is disabled. Previously submitted attempts from before this migration are not automatically requeued; create a job for an eligible attempt through a controlled admin shell if required.

Use original non-sensitive sample essays for the initial free-tier trial. Google's free-tier data terms may permit use of submitted content for product improvement. Do not enable real student submissions until data handling and consent are appropriate for your deployment.

Successful results are estimated practice scores, never official IELTS results. Task 2 has twice the weight of Task 1 when both are submitted. A single-task report is only an estimate for that task. Task 1 visual materials are not yet supported in the AI request: do not publish visual Task 1 assessments until image support is implemented. A human benchmark calibration is still required before commercial use.

Failed jobs retain the submitted answers and no band is fabricated. In Django admin, inspect Assessment jobs, fix the credential/model/quota issue, then select the retry action. Automatic retry is bounded at three provider requests. A worker crash may replay an external request after the lease expires, but only the current lease can store its result.

## Voice pilot

Sign in with a staff account. Open Profile and select the Speaking administrator test. Allow microphone access on HTTPS or localhost. The server creates a single-use ephemeral token with locked model/system instructions; the browser connects directly to Gemini. The long-lived provider key never reaches the browser.

The pilot sends PCM microphone audio, plays model audio, handles interruptions, and closes after five minutes. It is a technical conversation test, not a full three-part IELTS Speaking exam. It does not save recordings, score pronunciation, resume interrupted sessions, or grant paid Speaking attempts. Student access remains blocked until these are implemented and validated.

## Sources used for protocol implementation

- https://ai.google.dev/api/generate-content
- https://ai.google.dev/api/live
- https://ai.google.dev/gemini-api/docs/live-api/ephemeral-tokens

## Validation

21 Django tests pass, including invalid scores, invented evidence, duplicate task output, worker idempotency, quota failure, staff-only voice access and constrained token creation. Frontend TypeScript/build validation is performed separately. End-to-end provider, browser microphone and production load tests remain required.

## Speaking studio (2026-09-13)

Open the Speaking card or the profile's Speaking button. The studio has a static vector examiner avatar, measured microphone waveform, mute/end controls and automatic Part 1 (4 min), preparation (1 min), Part 2 (2 min), Part 3 (4 min) transitions. These are practice timings, not a validated full IELTS exam. Each speaking part uses a fresh one-use, five-minute token.

Microphone test runs locally for 15 seconds without sending audio to AI. Speaker test plays a short tone. Use localhost or HTTPS and grant microphone permission. AI conversation sends audio directly to Google; transcriptions are hidden until practice ends, held only in browser memory and cleared on leaving. Recording persistence, band scoring, error feedback and lip-synced video are not implemented.

Staff can test when AI_ENABLED=1 and GEMINI_API_KEY is set. Ordinary signed-in accounts additionally require VOICE_PRACTICE_ENABLED=1 (disabled by default). This separate ungraded mode does not grant paid exam access. Token throttling remains enabled. `/api/voice/status/` reports configuration/access without secrets; it does not perform a live provider health check.

Token requests use REST bidiGenerateContentSetup (model, generationConfig and systemInstruction at setup level; liveConnectConstraints is not a REST AuthToken field) and a configurable current Live model. Error feedback distinguishes missing configuration, disabled access, provider errors, quota, microphone permission/device problems and timeout. Each socket has a 20-second setup timeout; disconnects stop capture/playback. Live provider and browser verification remain pending.

Start locally from backend (Django does not auto-load .env):

```bash
source .venv/bin/activate
export DJANGO_DEBUG=1
export AI_ENABLED=1
export GEMINI_LIVE_MODEL=gemini-3.1-flash-live-preview
export GEMINI_API_KEY="$(python -c 'import getpass; print(getpass.getpass("Gemini API key: "))')"
python manage.py runserver 8001
```

The key prompt is hidden; its value is not put into shell history. Do not paste keys into chat. Enable the optional student flag only when student practice should call your provider account.

References checked:
- https://ai.google.dev/gemini-api/docs/live-api/ephemeral-tokens
- https://ai.google.dev/api/live
