from decimal import Decimal

import aiohttp

from app.core.enums import CurrencyEnum
from app.exceptions.exhange import RateException


async def get_exchange_rate(base: CurrencyEnum, target: CurrencyEnum) -> Decimal:

    url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base}.json"

    timeout = aiohttp.ClientTimeout(total=10)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                base_map = data.get(base, {})
                rate = base_map.get(target)
        if rate is not None and isinstance(rate, (int, float)):
            return Decimal(rate)
        raise RateException()
    except RateException as e:
        raise e
