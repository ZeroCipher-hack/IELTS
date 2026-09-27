#!/usr/bin/env bash
# Backend (Django + SQLite), baholash worker va frontend (Next.js)ni
# bitta buyruq bilan ishga tushiradi. To'xtatish uchun: Ctrl+C.
set -e
cd "$(dirname "$0")"

BACKEND_PORT="${BACKEND_PORT:-8001}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

echo "==> Backend: virtual muhitni tekshirish..."
cd backend
if [ ! -d ".venv" ]; then
  echo "    .venv topilmadi, yaratilmoqda..."
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
  echo "    .env topilmadi, .env.example dan nusxa olinmoqda."
  echo "    !!! backend/.env ichiga GEMINI_API_KEY kiritishni unutmang !!!"
  cp .env.example .env
fi

echo "==> Ma'lumotlar bazasi (SQLite): migratsiyalar qo'llanmoqda..."
python manage.py migrate

echo "==> Backend http://127.0.0.1:${BACKEND_PORT} da ishga tushmoqda..."
python manage.py runserver "127.0.0.1:${BACKEND_PORT}" &
BACKEND_PID=$!

echo "==> Baholash worker'i (Writing/Speaking) ishga tushmoqda..."
python manage.py assess_pending --watch &
WORKER_PID=$!

cd ../frontend
if [ ! -f ".env.local" ]; then
  echo "BACKEND_URL=http://127.0.0.1:${BACKEND_PORT}" > .env.local
  echo "    frontend/.env.local yaratildi (BACKEND_URL=http://127.0.0.1:${BACKEND_PORT})"
fi

echo "==> Frontend bog'liqliklari tekshirilmoqda (pnpm)..."
if command -v corepack >/dev/null 2>&1; then
  corepack enable >/dev/null 2>&1 || true
fi
pnpm install

echo "==> Frontend http://localhost:${FRONTEND_PORT} da ishga tushmoqda..."
pnpm dev &
FRONTEND_PID=$!

cleanup() {
  echo ""
  echo "==> To'xtatilmoqda..."
  kill "$BACKEND_PID" "$WORKER_PID" "$FRONTEND_PID" 2>/dev/null || true
  wait 2>/dev/null || true
  echo "==> Hammasi to'xtatildi."
}
trap cleanup INT TERM

echo ""
echo "=================================================="
echo " Backend:  http://127.0.0.1:${BACKEND_PORT}/api/health/"
echo " Frontend: http://localhost:${FRONTEND_PORT}"
echo " To'xtatish uchun: Ctrl+C"
echo "=================================================="

wait
