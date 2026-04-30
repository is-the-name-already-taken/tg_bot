from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.message(Command("ha"))
async def handle_ha(message: Message, command: CommandObject, admin_id: int, db):
    if not message.from_user.id == admin_id:
        return
    
    if not command.args:
        return await message.answer("Usage: /ha <name>")

    parsed = [line for line in command.args.split("\n") if line]
    for name in parsed:
        db.upsert(name, is_good=True)
    return await message.answer("Added")


@router.message(Command("hb"))
async def handle_hb(message: Message, command: CommandObject, admin_id: int, db):
    if not message.from_user.id == admin_id:
        return
    
    if not command.args:
        return await message.answer("Usage: /hb <name>")

    parsed = [line for line in command.args.split("\n") if line]
    for name in parsed:
        db.upsert(name, is_good=False)
    return await message.answer("Added")


@router.message(Command("hr"))
async def handle_hr(message: Message, command: CommandObject, admin_id: int, db):
    if not message.from_user.id == admin_id:
        return
    
    n = int(command.args.strip()) if command.args else 1
    samples = db.sample(n)
    if not samples:
        return await message.answer("No data available.")

    response = "\n".join(f"{s.content}: {s.used}" for s in samples)

    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="Refresh", callback_data=f"hr_refresh_{n}")
    )
    await message.answer(response, reply_markup=builder.as_markup())


@router.message(Command("hd"))
async def handle_hd(message: Message, command: CommandObject, admin_id: int, db):
    if not message.from_user.id == admin_id:
        return
    
    if not command.args:
        return await message.answer("Usage: /hd <name>")

    parsed = [line for line in command.args.split("\n") if line]
    for name in parsed:
        db.delete(name)
    return await message.answer("Deleted")


@router.message(Command("hs"))
async def handle_hs(message: Message, command: CommandObject, admin_id: int, db):
    if not message.from_user.id == admin_id:
        return
    
    if not command.args:
        return await message.answer("Usage: /hs <name>")

    name = command.args.strip()
    results = []
    matches = db.like(name)
    results.append(f"Matches for '{name}':")
    if matches:
        results.extend(f"{m.content}: {m.used}" for m in matches)
    else:
        results.append("No matches found.")
    return await message.answer("\n".join(results))


@router.message(Command("hl"))
async def handle_hl(message: Message, command: CommandObject, admin_id: int, db):
    if not message.from_user.id == admin_id:
        return
    
    page, per_page = 1, 30
    pupils_list = db.all(page, per_page)
    
    if not pupils_list:
        return await message.answer("No data available.")
    
    response = "\n".join(f"{p.content}: {p.used}" for p in pupils_list)
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="Prev", callback_data=f"hl_{page - 1}_{per_page}")
    )
    builder.add(
        types.InlineKeyboardButton(text="Next", callback_data=f"hl_{page + 1}_{per_page}")
    )
    await message.answer(response, reply_markup=builder.as_markup())

@router.callback_query(lambda c: c.data.startswith("hr_refresh_"))
async def callback_hr_refresh(callback_query: types.CallbackQuery, admin_id: int, db):
    if not callback_query.from_user.id == admin_id:
        return
    
    n = int(callback_query.data.split("_")[-1])
    samples = db.sample(n)
    if not samples:
        return await callback_query.message.edit_text("No data available.")

    response = "\n".join(f"{s.content}: {s.used}" for s in samples)
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="Refresh", callback_data=f"hr_refresh_{n}")
    )
    
    try:
        await callback_query.message.edit_text(response, reply_markup=builder.as_markup())
    except Exception as e:
        print(f"Error occurred while editing message: {e}")

@router.callback_query(lambda c: c.data.startswith("hl_"))
async def callback_hl(callback_query: types.CallbackQuery, admin_id: int, db):
    if not callback_query.from_user.id == admin_id:
        return
    
    _, page, per_page = callback_query.data.split("_")
    page, per_page = int(page), int(per_page)
    page = max(1, page)

    pupils_list = db.all(page, per_page)

    if not pupils_list:
        builder = InlineKeyboardBuilder()
        builder.add(
            types.InlineKeyboardButton(text="Go Back", callback_data=f"hl_{1}_{per_page}")
        )
        return await callback_query.message.edit_text("No data available.", reply_markup=builder.as_markup())
    
    response = "\n".join(f"{p.content}: {p.used}" for p in pupils_list)
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="Prev", callback_data=f"hl_{page - 1}_{per_page}")
    )
    builder.add(
        types.InlineKeyboardButton(text="Next", callback_data=f"hl_{page + 1}_{per_page}")
    )
    
    try:
        await callback_query.message.edit_text(response, reply_markup=builder.as_markup())
    except Exception as e:
        print(f"Error occurred while editing message: {e}")