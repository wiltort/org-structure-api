import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from typing import Generator, Any
import os

from app.core.database import Base, get_db
from app.main import app
from app.core.config import Settings


def get_settings_override() -> Settings:
    """Переопределение настроек для тестового окружения."""
    return Settings(
        db_name=":memory:",
        db_user="",
        db_password="",
        db_host="",
        db_port=0,
    )


@pytest.fixture(scope="session")
def test_engine():
    """Создание тестового движка SQLAlchemy с SQLite в памяти."""
    # Используем SQLite в памяти для тестов
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Установите True для отладки SQL запросов
    )
    
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Очищаем после завершения
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """Фикстура для тестовой сессии базы данных."""
    connection = test_engine.connect()
    transaction = connection.begin()
    
    # Создаем сессию, привязанную к соединению
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=connection,
    )
    
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Фикстура для тестового клиента FastAPI с переопределенной зависимостью БД."""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Сессия закрывается в фикстуре db_session
    
    # Переопределяем зависимость get_db
    app.dependency_overrides[get_db] = override_get_db
    
    # Переопределяем настройки
    app.dependency_overrides[Settings] = get_settings_override
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Очищаем переопределения после теста
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_department_data() -> dict[str, Any]:
    """Тестовые данные для создания отдела."""
    return {
        "name": "Тестовый отдел",
        "parent_id": None,
    }


@pytest.fixture(scope="function")
def test_employee_data() -> dict[str, Any]:
    """Тестовые данные для создания сотрудника."""
    return {
        "full_name": "Иванов Иван Иванович",
        "position": "Тестовый разработчик",
        "hired_at": "2023-01-15",
        "department_id": 1,
    }


@pytest.fixture(scope="function")
def sample_department(db_session: Session) -> dict[str, Any]:
    """Создает тестовый отдел в базе данных."""
    from app.models.departments import Department
    from datetime import datetime
    
    department = Department(
        name="Отдел разработки",
        parent_id=None,
        created_at=datetime.now(),
    )
    
    db_session.add(department)
    db_session.commit()
    db_session.refresh(department)
    
    return {
        "id": department.id,
        "name": department.name,
        "parent_id": department.parent_id,
    }


@pytest.fixture(scope="function")
def sample_employee(db_session: Session, sample_department: dict[str, Any]) -> dict[str, Any]:
    """Создает тестового сотрудника в базе данных."""
    from app.models.departments import Employee
    from datetime import date, datetime
    
    employee = Employee(
        full_name="Петров Петр Петрович",
        position="Старший разработчик",
        hired_at=date(2022, 5, 10),
        department_id=sample_department["id"],
        created_at=datetime.now(),
    )
    
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    
    return {
        "id": employee.id,
        "full_name": employee.full_name,
        "position": employee.position,
        "hired_at": employee.hired_at,
        "department_id": employee.department_id,
    }


@pytest.fixture(scope="function", autouse=True)
def cleanup_test_data(db_session: Session):
    """Автоматически очищает тестовые данные после каждого теста."""
    # Сохраняем текущее состояние
    yield
    
    # Очищаем таблицы в правильном порядке (из-за foreign key constraints)
    from app.models.departments import Employee, Department
    
    db_session.query(Employee).delete()
    db_session.query(Department).delete()
    db_session.commit()