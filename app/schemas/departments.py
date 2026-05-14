from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from datetime import datetime, date
from enum import Enum


class DepartmentBase(BaseModel):
    """Базовая схема подразделения."""

    name: str = Field(
        description="Наименование подразделения",
        max_length=200,
        min_length=1,
    )


class DepartmentCreate(DepartmentBase):
    """Схема для создания нового подразделения."""

    parent_id: int | None = Field(
        None,
        description="ID родительского подразделения",
    )
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if v:
            return v
        raise ValueError("name cannot be empty or contain only spaces")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"name": "Магазин №1", "parent_id": 1}
        }
    )


class DepartmentUpdate(BaseModel):
    """Схема для изменения подразделения."""
    name: str | None = Field(
        None,
        min_length=1,
        max_length=200,
        description="Наименование подразделения",
    )
    parent_id: int | None = Field(
        None,
        description="ID родительского подразделения",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if v:
            return v
        raise ValueError("name cannot be empty or contain only spaces")
    
    @model_validator(mode="after")
    def validate_parent_id(self):
        if self.parent_id is not None and self.id == self.parent_id:
            raise ValueError("parent_id cannot be equal to id")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"name": "Магазин №1", "parent_id": 1}
        }
    )

class DepartmentResponse(DepartmentBase):
    """Схема подразделения для API ответа."""
    
    id: int = Field(description="ID подразделения")
    parent_id: int | None = Field(None, description="ID родительского подразделения")
    created_at: datetime = Field(description="Дата создания")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Склад",
                "parent_id": 2,
                "created_at": "2026-01-01T12:00:00Z",
            },
        },
    )


class EmployeeBase(BaseModel):
    """Базовая схема для сотрудника."""

    full_name: str = Field(
        description="Полное имя",
        max_length=200,
        min_length=1,
    )
    position: str = Field(
        description="Должность",
        max_length=200,
        min_length=1,
    )
    hired_at: date | None = Field(
        None,
        description="Дата приема на работу",
    )

    
class EmployeeCreate(EmployeeBase):
    """Схема для создания сотрудника."""

    @field_validator("full_name", "position")
    @classmethod
    def validate_nonempty_string(cls, v: str) -> str:
        v = v.strip()
        if v:
            return v
        raise ValueError("This field cannot be empty or contain only spaces")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Иванов Иван Иванович",
                "position": "Менеджер",
                "hired_at": "2026-01-01",
                "department_id": 1,
            },
        },
    )

class EmployeeUpdate(BaseModel):
    """Схема для изменения сотрудника."""

    department_id: int | None = Field(
        None,
        description="ID подразделения",
    )
    full_name: str | None = Field(
        None,
        description="Полное имя",
        max_length=200,
        min_length=1,
    )
    position: str | None = Field(
        None,
        description="Должность",
        max_length=200,
        min_length=1,
    )
    hired_at: date | None = Field(
        None,
        description="Дата приема на работу",
    )
    
    @field_validator("full_name", "position")
    @classmethod
    def validate_nonempty_string(cls, v: str) -> str:
        if v is None:
            return v
        v = v.strip()
        if v:
            return v
        raise ValueError("This field cannot be empty or contain only spaces")


    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Иванов Иван Иванович",
                "position": "Менеджер",
                "hired_at": "2026-01-01",
                "department_id": 1,
            },
        },
    )

class EmployeeResponse(EmployeeBase):
    """Схема сотрудника для API ответа."""

    id: int = Field(description="ID сотрудника")
    department_id: int = Field(description="ID подразделения")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "full_name": "Иванов Иван Иванович",
                "position": "Менеджер",
                "hired_at": "2026-01-01",
                "department_id": 1,
            },
        },
    )

class DepartmentTreeResponse(DepartmentResponse):
    """Схема дерева подразделения для API ответа."""
    children: list['DepartmentTreeResponse'] = Field(
        default_factory=list,
        description="Дочерние подразделения",
    )
    employees: list[EmployeeResponse] = Field(
        default_factory=list,
        description="Сотрудники",
    )
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Отдел 1",
                "parent_id": None,
                "children": [
                    {
                        "id": 2,
                        "name": "Отдел 2",
                        "parent_id": 1,
                    },
                ],
                "employees": [
                    {
                        "id": 1,
                        "full_name": "Иванов Иван Иванович",
                        "position": "Менеджер",
                        "hired_at": "2026-01-01",
                        "department_id": 1,
                    },
                ],
            },
        },
    )


class DepartmentTreeRequest(BaseModel):
    depth: int = Field(1, le=5, ge=1, description="Глубина вложенности")
    include_employees: bool = Field(True, description="Включая сотрудников")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "depth": 1,
                "include_employees": True,
            },
        },
    )

DepartmentTreeResponse.model_rebuild()

class ModeEnum(str, Enum):
    """Схема для выбора режима."""

    CASCADE = "cascade"
    REASSIGN = "reassign"

class DepartmentDeleteRequest(BaseModel):
    """Схема для удаления подразделения."""

    mode: ModeEnum = Field(ModeEnum.CASCADE, description="Режим удаления")
    reassign_to_department_id: int | None = Field(None, description="ID подразделения для переназначения")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "mode": "cascade",
                "reassign_to_department_id": 1,
            },
        },
    )

    @model_validator(mode='after')
    def validate_reassign_to_department_id(self):
        if self.mode == ModeEnum.REASSIGN and self.reassign_to_department_id is None:
            raise ValueError("reassign_to_department_id is required for reassign mode")