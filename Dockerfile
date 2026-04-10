FROM python:3.11-slim AS base

WORKDIR /pysite
COPY req.txt .
RUN pip install --no-cache-dir -r req.txt
COPY core ./core

FROM base AS main_app
COPY main_app.py .
COPY api ./api
COPY db ./db
COPY domain ./domain
COPY infrastructure ./infrastructure
COPY services ./services
COPY static/js ./static/js
COPY static/css ./static/css
COPY templates ./templates
CMD ["uvicorn", "main_app:app", "--host", "0.0.0.0", "--port", "8000"]


FROM base AS image
COPY image_worker.py .
CMD ["sh", "-c", "uvicorn image_worker:app --host 0.0.0.0 --port ${PORT}"]


FROM base AS migrate
COPY alembic.ini .
COPY migrations migrations
COPY db ./db
CMD ["alembic", "upgrade", "head"]

FROM base AS runner
COPY infrastructure ./infrastructure
COPY domain ./domain
COPY db ./db
COPY services/security.py ./services/security.py
COPY scripts/add_admins.py ./add_admins.py
CMD ["python", "-m", "add_admins"]


FROM base AS int_tests
COPY core ./core
COPY tests ./tests
COPY db ./db
COPY services ./services
COPY infrastructure ./infrastructure
COPY domain ./domain
COPY pytest.ini ./pytest.ini
CMD ["pytest", "tests/integrations"]


FROM mcr.microsoft.com/playwright/python:v1.58.0-noble AS e2e_tests
WORKDIR /pysite
COPY req.txt .
RUN pip install --no-cache-dir -r req.txt
COPY core ./core
COPY tests ./tests
COPY services ./services
COPY infrastructure ./infrastructure
COPY domain ./domain
COPY pytest.ini ./pytest.ini
CMD ["pytest", "tests/e2e"]


# FROM mcr.microsoft.com/playwright/python:v1.58.0-noble AS tests
# WORKDIR /pysite
# COPY req.txt .
# RUN pip install --no-cache-dir -r req.txt
# COPY core ./core
# COPY tests ./tests
# COPY services ./services
# COPY infrastructure ./infrastructure
# COPY domain ./domain
# COPY pytest.ini ./pytest.ini
# COPY db ./db
# CMD ["pytest", "tests/e2e", "tests/integrations"]