# Remaining integrations and launch requirements

## Backend hosting
Deploy Django separately from the frontend demo. Set a random DJANGO_SECRET_KEY, exact ALLOWED_HOSTS, HTTPS CSRF_TRUSTED_ORIGINS, PostgreSQL credentials and debug off. Run migrations. Set the frontend BACKEND_URL at build/runtime as required by the hosting provider. Do not expose SQLite or admin credentials in the repository. Production static files/reverse-proxy configuration still needs deployment-specific setup.

## AI
No API key is currently configured. Select and provision a model provider, then implement and validate Writing rubric output and audio-based Speaking assessment against independently marked examples. Conversation transport is separate from final assessment. Never grade pronunciation from transcript alone.

## Payments
Provider merchant credentials and sandbox access are required. Use verified callbacks, unique transactions, amount/currency checks and transactional entitlement grants. Current Entitlement records may only be granted by staff; no public payment endpoint exists.

## Content
Provide one complete Academic test: Listening audio/transcript/keys; Reading passages/keys/evidence; Writing graphics/prompts; Speaking prompts. The seeded test is only a five-question original Reading exercise.

## Verification completed
Thirteen Django tests cover authentication/CSRF, cross-user isolation, hidden answer keys, grading idempotency, one free attempt, expired deadlines, invalid answer keys and snapshot preservation. No claim is made of 50-session capacity or live provider readiness.

## September 12 product update

The main route now renders real authenticated data in UZ/EN/RU; the old sample UI is at `/design`. Writing collection is enabled with explicit acknowledgement that assessment is pending. Reading/Listening produce evidence rows and a rule-based weekly plan. Next-to-Django HTTP registration, CSRF, catalog, save, submit, history, profile and logout were exercised successfully after fixing rewrite trailing slashes. Browser verification could not run because Chromium download was blocked; Docker deployment and load tests are not yet verified. See DEPLOYMENT.md for exact setup and remaining launch gates.
