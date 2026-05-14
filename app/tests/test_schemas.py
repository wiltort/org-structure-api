import pytest
from pydantic import ValidationError
from app.schemas.departments import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    EmployeeCreate,
    EmployeeUpdate,
    ModeEnum,
    DepartmentDeleteRequest,
)


class TestDepartmentCreate:
    """Тесты для схемы DepartmentCreate"""

    def test_create_valid_department(self):
        """Тест создания валидного отдела"""
        data = {"name": "IT Department", "parent_id": 1}
        department = DepartmentCreate(**data)
        
        assert department.name == "IT Department"
        assert department.parent_id == 1

    def test_create_department_without_parent_id(self):
        """Тест создания отдела без родителя"""
        data = {"name": "Main Office"}
        department = DepartmentCreate(**data)
        
        assert department.name == "Main Office"
        assert department.parent_id is None

    def test_create_department_with_empty_name(self):
        """Тест создания отдела с пустым именем - должно выбросить ошибку"""
        with pytest.raises(ValidationError):
            DepartmentCreate(name="")

    def test_create_department_with_whitespace_name(self):
        """Тест создания отдела с именем из пробелов - должно выбросить ошибку"""
        with pytest.raises(ValidationError):
            DepartmentCreate(name="   ")

    def test_create_department_name_is_trimmed(self):
        """Тест что имя отдела обрезается от пробелов"""
        data = {"name": "  IT Department  "}
        department = DepartmentCreate(**data)
        
        assert department.name == "IT Department"


class TestDepartmentUpdate:
    """Тесты для схемы DepartmentUpdate"""

    def test_update_with_name_only(self):
        """Тест обновления только имени"""
        data = {"name": "New Name"}
        update = DepartmentUpdate(**data)
        
        assert update.name == "New Name"
        assert update.parent_id is None

    def test_update_with_none_values(self):
        """Тест обновления с None значениями"""
        data = {}
        update = DepartmentUpdate(**data)
        
        assert update.name is None
        assert update.parent_id is None

    def test_update_name_with_whitespace(self):
        """Тест что имя при обновлении обрезается"""
        data = {"name": "  Trimmed Name  "}
        update = DepartmentUpdate(**data)
        
        assert update.name == "Trimmed Name"


class TestEmployeeCreate:
    """Тесты для схемы EmployeeCreate"""

    def test_create_valid_employee(self):
        """Тест создания валидного сотрудника"""
        data = {
            "full_name": "John Doe",
            "position": "Manager",
            "hired_at": "2024-01-15"
        }
        employee = EmployeeCreate(**data)
        
        assert employee.full_name == "John Doe"
        assert employee.position == "Manager"
        assert str(employee.hired_at) == "2024-01-15"

    def test_create_employee_without_hired_at(self):
        """Тест создания сотрудника без даты найма"""
        data = {
            "full_name": "Jane Smith",
            "position": "Developer"
        }
        employee = EmployeeCreate(**data)
        
        assert employee.full_name == "Jane Smith"
        assert employee.position == "Developer"
        assert employee.hired_at is None

    def test_create_employee_with_empty_full_name(self):
        """Тест создания сотрудника с пустым именем - ошибка"""
        with pytest.raises(ValidationError):
            EmployeeCreate(full_name="", position="Manager")

    def test_create_employee_with_empty_position(self):
        """Тест создания сотрудника с пустой должностью - ошибка"""
        with pytest.raises(ValidationError):
            EmployeeCreate(full_name="John", position="")

    def test_create_employee_name_is_trimmed(self):
        """Тест что имя сотрудника обрезается"""
        data = {
            "full_name": "  John Doe  ",
            "position": "  Manager  "
        }
        employee = EmployeeCreate(**data)
        
        assert employee.full_name == "John Doe"
        assert employee.position == "Manager"


class TestDepartmentDeleteRequest:
    """Тесты для схемы DepartmentDeleteRequest"""

    def test_delete_with_cascade_mode(self):
        """Тест удаления в режиме cascade"""
        data = {"mode": ModeEnum.CASCADE}
        request = DepartmentDeleteRequest(**data)
        
        assert request.mode == ModeEnum.CASCADE
        assert request.reassign_to_department_id is None

    def test_delete_with_reassign_mode_without_target(self):
        """Тест реассайна без целевого отдела - ошибка"""
        with pytest.raises(ValidationError):
            DepartmentDeleteRequest(mode=ModeEnum.REASSIGN)

    def test_delete_with_reassign_mode_with_target(self):
        """Тест реассайна с целевым отделом"""
        data = {
            "mode": ModeEnum.REASSIGN,
            "reassign_to_department_id": 5
        }
        request = DepartmentDeleteRequest(**data)
        
        assert request.mode == ModeEnum.REASSIGN
        assert request.reassign_to_department_id == 5

    def test_default_mode_is_cascade(self):
        """Тест что режим по умолчанию - cascade"""
        request = DepartmentDeleteRequest()
        
        assert request.mode == ModeEnum.CASCADE
