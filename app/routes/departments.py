from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.departments import (
    DepartmentResponse,
    DepartmentTreeResponse,
    DepartmentCreate,
    EmployeeResponse,
    EmployeeCreate,
    DepartmentTreeRequest,
    DepartmentDeleteRequest,
    DepartmentUpdate,
)
from app.services.departaments import DepartmentService

router = APIRouter(prefix="/departments", tags=["departments"])

@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(department: DepartmentCreate, db: Session = Depends(get_db)):
    return DepartmentService.create(db, department)

@router.post("/{department_id}/employees/", 
             response_model=EmployeeResponse, 
             status_code=status.HTTP_201_CREATED)
def add_employee(
    department_id: int,
    employee: EmployeeCreate,
    db: Session = Depends(get_db)
):
    return DepartmentService.add_employee(db, department_id, employee)

@router.get("/{department_id}", response_model=DepartmentTreeResponse)
def get_tree(
    department_id: int, 
    request: DepartmentTreeRequest, 
    db: Session = Depends(get_db)
):
    return DepartmentService.get_tree_and_employees(db, department_id, **request.model_dump())

@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(department_id: int, request: DepartmentDeleteRequest,
                      db: Session = Depends(get_db)):
    return DepartmentService.delete(db, department_id, **request.model_dump())


@router.patch("/{department_id}", status_code=status.HTTP_200_OK)
def update_department(department_id: int, department: DepartmentUpdate,
                      db: Session = Depends(get_db)) -> DepartmentResponse:
    return DepartmentService.update(db, department_id, department)