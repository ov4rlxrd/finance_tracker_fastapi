import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.operation_service import get_operations_list_service


async def get_operations_analysis(user_id:int, session: AsyncSession, wallet_id: int |None = None,):
    if wallet_id:
        operations = await get_operations_list_service(
            user_id, session, wallet_id
        )
    else:
        operations = await get_operations_list_service(
            user_id, session
        )
    prompt = f"""
    Analyze the following financial operations and provide insights on spending patterns, potential savings, and recommendations for better financial management.
    
    Here operations: {operations}
    
    """

    response = await ai_request(prompt)
    return {"analysis": response}

async def ai_request(prompt: str) -> str:
    timeout = aiohttp.ClientTimeout(total=300)
    async with aiohttp.ClientSession(timeout=timeout) as client:
        async with client.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3-vl:8b",
                "prompt": prompt,
                "stream": False
            },
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data["response"]
