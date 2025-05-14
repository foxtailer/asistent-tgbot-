from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def play_ikb(data:list[tuple]):
    ibtn1 = InlineKeyboardButton(text=f"{data[0][0]}",callback_data=f"{data[0][1]}")
    ibtn2 = InlineKeyboardButton(text=f"{data[1][0]}", callback_data=f"{data[1][1]}")
    ibtn3 = InlineKeyboardButton(text=f"{data[2][0]}",callback_data=f"{data[2][1]}")
    ibtn4 = InlineKeyboardButton(text=f"{data[3][0]}", callback_data=f"{data[3][1]}")
    
    return InlineKeyboardMarkup(inline_keyboard=[[ibtn1,ibtn2],[ibtn3,ibtn4]])
