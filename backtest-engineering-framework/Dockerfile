FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt pyproject.toml README.md ./
COPY python ./python
COPY scripts ./scripts
COPY configs ./configs
COPY data ./data

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -e .

CMD ["python", "scripts/run_walk_forward.py", "--config", "configs/momentum_walk_forward.yaml"]
