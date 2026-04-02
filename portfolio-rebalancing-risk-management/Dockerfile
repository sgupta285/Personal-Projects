FROM python:3.11-slim
WORKDIR /app
COPY requirements-lite.txt requirements-lite.txt
RUN pip install --no-cache-dir -r requirements-lite.txt
COPY . .
ENV PYTHONPATH=/app/src
CMD ["python", "scripts/run_demo.py"]
