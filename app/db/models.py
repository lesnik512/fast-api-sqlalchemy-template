import logging
import re
from typing import Any, List, NoReturn, Optional, Type, TypeVar

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base
from app.db.deps import get_db
from app.db.exceptions import DatabaseValidationError
from app.utils.datetime import utcnow


logger = logging.getLogger(__name__)


# https://mypy.readthedocs.io/en/latest/generics.html#generic-methods-and-generic-self
T = TypeVar("T", bound="BaseModel")


class BaseModel(Base):
    __abstract__ = True

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    created_at = sa.Column(
        sa.DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    @classmethod
    def _raise_validation_exception(
        cls, e: IntegrityError, object_id: Optional[int] = None
    ) -> NoReturn:
        info = e.orig.args
        match: List[str] = re.findall(
            r"Key \((.*)\)=\(.*\) already exists|$", info[0]
        )
        if match:
            raise DatabaseValidationError(
                f"Unique constraint violated for {cls.__name__}",
                field=match[0],
                object_id=object_id,
            ) from e
        raise DatabaseValidationError(
            f"Integrity error for {cls.__name__}", object_id=object_id
        ) from e

    @classmethod
    async def all(cls: Type[T]) -> List[T]:
        db: AsyncSession = get_db()
        db_execute = await db.execute(sa.select(cls))
        return db_execute.scalars().all()

    @classmethod
    async def filter(cls: Type[T], conditions: List[Any]) -> List[T]:
        db: AsyncSession = get_db()
        query = sa.select(cls)
        db_execute = await db.execute(query.where(sa.and_(*conditions)))
        return db_execute.scalars().all()

    @classmethod
    async def get_by_id(cls: Type[T], object_id: int) -> T:
        db: AsyncSession = get_db()
        return await db.get(cls, object_id)

    @classmethod
    async def bulk_create(cls: Type[T], objects: List[T]) -> List[T]:
        db: AsyncSession = get_db()
        try:
            db.add_all(objects)
            await db.flush()
        except IntegrityError as e:
            cls._raise_validation_exception(e)
        return objects

    @classmethod
    async def bulk_update(cls: Type[T], objects: List[T]) -> List[T]:
        db: AsyncSession = get_db()
        try:
            ids = [x.id for x in objects if x.id]
            await db.execute(sa.select(cls).where(cls.id.in_(ids)))
            for item in objects:
                try:
                    await db.merge(item)
                except IntegrityError as e:
                    cls._raise_validation_exception(e, item.id)
            await db.flush()
        except IntegrityError as e:
            cls._raise_validation_exception(e)
        return objects

    async def save(self, commit: bool = False) -> None:
        db: AsyncSession = get_db()
        db.add(self)
        try:
            await db.flush()
        except IntegrityError as e:
            self._raise_validation_exception(e)
        if commit:
            await db.commit()

    async def update(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)
        await self.save()
