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
COPY shared.py .
CMD ["uvicorn", "main_app:app", "--host", "0.0.0.0", "--port", "8000"]


FROM base AS image
COPY image_worker.py .
COPY shared.py .
CMD ["sh", "-c", "uvicorn image_worker:app --host 0.0.0.0 --port ${PORT}"]


FROM base AS migrate
COPY alembic.ini .
COPY migrations migrations
COPY db db
CMD ["alembic", "upgrade", "head"]

FROM base AS runner
COPY infra/security.py infra/security.py
COPY adapters/db.py adapters/db.py
COPY adapters/uow.py adapters/uow.py
COPY adapters/db_provider.py adapters/db_provider.py
COPY domain domain
COPY db db
COPY scripts/add_admins.py ./add_admins.py
CMD ["python", "-m", "add_admins"]

FROM base AS resize-images-script
COPY image_worker.py .
COPY shared.py .
COPY scripts/resize_images.py ./resize_images.py
CMD ["python", "-m", "resize_images"]

FROM base AS migrate_paths_script
COPY scripts/collection_paths.py .
COPY domain domain
COPY adapters/db.py adapters/db.py
COPY db db
COPY adapters/db_provider.py adapters/db_provider.py
CMD ["python", "collection_paths.py"]

FROM base AS fix-extensions-script
COPY scripts/fix_extensions.py ./fix_extensions.py
COPY adapters adapters
COPY domain domain
COPY db db
COPY infra infra
CMD ["python", "fix_extensions.py"]


FROM base AS int_tests
COPY core ./core
COPY tests ./tests
COPY db ./db
COPY services ./services
COPY infra ./infra
COPY domain ./domain
COPY adapters adapters
COPY pytest.ini ./pytest.ini
COPY shared.py .
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
COPY shared.py .
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
COPY shared.py shared.py
CMD ["pytest", "tests/e2e"]

