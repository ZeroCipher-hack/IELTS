FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements-production.txt && useradd --create-home app
COPY . .
RUN mkdir -p /app/staticfiles && chown -R app:app /app
ARG DJANGO_SECRET_KEY=build-time-dummy-key
ENV DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
RUN python manage.py collectstatic --noinput
USER app
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-"]
