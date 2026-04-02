FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
COPY scripts ./scripts
COPY data ./data
COPY artifacts ./artifacts
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .
CMD ["python", "scripts/run_pipeline.py"]
