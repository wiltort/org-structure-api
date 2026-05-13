from sqlalchemy.orm import Session
from app.repositories.department_repo import DepartmentRepository
from app.schemas.departments import DepartamentCreate, DepartamentResponse, DepartamentUpdate

class DepartmentService:
    """Сервис для работы с отделами"""
    
    @staticmethod
    def get_by_id(db: Session, department_id: int) -> DepartamentResponse | None:
        departament = DepartmentRepository.get_by_id(db, department_id)
        if departament:
            return DepartamentResponse.model_validate(departament)
        return None
    
    @staticmethod
    def 

    @classmethod
    def get_tree_and_employees(
        cls,
        db: Session,
        department_id: int,
        depth: int = 1,
        include_employees: bool = False,
    ) -> dict | None:
        # 1. Получаем сырые данные через репозиторий
        department = DepartmentRepository.get_by_id(db, department_id)
        if not department:
            return None
        
        # 2. Строим результат
        result = {
            'id': department.id,
            'name': department.name,
            'parent_id': department.parent_id,
            'created_at': department.created_at,
            'children': [],
            'employees': []
        }
        
        # 3. Добавляем сотрудников (если нужно)
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
        
        # 4. Добавляем детей рекурсивно (если нужно)
        if depth > 0:
            result['children'] = cls._get_children_tree(db, department_id, depth, include_employees)
        
        return result
    
    @classmethod
    def _get_children_tree(
        cls,
        db: Session,
        parent_id: int,
        depth: int,
        include_employees: bool
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
            
            # Рекурсивно получаем детей следующего уровня
            child_dict['children'] = cls._get_children_tree(
                db, child.id, depth - 1, include_employees
            )
            
            result.append(child_dict)
        
        return result