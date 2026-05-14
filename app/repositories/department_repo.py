from sqlalchemy.orm import Session
from app.models.departments import Department, Employee
from datetime import date

class DepartmentRepository:
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
        query = db.query(Employee).filter(Employee.department_id == department_id)
        query = query.order_by(Employee.full_name).all()
        return query
    
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
    def delete(db: Session, department: Department) -> None:
        db.delete(department)
        db.commit()

    @staticmethod
    def add_employee(
        db: Session,
        department_id: int,
        full_name: str,
        position: str,
        hired_at: date,
    ) -> Employee:
        employee = Employee(
            department_id=department_id,
            full_name=full_name,
            position=position,
            hired_at=hired_at,
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)
        return employee
    
    @staticmethod
    def find_one_or_none(
        db: Session,
        parent_id: int | None = None,
        name: str | None = None
    ) -> Department | None:
        query = db.query(Department)
        if parent_id:
            query = query.filter(Department.parent_id == parent_id)
        if name:
            query = query.filter(Department.name == name)
        return query.first()
    
    @classmethod
    def get_all_parents_ids(cls, db: Session, department_id: int) -> list[int]:
        parents_ids = []
        department = cls.get_by_id(db, department_id)
        while department.parent_id:
            parents_ids.append(department.parent_id)
            department = cls.get_by_id(db, department.parent_id)
        return parents_ids
    
    @staticmethod
    def get_all_children(db: Session, departament_id: int) -> list[Department]:
        children = db.query(Department).filter(Department.parent_id == departament_id).all()
        return children
    
    @staticmethod
    def get_all_employees(db: Session, departament_id: int) -> list[Employee]:
        employees = db.query(Employee).filter(departament_id == departament_id).all()
        return employees
    
    @staticmethod
    def reassign_employees(db: Session, employees: list[Employee], departament_id: int) -> None:
        for employee in employees:
            employee.departament_id = departament_id
        db.commit()
