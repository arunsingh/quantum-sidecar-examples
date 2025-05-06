
---

## 2 Docker/runtime/Dockerfile (full)

```Dockerfile
# syntax=docker/dockerfile:1.6
ARG PY=3.11
FROM python:${PY}-slim-bullseye AS base

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc git curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV && \
    $VIRTUAL_ENV/bin/pip install --upgrade pip

ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python","-m","ipykernel_launcher","-f","/dev/null"]
