FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY api ./api
COPY dashboard ./dashboard
COPY scripts ./scripts
COPY docs ./docs
COPY data ./data
COPY sql ./sql
COPY artifacts ./artifacts
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -e .
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
