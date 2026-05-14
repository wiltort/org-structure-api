import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from datetime import datetime
from app.services.departaments import DepartmentService
from app.schemas.departments import DepartmentCreate, DepartmentUpdate, ModeEnum, EmployeeCreate


class TestDepartmentServiceCreate:
    """Тесты для метода создания отдела"""

    @patch("app.services.departaments.DepartmentRepository")
    def test_create_department_success(self, mock_repo):
        """Тест успешного создания отдела"""
        from datetime import datetime
        
        mock_db = Mock()
        mock_department = MagicMock()
        mock_department.id = 1
        mock_department.name = "IT Department"
        mock_department.parent_id = None
        mock_department.created_at = datetime.now()
        
        mock_repo.get_by_id.return_value = None  # parent не проверяем (None)
        mock_repo.find_one_or_none.return_value = None  # существующего нет
        mock_repo.create.return_value = mock_department

        result = DepartmentService.create(mock_db, DepartmentCreate(name="IT Department"))

        assert result.name == "IT Department"
        assert result.id == 1
        mock_repo.create.assert_called_once()

    @patch("app.services.departaments.DepartmentRepository")
    def test_create_department_with_invalid_parent(self, mock_repo):
        """Тест создания отдела с несуществующим родителем"""
        mock_db = Mock()
        mock_repo.get_by_id.return_value = None  # родитель не найден

        with pytest.raises(HTTPException) as exc_info:
            DepartmentService.create(
                mock_db,
                DepartmentCreate(name="IT Department", parent_id=999)
            )

        assert exc_info.value.status_code == 404
        assert "Parent department not found" in exc_info.value.detail

    @patch("app.services.departaments.DepartmentRepository")
    def test_create_department_duplicate(self, mock_repo):
        """Тест создания дубликата отдела"""
        mock_db = Mock()
        mock_existing = Mock(id=1)
        mock_repo.get_by_id.return_value = Mock()  # родитель существует
        mock_repo.find_one_or_none.return_value = mock_existing  # такой уже есть

        with pytest.raises(HTTPException) as exc_info:
            DepartmentService.create(
                mock_db,
                DepartmentCreate(name="IT Department", parent_id=1)
            )

        assert exc_info.value.status_code == 409
        assert "already exists" in exc_info.value.detail


class TestDepartmentServiceGetById:
    """Тесты для метода получения отдела по ID"""

    @patch("app.services.departaments.DepartmentRepository")
    def test_get_existing_department(self, mock_repo):
        """Тест получения существующего отдела"""
        from datetime import datetime
        
        mock_db = Mock()
        mock_department = MagicMock()
        mock_department.id = 1
        mock_department.name = "IT Department"
        mock_department.parent_id = None
        mock_department.created_at = datetime.now()
        
        mock_repo.get_by_id.return_value = mock_department

        result = DepartmentService.get_by_id(mock_db, 1)

        assert result is not None
        assert result.id == 1
        assert result.name == "IT Department"

    @patch("app.services.departaments.DepartmentRepository")
    def test_get_nonexistent_department(self, mock_repo):
        """Тест получения несуществующего отдела"""
        mock_db = Mock()
        mock_repo.get_by_id.return_value = None

        result = DepartmentService.get_by_id(mock_db, 999)

        assert result is None


