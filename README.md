# API Организационной Структуры

REST API для управления структурой компании: подразделениями и сотрудниками.

## Стек

- Python + FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Docker + docker-compose
- Alembic (миграции)

## Запуск

```bash
docker-compose up --build
```

API доступно по адресу: `http://localhost:8000`

## API Endpoints
- | POST | `/departments/` | Создать подразделение |
- | POST | `/departments/{id}/employees/` | Создать сотрудника |
- | GET | `/departments/{id}?depth=1&include_employees=true` | Получить подразделение с деревом |
- | PATCH | `/departments/{id}` | Обновить подразделение (name, parent_id) |
- | DELETE | `/departments/{id}?mode=reassign&reassign_to_department_id=X` | Удалить подразделение |

## Тесты

```bash
docker-compose exec app pytest
```

## OpenAPI

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
