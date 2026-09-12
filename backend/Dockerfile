FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/workspace/backend
WORKDIR /workspace
COPY backend/requirements*.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements-dev.txt
COPY . /workspace
RUN useradd --create-home app && chown -R app:app /workspace
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
