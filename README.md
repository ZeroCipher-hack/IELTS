# IELTSQA

IELTS Academic mock exam and evidence-based performance analysis platform. Repository: `ZeroCipher-hack/IELTS`.

## Current stage
Interactive frontend prototype, not a production examination service.

Implemented: Uzbek dashboard, illustrative band reports and criterion dialogs, five-question Reading exercise with answer explanations, Writing Task 2 editor, local microphone recording/playback, weekly checklist and local question draft constructor.

Not implemented: accounts, server persistence, complete exam content, AI assessment, conversational voice AI, payment processing, full English/Russian localization, and 50-concurrent-session verification. Dashboard scores/history are sample data. The mini Reading exercise returns a raw score, not an IELTS band. Browser-local drafts are not a database. The question constructor is not a secured admin panel.

## Repository layout
- `frontend/`: Next.js + TypeScript interface, components and dependency lockfile.
- `docs/ARCHITECTURE.md`: agreed product requirements and proposed backend.
- `docs/DESIGN.md`: visual direction and screens.

## Run locally
Requires Node.js 22.13+ and pnpm. From the repository root:

```bash
cd frontend
pnpm install --frozen-lockfile
pnpm dev
```

Open http://localhost:3000. Microphone capture requires browser permission and localhost or HTTPS.

```bash
pnpm typecheck
pnpm build
pnpm start
```

The original prototype dependency set is retained for reproducibility; some packages are not yet used. This export runs with Next.js and has no Sites account or hosting configuration dependency.

## Data and credentials
Do not commit real student records, private test banks, paid answer keys or credentials. The included Reading exercise is an original demonstration. Configure future integration credentials on the server, not in client code.

## Design
Warm white, forest green and sage surfaces. Academic and language-focused identity with speech-bubble iconography. No leaves or nature-themed decoration.
