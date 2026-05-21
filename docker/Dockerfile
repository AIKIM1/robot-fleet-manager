FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[test]"

COPY src/ src/
COPY tests/ tests/
COPY scripts/ scripts/

# For MuJoCo headless rendering
ENV MUJOCO_GL=egl

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
