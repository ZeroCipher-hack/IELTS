# Server setup

The primary frontend now uses real Django accounts and data. `/design` preserves the earlier explicitly labelled mockup. No AI or payment credentials are needed for Reading/Listening or collecting Writing responses. A paid public launch is NOT yet ready.

## Local

1. Backend: create a virtualenv, install `backend/requirements.txt`.
2. Set `DJANGO_DEBUG=1`, run `python manage.py migrate`, optionally `python manage.py seed_demo`, then `python manage.py runserver` inside backend.
3. Frontend: Node 22+, `corepack enable`, `pnpm install --frozen-lockfile`.
4. Set `BACKEND_URL=http://127.0.0.1:8000`, run `pnpm dev`. Use `--webpack` if a workspace symlink prevents Turbopack from resolving dependencies.
5. Create staff with `python manage.py createsuperuser`. Access `/admin/`.

## VPS with Docker Compose

1. Point your domain to the server; allow incoming 80/443. Install Docker and Compose.
2. Copy `.env.example` to `.env`. Set your real domain, strong random secret/password, exact allowed host and HTTPS trusted origin. Never commit `.env`.
3. `docker compose build`
4. `docker compose up -d db`
5. `docker compose run --rm backend python manage.py migrate`
6. `docker compose run --rm backend python manage.py collectstatic --noinput`
7. `docker compose run --rm backend python manage.py createsuperuser`
8. `docker compose up -d`

Caddy obtains HTTPS certificates. Database and backend have no public port mapping. Trust forwarded HTTPS only behind this proxy. Do not expose backend directly when DJANGO_TRUST_PROXY=1.

Run `docker compose exec -T backend python manage.py expire_attempts` every minute via the server scheduler. Expired attempts also finalize when the student opens their history or attempt. No always-on AI worker is installed yet.

Run `sh deploy/backup.sh /private/path/backups` daily from the repository root. Copy backups to separate storage. Test restoration into a separate empty database with `pg_restore`; do not overwrite the live database during a restoration test. Monitor disk space, TLS, errors and backup age.

Docker configuration is provided but must be built and exercised on the target server. It is not a claim of tested container deployment or 50-session capacity.

## Content workflow

Create an exam draft in Django admin, then add questions. JSON arrays are required for choices and accepted answers, e.g. `["TRUE", "FALSE", "NOT GIVEN"]`. For short answers use empty choices and a list of accepted strings. Writing tasks use empty answer keys. Use HTTPS audio URLs for Listening.

Select **Tekshirish va nashr qilish** in the exam list. Invalid drafts are rejected. Published fields cannot be edited in admin; use **Yangi versiyaga nusxalash** to create a new draft. Attempts keep immutable content snapshots.

Bulk import: `python manage.py import_exam /path/to/exam.json`. It validates and creates a draft, never publishes automatically. Schema: title, section, duration_seconds, passage, audio_url, questions (prompt, choices, accepted_answers, evidence, explanation, skill_tag). Question positions are assigned in list order.

## Remaining launch gates

- Speaking realtime conversation and audio-based assessment are unimplemented.
- Writing responses wait for assessment; rubric calibration and provider worker remain.
- Full four-section orchestration and combined band calculation remain.
- Merchant payment adapter, signed callbacks, refunds and purchase records remain.
- Full real test materials, rights checks and independently marked benchmark answers remain.
- Verified email/password recovery and stronger free-attempt abuse prevention remain.
- Backend validation messages and admin-entered explanations currently remain in their source language; primary UI supports UZ/EN/RU.
- Load testing, backup restore drill, production monitoring and final accessibility review remain.

## AI pilot update
Writing provider/worker and a staff-only voice pilot are now implemented; see AI_SETUP.md. Full Speaking timing, audio retention and audio-based scoring still remain. Enable Compose profile `ai` only after configuring the server key.
