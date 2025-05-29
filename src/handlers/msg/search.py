from aiogram import types, Router

from src.services.db_functions import search
from src.config import DB_PATH


search_router = Router()


@search_router.message()
async def msg_search(msg: types.Message):
    word = await search(msg.from_user.first_name,
                        msg.text.lower().strip(),
                        db_path=DB_PATH
    )
    
    if word:
        await msg.answer(f"<code>{word.eng.capitalize()}</code>: {word.rus} <pre>{word.example.capitalize()}</pre>\n")
    else:
        await msg.answer(msg.text)
    
    msg.delete()