class TestDepartmentServiceAddEmployee:
    """Тесты для метода добавления сотрудника"""

    @patch("app.services.departaments.DepartmentRepository")
    def test_add_employee_success(self, mock_repo):
        """Тест успешного добавления сотрудника"""
        from datetime import date, datetime
        
        mock_db = Mock()
        mock_department = MagicMock()
        mock_department.id = 1
        
        mock_employee = MagicMock()
        mock_employee.id = 1
        mock_employee.full_name = "John Doe"
        mock_employee.position = "Manager"
        mock_employee.department_id = 1
        mock_employee.hired_at = date(2024, 1, 15)
        mock_employee.created_at = datetime.now()
        
        mock_repo.get_by_id.return_value = mock_department
        mock_repo.add_employee.return_value = mock_employee

        result = DepartmentService.add_employee(
            mock_db,
            1,
            EmployeeCreate(full_name="John Doe", position="Manager")
        )

        assert result.full_name == "John Doe"
        assert result.position == "Manager"
        mock_repo.add_employee.assert_called_once()

    @patch("app.services.departaments.DepartmentRepository")
    def test_add_employee_to_nonexistent_department(self, mock_repo):
        """Тест добавления сотрудника в несуществующий отдел"""
        mock_db = Mock()
        mock_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            DepartmentService.add_employee(
                mock_db, 
                999,
                {"full_name": "John Doe", "position": "Manager"}
            )

        assert exc_info.value.status_code == 404
        assert "Department not found" in exc_info.value.detail


class TestDepartmentServiceUpdate:
    """Тесты для метода обновления отдела"""

    @patch("app.services.departaments.DepartmentRepository")
    def test_update_department_success(self, mock_repo):
        """Тест успешного обновления отдела"""
        mock_db = Mock()
        mock_department = MagicMock()
        mock_department.id = 1
        mock_department.name = "Old Name"
        mock_department.parent_id = None
        
        mock_repo.get_by_id.return_value = mock_department
        mock_repo.find_one_or_none.return_value = None  # дубликат не найден
        mock_repo.update.return_value = mock_department

        result = DepartmentService.update(
            mock_db,
            1,
            DepartmentUpdate(name="New Name")
        )

        assert result.name == "Old Name"  # Возвращается обновленный отдел (mock)
        mock_repo.update.assert_called_once()

    @patch("app.services.departaments.DepartmentRepository")
    def test_update_nonexistent_department(self, mock_repo):
        """Тест обновления несуществующего отдела"""
        mock_db = Mock()
        mock_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            DepartmentService.update(
                mock_db,
                999,
                DepartmentUpdate(name="New Name")
            )

        assert exc_info.value.status_code == 404
        assert "Department not found" in exc_info.value.detail


class TestDepartmentServiceDelete:
    """Тесты для метода удаления отдела"""

    @patch("app.services.departaments.DepartmentRepository")
    def test_delete_department_success(self, mock_repo):
        """Тест успешного удаления отдела"""
        mock_db = Mock()
        mock_department = Mock(id=1)
        mock_repo.get_by_id.return_value = mock_department

        DepartmentService.delete(mock_db, 1, ModeEnum.CASCADE)

        mock_repo.delete.assert_called_once()

    @patch("app.services.departaments.DepartmentRepository")
    def test_delete_nonexistent_department(self, mock_repo):
        """Тест удаления несуществующего отдела"""
        mock_db = Mock()
        mock_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            DepartmentService.delete(mock_db, 999, ModeEnum.CASCADE)

        assert exc_info.value.status_code == 404
        assert "Department not found" in exc_info.value.detail

    @patch("app.services.departaments.DepartmentRepository")
    def test_reassign_requires_target_department(self, mock_repo):
        """Тест что reassign требует целевой отдел"""
        mock_db = Mock()
        mock_repo.get_by_id.return_value = Mock(id=1)

        with pytest.raises(HTTPException) as exc_info:
            DepartmentService.delete(mock_db, 1, ModeEnum.REASSIGN)

        assert exc_info.value.status_code == 400
        assert "reassign_to_department_id is required" in exc_info.value.detail

    @patch("app.services.departaments.DepartmentRepository")
    def test_reassign_cannot_be_to_same_department(self, mock_repo):
        """Тест что нельзя переназначить на тот же отдел"""
        mock_db = Mock()
        mock_repo.get_by_id.return_value = Mock(id=1)

        with pytest.raises(HTTPException) as exc_info:
            DepartmentService.delete(
                mock_db, 
                1, 
                ModeEnum.REASSIGN,
                reassign_to_department_id=1
            )

        assert exc_info.value.status_code == 400
        assert "cannot be equal to department_id" in exc_info.value.detail
