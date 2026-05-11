FROM python:3.12-slim
WORKDIR /app
COPY poetry.lock pyproject.toml .
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi --no-root
COPY src/travel_agency_backend ./travel_agency_backend
EXPOSE 8000
CMD ["sh", "-c", "uvicorn travel_agency_backend.main:app --host 0.0.0.0 --port $PORT"]