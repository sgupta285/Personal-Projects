FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts
COPY examples ./examples

ENV PYTHONPATH=/app/src
EXPOSE 8501

CMD ["streamlit", "run", "src/expower/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
