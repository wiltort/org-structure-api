from sqlalchemy import Date, ForeignKey, Integer, DateTime, String, Index 
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import date, datetime
from app.core.database import Base


class Department(Base):
    """Модель для хранения подразделений организации."""

    __tablename__ = "departments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("departments.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    parent: Mapped["Department | None"] = relationship("Department", remote_side=[id], back_populates="children")
    children: Mapped[list["Department"]] = relationship(
        "Department",
        back_populates="parent",
        cascade="all, delete_orphan"
    )
    employees: Mapped[list["Employee"]] = relationship(
        "Employee",
        back_populates="department",
        cascade="all, delete_orphan"
    )

    __table_args__ = (
        Index("ix_departments_parent_id_name", "parent_id", "name", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Departament(name='{self.name}', id={self.id}>"

class Employee(Base):
    """Модель для хранения сотрудников организации."""

    __tablename__ = "employees"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"), index=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[str] = mapped_column(String(200), nullable=False)
    hired_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    department: Mapped["Department"] = relationship("Department", back_populates="employees")

    def __repr__(self) -> str:
        return f"<Employee(full_name='{self.full_name}', id={self.id}>"
