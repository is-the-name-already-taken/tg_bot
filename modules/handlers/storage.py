import pathlib
from urllib.parse import urlparse
from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

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

@router.message(Command("fl"))
async def handle_fl(message: Message, command: CommandObject, admin_id: int, db):
    if not message.from_user.id == admin_id:
        return

    page, per_page = 1, 30
    files = db.all_file(page=page, per_page=per_page)
    
    if not files:
        return await message.answer("No files found.")

    response = "\n".join(f"{f.filename}" for f in files)
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="Prev", callback_data=f"fl_{page - 1}_{per_page}")
    )
    builder.add(
        types.InlineKeyboardButton(text="Next", callback_data=f"fl_{page + 1}_{per_page}")
    )
    await message.answer(f"Files:\n{response}", reply_markup=builder.as_markup())
    
@router.callback_query(lambda c: c.data.startswith("fl_"))
async def callback_fl_page(callback_query: types.CallbackQuery, admin_id: int, db):
    if not callback_query.from_user.id == admin_id:
        return

    _, page_str, per_page_str = callback_query.data.split("_")
    page, per_page = int(page_str), int(per_page_str)
    page = max(1, page)

    files = db.all_file(page=page, per_page=per_page)
    
    if not files:
        builder = InlineKeyboardBuilder()
        builder.add(
            types.InlineKeyboardButton(text="Go Back", callback_data=f"fl_{1}_{per_page}")
        )
        return await callback_query.message.edit_text("No files found.", reply_markup=builder.as_markup())

    response = "\n".join(f"{f.filename}" for f in files)
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="Prev", callback_data=f"fl_{page - 1}_{per_page}")
    )
    builder.add(
        types.InlineKeyboardButton(text="Next", callback_data=f"fl_{page + 1}_{per_page}")
    )
    
    try:
        await callback_query.message.edit_text(f"Files:\n{response}", reply_markup=builder.as_markup())
    except Exception as e:
        await callback_query.message.edit_text(f"Error: {e}")