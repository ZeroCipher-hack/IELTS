# IELTSQA

IELTS Academic mock examination platform. Repository: ZeroCipher-hack/IELTS.

## Implemented
- Bargsiz academic design: warm white, forest green, speech-bubble identity.
- Frontend demo: sample reports, criterion explanations, weekly checklist, Writing editor and microphone recording.
- Django backend: email/password accounts, session + CSRF protection, database-backed test catalog, staff administration, immutable attempt snapshots, server-owned deadlines, answer saving, deterministic Reading/Listening grading and user-isolated history.
- One free attempt per account and staff-issued subsequent entitlements. This is NOT phone-verified free-trial protection yet.
- Frontend account portal: register/login, start/resume, save answers, submit and reopen results when backend is connected.

## Not ready for paid launch
Full-length validated IELTS content, AI Writing/Speaking grading, live voice interviewer, actual payments, phone verification, full UZ/EN/RU localization and 50-session load verification are not implemented. No fake AI grades or payment-success responses are returned. The five-question demo returns a raw score, not an IELTS band. The public hosted demo currently has no Django backend attached; its account portal reports this clearly.

## Local setup
Requires Python 3.11+ and Node.js 22.13+, with pnpm installed.

Terminal 1:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DJANGO_DEBUG=1
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```
Admin: http://127.0.0.1:8000/admin/

Terminal 2:
```bash
cd frontend
pnpm install --frozen-lockfile
BACKEND_URL=http://127.0.0.1:8000 pnpm dev
```
Open http://localhost:3000 and select **Mening hisobim**. The other dashboard views are explicitly illustrative. The backend uses SQLite for local development. For PostgreSQL install the production extras and set the POSTGRES_* variables. Environment templates are examples, not automatically loaded by Django.

## Verify
```bash
cd backend
DJANGO_DEBUG=1 .venv/bin/python manage.py test exams
cd ../frontend
pnpm build
```

## Structure
- frontend/: Next.js + TypeScript, no Sites account dependency.
- backend/: Django API, admin, models, migrations, seed command and tests.
- docs/: architecture, design and integration checklist.

Only original demonstration content belongs in this public repository. Do not commit real user records, paid answer keys, credentials or database files.
