import logging
import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from modules.db import DB
from modules.handlers import pupils


async def on_startup(bot: Bot, admin_id: int):
    try:
        await bot.send_message(admin_id, "Loaded")
    except Exception as e:
        print(str(e))


async def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    TG_TOKEN = os.getenv("TG_TOKEN")
    TG_ADMIN_ID = int(os.getenv("TG_ADMIN_ID", "0"))
    POCKETBASE_URL = os.getenv("POCKETBASE_URL")
    POCKETBASE_ADMIN_EMAIL = os.getenv("POCKETBASE_ADMIN_EMAIL")
    POCKETBASE_ADMIN_PASSWORD = os.getenv("POCKETBASE_ADMIN_PASSWORD")
    POCKETBASE_COLLECTION = os.getenv("POCKETBASE_COLLECTION")

    db = DB(
        POCKETBASE_URL,
        POCKETBASE_ADMIN_EMAIL,
        POCKETBASE_ADMIN_PASSWORD,
        POCKETBASE_COLLECTION,
    )
    bot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()
    dp.startup.register(on_startup)
    dp.include_router(pupils.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, admin_id=TG_ADMIN_ID, db=db)


if __name__ == "__main__":
    asyncio.run(main())
