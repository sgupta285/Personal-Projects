FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts
COPY dashboard ./dashboard
COPY sql ./sql
COPY docs ./docs
COPY data ./data
COPY artifacts ./artifacts
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -e .
EXPOSE 8501
CMD ["streamlit", "run", "dashboard/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
