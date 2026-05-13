from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.departments import Department, Employee
from datetime import datetime
from app.core.config import settings


class DepartamentRepository:
    """Репозиторий для работы с моделями Departament."""

    @staticmethod
    def get_by_id(
        db: Session, department_id: int
    ) -> Department | None:
        result = db.execute(
            select(Department).where(Department.id == department_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    def create(
        db: Session,
        name: str,
        parent_id: int | None = None,
    ) -> Department:
        department = Department(name=name, parent_id=parent_id)
        db.add(department)
        db.commit()
        return department
    
    @staticmethod
    def get_tree_and_employees(
        db: Session,
        department_id: int,
        depth: int = 1,
    ) -> list[Department]:
        return db.execute(
            select(Department).where(Department.parent_id == department_id)
        )

    @staticmethod
    async def get_last_price_record(
        db: AsyncSession, ticker: str
    ) -> models.PriceRecord | None:
        stmt = select(models.PriceRecord)
        if ticker:
            stmt = stmt.where(models.PriceRecord.ticker == ticker)
        stmt = stmt.order_by(models.PriceRecord.timestamp.desc()).limit(1)
        return (await db.execute(stmt)).scalar_one_or_none()

    @staticmethod
    async def create_price_record(
        db: AsyncSession, price_record_data: dict
    ) -> models.PriceRecord:
        db_price_record = models.PriceRecord(**price_record_data)
        db.add(db_price_record)
        await db.commit()
        await db.refresh(db_price_record)
        return db_price_record

    @staticmethod
    async def get_price_records(
        db: AsyncSession,
        ticker: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        desc: bool = False,
        pagination: bool = True,
        page: int = 1,
        page_size: int = settings.page_size,
    ) -> list[models.PriceRecord]:
        """Получение записей цен"""
        stmt = select(models.PriceRecord)

        if ticker:
            stmt = stmt.where(models.PriceRecord.ticker == ticker)

        if start_date:
            stmt = stmt.where(models.PriceRecord.timestamp >= start_date)

        if end_date:
            stmt = stmt.where(models.PriceRecord.timestamp <= end_date)
        if desc:
            stmt = stmt.order_by(models.PriceRecord.timestamp.desc())
        else:
            stmt = stmt.order_by(models.PriceRecord.timestamp)

        # Пагинация
        if pagination:
            offset = (page - 1) * page_size
            stmt = stmt.offset(offset).limit(page_size)

        return (await db.execute(stmt)).scalars().all()

    @staticmethod
    async def get_total_and_pages(
        db: AsyncSession,
        ticker: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page_size: int = settings.page_size,
        **kwargs,
    ) -> dict[str, int]:
        """Получение общего количества записей и общего количества страниц"""
        stmt = select(func.count(models.PriceRecord.id))
        if ticker:
            stmt = stmt.where(models.PriceRecord.ticker == ticker)
        if start_date:
            stmt = stmt.where(models.PriceRecord.timestamp >= start_date)
        if end_date:
            stmt = stmt.where(models.PriceRecord.timestamp <= end_date)
        result = await db.execute(stmt)
        total = result.scalar() or 0
        pages = total // page_size + (1 if total % page_size > 0 else 0)
        return {"total": total, "pages": pages}
