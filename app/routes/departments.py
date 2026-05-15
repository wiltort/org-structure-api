from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.departments import (
    DepartmentResponse,
    DepartmentTreeResponse,
    DepartmentCreate,
    EmployeeResponse,
    EmployeeCreate,
    DepartmentUpdate,
    ModeEnum,
)
from app.services.departaments import DepartmentService

router = APIRouter(prefix="/departments", tags=["departments"])


@router.post(
    "/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED
)
def create_department(department: DepartmentCreate, db: Session = Depends(get_db)):
    return DepartmentService.create(db, department)


@router.post(
    "/{department_id}/employees/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_employee(
    department_id: int, employee: EmployeeCreate, db: Session = Depends(get_db)
):
    return DepartmentService.add_employee(db, department_id, employee)


@router.get("/{department_id}", response_model=DepartmentTreeResponse)
def get_tree(
    department_id: int,
    depth: int = Query(1, le=5, ge=1, description="Глубина вложенности"),
    include_employees: bool = Query(True, description="Включая сотрудников"),
    db: Session = Depends(get_db),
):
    return DepartmentService.get_tree_and_employees(
        db, department_id, depth=depth, include_employees=include_employees
    )


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    department_id: int,
    mode: ModeEnum = Query(ModeEnum.CASCADE, description="Режим удаления"),
    reassign_to_department_id: int | None = Query(
        None, description="ID подразделения для переназначения"
    ),
    db: Session = Depends(get_db),
):
    return DepartmentService.delete(
        db,
        department_id,
        mode=mode,
        reassign_to_department_id=reassign_to_department_id,
    )


@router.patch("/{department_id}", status_code=status.HTTP_200_OK)
def update_department(
    department_id: int, department: DepartmentUpdate, db: Session = Depends(get_db)
) -> DepartmentResponse:
    return DepartmentService.update(db, department_id, department)
