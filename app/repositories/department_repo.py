from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased
from app.models.departments import Department, Employee
from datetime import date, datetime
from app.core.config import settings


class DepartamentRepository:
    """Репозиторий для работы с моделями Departament."""

    @staticmethod
    def get_by_id(
        db: Session, department_id: int
    ) -> Department | None:
        return db.query(Department).get(department_id)
 
    @staticmethod
    def get_children(db: Session, parent_id: int) -> list[Department]:
        return db.query(Department).filter(Department.parent_id == parent_id).all()
    
    @staticmethod
    def get_employees(db: Session, department_id: int) -> list[Employee]:
        return db.query(Employee).filter(Employee.department_id == department_id).all()
    
    @staticmethod
    def create(db: Session, name: str, parent_id: int | None = None) -> Department:
        department = Department(name=name, parent_id=parent_id)
        db.add(department)
        db.commit()
        db.refresh(department)
        return department

    @staticmethod
    def update(db: Session, department: Department, **kwargs) -> Department:
        for key, value in kwargs.items():
            setattr(department, key, value)
        db.commit()
        db.refresh(department)
        return department
    
    @staticmethod
    def delete(db: Session, department_id: int) -> None:
        db.delete(db.query(Department).get(department_id))
        db.commit()

    @staticmethod
    def add_employee(
        db: Session,
        department_id: int,
        full_name: str,
        position: str,
        hired_at: date,
    ) -> Employee:
        pass