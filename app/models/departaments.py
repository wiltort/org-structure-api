from sqlalchemy import Integer, DateTime, Float, String, Index 
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base


class Department(Base):
    """Модель для хранения подразделений организации."""

    __tablename__ = "departments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("departments.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    parent: Mapped["Department | None"] = relationship("Department", remote_side=[id], back_populates="children")
    children: Mapped[list["Department"]] = relationship("Department", back_populates="parent")
    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="department")

    def __repr__(self) -> str:
        return f"<Departament(name='{self.name}', id={self.id}>"


class Employee(Base):
    """Модель для хранения сотрудников организации."""

    __tablename__ = "employees"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"))
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[str] = mapped_column(String(200), nullable=False)
    hired_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    department: Mapped["Department"] = relationship("Department", back_populates="employees")

    def __repr__(self) -> str:
        return f"<Employee(full_name='{self.full_name}', id={self.id}>"
