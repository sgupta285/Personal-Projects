FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends build-essential make binutils && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
COPY . /workspace
RUN pip install --no-cache-dir -e .
CMD ["python", "-m", "fwtool.cli", "hil", "--version", "0.3.0", "--port", "9130"]
