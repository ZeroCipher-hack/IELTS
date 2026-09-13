# Integration review — 2026-09-13

## Implemented in this change

- Authenticated `/api/analytics/` endpoint exposes only the current account's latest 100 graded attempts, without answer content. Four module panels render SVG charts and accessible tables. Reading/Listening raw results are separated by exam, content snapshot and question total; AI bands are separated by model, rubric, scope and submitted tasks. Unknown AI metadata remains isolated. Pending assessments are excluded; zero scores are retained.
- UI import audit: 61 components reduced to the 12 used directly or transitively by the historical design route. 49 unused components removed. Remaining components do not use custom vendor variants or effects, so the vendor stylesheet was removed. Tailwind and animation packages remain in package.json and pnpm-lock.yaml.
- Direct production dependencies reduced to 8 and dev dependencies to 9. An unimported TSX file does not automatically become shipped JavaScript, so file count is not a JS-bundle measurement. The measured primary CSS output fell from approximately 159 KB to 63 KB after pruning Tailwind scan sources and vendor rules (uncompressed).
- Validation: 31 backend tests, Next production build and TypeScript passed. Browser interaction and live provider testing remain pending.

## Real-time assessment: pending implementation

Speaking audio already uses a browser-to-Gemini WebSocket with server-issued short-lived tokens. Writing assessment runs in a separate worker and the browser polls every five seconds; this is distinct from live audio transport. Current states include pending/running/done/failed/disabled. Do not invent a percentage while a provider request is in progress.

Current production deployment is synchronous Gunicorn WSGI. Long-running SSE responses would occupy workers. Adopt ASGI before introducing authenticated per-attempt SSE, with disconnect cleanup, bounded stream lifetime, heartbeat, proxy buffering disabled and polling fallback. Channels/Redis are optional infrastructure, not prerequisites for the existing browser-to-provider voice session.

Reference: https://docs.djangoproject.com/en/5.2/ref/request-response/#streaminghttpresponse-objects

## Click / Payme: not connected

Keep payments unavailable until the transaction lifecycle is implemented and provider sandbox tests pass. Account-specific merchant credentials and a reachable HTTPS callback are needed for a live integration, but core transaction logic can be implemented beforehand.

Use a dedicated `payments` application for orders and immutable transaction records rather than adding all business logic to config. Configuration belongs in settings; payment callbacks should grant an exam entitlement only after a verified completed transaction. Required cases: exact server-side amount, duplicate callbacks, concurrent requests, cancel/refund handling, expired orders, and reconciliation. Do not grant access based on the browser's return URL. Do not add placeholder callbacks that always succeed.

Payme documents creation, completion, cancellation and status methods and provides sandbox scenarios. Click's documentation was not retrievable in this session, so its protocol was not implemented from memory.

References:
- https://developer.help.paycom.uz/metody-merchant-api/
- https://developer.help.paycom.uz/pesochnitsa/
- https://developer.help.paycom.uz/protokol-merchant-api/skhema-vzaimodeystviya/

## Audio storage: pending implementation

Listening currently accepts HTTPS URLs. The voice pilot does not retain recordings. Neither private S3 media storage nor a MinIO service was added in this change.

Proposed design: private S3-compatible bucket, unique object keys, metadata in the database, staff-only Listening uploads, and user recordings bound to an owned active attempt. Issue short-lived upload/download URLs only after checking authorization. Validate content size/type and uploaded objects; configure bucket CORS, retention/deletion policy and lifecycle cleanup. A presigned URL is temporary bearer access, not proof of user ownership. Keep storage keys server-side. Do not start retaining student voice recordings silently.

Reference: https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html
