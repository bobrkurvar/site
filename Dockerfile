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
COPY infra ./infra
COPY adapters adapters
COPY services ./services
COPY static/js ./static/js
COPY static/css ./static/css
COPY templates ./templates
COPY contracts ./contracts
CMD ["uvicorn", "main_app:app", "--host", "0.0.0.0", "--port", "8000"]


FROM base AS image
COPY image_worker.py .
COPY contracts ./contracts
CMD ["sh", "-c", "uvicorn image_worker:app --host 0.0.0.0 --port ${PORT}"]


FROM base AS migrate
COPY alembic.ini .
COPY migrations migrations
COPY db db
ENTRYPOINT ["alembic"]
CMD ["upgrade", "head"]

FROM base AS runner
COPY infra/security.py infra/security.py
COPY adapters/db.py adapters/db.py
COPY adapters/uow.py adapters/uow.py
COPY adapters/db_provider.py adapters/db_provider.py
COPY domain domain
COPY db db
COPY adapters/query_service.py adapters/query_service.py
COPY services services
COPY scripts/add_admins.py ./add_admins.py
CMD ["python", "-m", "add_admins"]

FROM base AS generate_miniatures
COPY image_worker.py .
COPY contracts ./contracts
COPY scripts/generate_miniatures.py ./generate_miniatures.py
CMD ["python", "-m", "generate_miniatures"]


FROM base AS rename_collections
COPY scripts/rename_collections.py ./rename_collections.py
COPY adapters ./adapters
COPY db ./db
COPY domain ./ domain
COPY services ./services
COPY contracts ./contracts
COPY infra ./infra
CMD ["python", "-m", "rename_collections"]


FROM base AS int_tests
COPY core ./core
COPY tests ./tests
COPY db ./db
COPY services ./services
COPY infra ./infra
COPY domain ./domain
COPY adapters adapters
COPY pytest.ini ./pytest.ini
COPY contracts ./contracts
WORKDIR /pysite/tests/integrations
ENV PYTHONPATH=/pysite
ENTRYPOINT ["pytest"]

FROM base AS unit_tests
COPY core ./core
COPY tests ./tests
COPY services ./services
COPY domain ./domain
COPY adapters adapters
COPY infra ./infra
COPY pytest.ini ./pytest.ini
COPY contracts ./contracts
WORKDIR /pysite/tests/unit
ENV PYTHONPATH=/pysite
ENTRYPOINT ["pytest"]


FROM mcr.microsoft.com/playwright/python:v1.58.0-noble AS e2e_tests
WORKDIR /pysite
COPY req.txt .
RUN pip install --no-cache-dir -r req.txt
COPY core core
COPY tests tests
COPY services services
COPY infra infra
COPY domain domain
COPY pytest.ini pytest.ini
COPY adapters adapters
COPY db db
COPY contracts contracts
WORKDIR /pysite/tests/e2e
ENV PYTHONPATH=/pysite
ENTRYPOINT ["pytest"]

FROM nginx:1.27-alpine AS custom_nginx

COPY nginx/site.conf /etc/nginx/conf.d/default.conf
COPY nginx/snippets /etc/nginx/snippets

COPY static/css /var/www/static/css
COPY static/js /var/www/static/js