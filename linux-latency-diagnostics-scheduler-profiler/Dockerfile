FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md /app/
COPY latdiag /app/latdiag
RUN pip install --no-cache-dir -e .
ENTRYPOINT ["latdiag"]
