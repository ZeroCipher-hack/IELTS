# IELTSQA architecture

## Agreed product requirements
IELTS Academic first. Full and separate-section exams are paid. One chosen section is free once per verified user. Planned full-exam price: 200,000 UZS; individual prices depend on measured operating costs. Uzbek payment methods. UZ/EN/RU interface and reports, English test content. Target: 50 simultaneous sessions, including a separate voice-concurrency test. Initial demo target: one week. School finances promotion and operating budget.

## Current implementation
Only the frontend prototype exists. Next.js + React + TypeScript, device-local writing drafts/checklists/question drafts. Recording stays in browser memory. Scores/history are illustrative. No authentication, real payment or AI services are integrated.

## Proposed production architecture
Frontend -> Django REST API -> PostgreSQL.
API -> object storage for audio, images and transcripts.
API -> Redis/Celery queue -> AI assessment -> saved report.
Browser -> authorized short-lived voice session -> voice provider.
Payment provider -> authenticated, verified, idempotent callback -> payment record -> exam entitlement.

Django and Celery are proposed, not installed in this repository yet. Model/provider selection follows measured grading quality, latency and cost.

## Core entities
User, target, exam version, section, material, question, accepted answer, attempt, response, recording, assessment, criterion score, evidence reference, recommendation, weekly plan, payment, entitlement and free-attempt claim.

## Exam integrity
Server owns deadlines and submission state. Save responses incrementally. Attempt pins an immutable exam version. Do not disclose answer keys in exam APIs. Retries and reconnects must not duplicate attempts, payment charges or grading work. A unique transactional claim enforces the one-free-section rule.

## Assessment
Listening/Reading: deterministic answer-key comparison with explicit normalization and accepted variants. Convert raw scores only using validated test-specific mapping; no band from a five-question exercise.
Writing/Speaking: criterion-based estimated scores, response-linked evidence and uncertainty. Pronunciation requires original audio, not transcript alone. Compare assessment against independently marked examples before paid launch. Provider failures leave grading pending/retryable, never invent a score.

## Content management
Editors enter passages, questions, images, audio, transcripts, word limits, accepted answers, skill tags and evidence locations. Draft -> preview -> published version. Editing a published test creates a new version without changing previous attempts.

## Release gates
Complete original or appropriately licensed test set; server accounts and storage; validated AI assessment; voice flow; payment sandbox and reconciliation; localization; browser E2E and responsive checks; 50-session load exercise; backup/recovery and access controls.
