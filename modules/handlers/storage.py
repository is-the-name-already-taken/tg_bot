import pathlib
from urllib.parse import urlparse
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from pocketbase import PocketBase
from pocketbase.client import FileUpload

router = Router()

TEMP_DIR = pathlib.Path("tmp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)


@router.message(F.document)
async def handle_file_upload(message: Message, admin_id: int, db):
    if not message.from_user.id == admin_id:
        return

    file_id = message.document.file_id
    file_name = message.document.file_name

    file_path = TEMP_DIR / file_name

    try:
        file = await message.bot.get_file(file_id)
        await message.bot.download_file(file.file_path, destination=file_path)

        result = db.upload_file(file_path, file_name)

        if result:
            await message.reply(f"✅ uploaded. (ID: {result.id})")
        else:
            await message.reply("❌ upload failed.")

    except Exception as e:
        await message.reply(f"⚠️ error: {e}")

    finally:
        file_path.unlink(missing_ok=True)


@router.message(Command("fu"))
async def handle_fu(message: Message, command: CommandObject, admin_id: int, db):
    if not message.from_user.id == admin_id:
        return

    if not command.args:
        return await message.answer("Usage: /fu <file_name>")

    file_name = command.args.strip()
    url = db.get_file_url(file_name)

    if url:
        parsed = urlparse(url)
        new_path = parsed.path.replace("/api/files/", "/", 1)
        new_domain = "files.y0rfa1se.top"
        url = f"https://{new_domain}{new_path}"
        
        await message.answer(f"File URL: {url}")
    else:
        await message.answer("File not found.")
