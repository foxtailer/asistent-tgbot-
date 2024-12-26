import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, types, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.handlers import routers_list
from src.services.bot_cmds_list import get_command_list


load_dotenv()
bot_token = os.getenv('TOKEN')

bot = Bot(bot_token,
          default=DefaultBotProperties(
              parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_routers(*routers_list)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=get_command_list('RU'), scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, 
                           allowed_updates=["message", "edited_message", "callback_query", "inline_query"],
                           polling_timeout=20)


if __name__ == '__main__':
    asyncio.run(main())
