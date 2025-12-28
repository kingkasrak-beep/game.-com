import asyncio
from aiogram import Bot, Dispatcher
from config import API_TOKEN

from handlers import start, register, profile, shop, mercenary, income, owner

bot = Bot(API_TOKEN)
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(register.router)
dp.include_router(profile.router)
dp.include_router(shop.router)
dp.include_router(mercenary.router)
dp.include_router(income.router)
dp.include_router(owner.router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
