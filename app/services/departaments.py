import logging
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.repositories.department_repo import DepartmentRepository
from app.schemas.departments import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
    EmployeeCreate,
    EmployeeResponse,
    DepartmentTreeResponse,
    ModeEnum,
)


logger = logging.getLogger(__name__)


class DepartmentService:
    """Сервис для работы с отделами"""
    
    @staticmethod
    def get_by_id(db: Session, department_id: int) -> DepartmentResponse | None:
        departament = DepartmentRepository.get_by_id(db, department_id)
        if departament:
            return DepartmentResponse.model_validate(departament)
        return None
    
    @staticmethod
    def create(db: Session, departament: DepartmentCreate) -> DepartmentResponse:
        if departament.parent_id is not None:
            parent = DepartmentRepository.get_by_id(db, departament.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent department not found"
                )
        existing = DepartmentRepository.find_one_or_none(db, parent_id=departament.parent_id,
                                             name=departament.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department with this name already exists"
            )
        try:
            departament = DepartmentRepository.create(db, **departament.model_dump())
        except IntegrityError as e:
            db.rollback()
            logger.error(f"IntegrityError: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        return DepartmentResponse.model_validate(departament)
    
    @staticmethod
    def add_employee(
        db: Session,
        department_id: int,
        employee: EmployeeCreate
    ) -> EmployeeResponse | None:
        department = DepartmentRepository.get_by_id(db, department_id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        try:
            employee = DepartmentRepository.add_employee(
                db, 
                department_id=department_id, 
                **employee.model_dump()
            )
        except IntegrityError as e:
            db.rollback()
            logger.error(f"IntegrityError: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        return EmployeeResponse.model_validate(employee)


    @classmethod
    def get_tree_and_employees(
        cls,
        db: Session,
        department_id: int,
        depth: int = 1,
        include_employees: bool = False,
    ) -> DepartmentTreeResponse | None:
        department = DepartmentRepository.get_by_id(db, department_id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        result = {
            'id': department.id,
            'name': department.name,
            'parent_id': department.parent_id,
            'created_at': department.created_at,
            'children': [],
            'employees': []
        }
        
        if include_employees:
            employees = DepartmentRepository.get_employees(db, department_id)
            result['employees'] = [
                {
                    'id': e.id,
                    'full_name': e.full_name,
                    'position': e.position,
                    'hired_at': e.hired_at,
                    'created_at': e.created_at
                }
                for e in employees
            ]
        
        if depth > 0:
            result['children'] = cls._get_children_tree(db, department_id, depth)
        
        return result
    
    @classmethod
    def _get_children_tree(
        cls,
        db: Session,
        parent_id: int,
        depth: int,
        include_employees: bool = False
    ) -> list[dict]:
        """Рекурсивное построение дерева детей (приватный метод)"""
        if depth <= 0:
            return []
        
        children = DepartmentRepository.get_children(db, parent_id)
        result = []
        
        for child in children:
            child_dict = {
                'id': child.id,
                'name': child.name,
                'parent_id': child.parent_id,
                'created_at': child.created_at,
                'children': [],
                'employees': []
            }
            
            if include_employees:
                employees = DepartmentRepository.get_employees(db, child.id)
                child_dict['employees'] = [
                    {'id': e.id, 'full_name': e.full_name, 'position': e.position}
                    for e in employees
                ]
            
            child_dict['children'] = cls._get_children_tree(
                db, child.id, depth - 1, include_employees
            )
            
            result.append(child_dict)
        
        return result
    
    @staticmethod
    def update(db: Session, department_id: int, department_update: DepartmentUpdate) -> DepartmentResponse:
        department = DepartmentRepository.get_by_id(db, department_id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        new_parent_id = department_update.parent_id
        if new_parent_id is not None:
            new_parent = DepartmentRepository.get_by_id(db, new_parent_id)
            if not new_parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent department not found"
                )
            if new_parent_id == department_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department cannot be its own parent"
                )
            if new_parent_id == department.parent_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New parent is equal to current parent"
                )
            all_parents = DepartmentRepository.get_all_parents_ids(db, new_parent_id)
            if department_id in all_parents:
                # Получаем циклическое дерево
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Cannot move department into its own descendant (cycle detected)"
                )
        new_name = department_update.name
        params = {
            'parent_id': new_parent_id if new_parent_id else department.parent_id,
            'name': new_name.strip() if new_name else department.name
        }
        existing = DepartmentRepository.find_one_or_none(db, **params)
        if existing and existing.id != department_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department with this name already exists"
            )
        try:
            department = DepartmentRepository.update(
                db,
                department,
                **department_update.model_dump(exclude_unset=True)
            )
        except IntegrityError as e:
            db.rollback()
            logger.error(f"IntegrityError: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        return department
    
    @classmethod
    def delete(
        cls,
        db: Session,
        department_id: int,
        mode: ModeEnum,
        reassign_to_department_id: int | None = None
    ) -> None:

        department = DepartmentRepository.get_by_id(db, department_id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        if mode == ModeEnum.REASSIGN:
            if reassign_to_department_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="reassign_to_department_id is required"
                )
            if reassign_to_department_id == department_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="reassign_to_department_id cannot be equal to department_id"
                )
            new_departament = DepartmentRepository.get_by_id(db, reassign_to_department_id)
            if not new_departament:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="New department not found"
                )
            children = DepartmentRepository.get_all_children(db, department_id)
            for child in children:
                dep_update = DepartmentUpdate(parent_id=reassign_to_department_id)
                DepartmentRepository.update(db, child, dep_update)
            employees = DepartmentRepository.get_all_employees(db, department_id)
            DepartmentRepository.reassign_employees(db, employees, reassign_to_department_id)
        try:
            DepartmentRepository.delete(db, department)
        except IntegrityError as e:
            db.rollback()
            logger.error(f"IntegrityError: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )