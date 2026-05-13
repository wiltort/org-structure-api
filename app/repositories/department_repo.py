from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased
from app.models.departments import Department, Employee
from datetime import datetime
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

# перенести в сервис
    @classmethod
    def get_children_tree(
        cls,
        db: Session,
        parent_id: int,
        depth: int = 1
    ) -> list[dict[str, any]]:
        children = db.query(Department).filter(Department.parent_id == parent_id).all()
        result = []
        if depth <= 1:
            for child in children:
                result.append({
                    'id': child.id,
                    'name': child.name,
                    'created_at': child.created_at,    
                })
            return result
        for child in children:
            result.append({
                'id': child.id,
                'name': child.name,
                'created_at': child.created_at,
                'children': cls.get_children_tree(db, child.id, depth-1),
            })
        return result

    @classmethod
    def get_tree_and_employees(
        cls,
        db: Session,
        department_id: int,
        depth: int = 1,
        include_employees: bool = False,
    ) -> dict[str, any] | None:
        
        department = db.query(Department).get(department_id)

        if not department:
            return None
        result = {
            'department': department,
            'employees': [],
            'children': cls.get_children_tree(db, department_id, depth),
        }
        if include_employees:
            result['employees'] = db.query(Employee).filter(Employee.department_id == department_id).all()
        return result

                
