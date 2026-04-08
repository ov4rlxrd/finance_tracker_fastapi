from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Operation

from app.core.enums import CurrencyEnum


class OperationsRepository:

    @classmethod
    async def create_operation(cls,
                               wallet_id: int,
                               operation_type: str,
                               amount: Decimal,
                               currency: CurrencyEnum,
                               session: AsyncSession,
                               category: str | None = None,
                               subcategory: str | None = None,
    ) -> Operation:
        operation = Operation(
            wallet_id = wallet_id,
            operation_type = operation_type,
            amount = amount,
            currency = currency,
            category = category,
            subcategory = subcategory
        )
        session.add(operation)
        await session.flush()
        return operation

    @classmethod
    async def get_operations_list(cls, session: AsyncSession,
                                  wallet_ids: list[int],
                                  date_from: datetime | None = None,
                                  date_to: datetime | None = None
    ) -> list[Operation]:
        query = select(Operation).where(Operation.wallet_id.in_(wallet_ids))
        if date_from:
            query = query.where(Operation.created_at >= date_from)
        if date_to:
            query = query.where(Operation.created_at <= date_to)
        result = await session.execute(query)
        return list(result.scalars().all())

