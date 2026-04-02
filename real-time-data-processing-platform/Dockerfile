FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app/src
EXPOSE 8000
CMD ["uvicorn", "rtdp.api:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
