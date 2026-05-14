# Базовый образ с Python
FROM python:3.12-slim as builder

# Установка системных зависимостей для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
ENV POETRY_VERSION=2.0.0 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN pip install poetry==$POETRY_VERSION

# Рабочая директория
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock* ./

# Установка зависимостей (без установки проекта)
RUN poetry install --no-root --no-interaction --no-ansi

# Финальный образ
FROM python:3.12-slim

# Установка системных зависимостей для runtime
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание непривилегированного пользователя
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Рабочая директория
WORKDIR /app

# Копирование виртуального окружения из builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Копирование кода приложения
COPY ./app /app/app

# Создание директории для логов
RUN mkdir -p /app/logs && chown -R appuser:appuser /app

# Переключение на непривилегированного пользователя
USER appuser

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Экспонирование порта
EXPOSE 8000

# Команда по умолчанию (будет переопределена в docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
