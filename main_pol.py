import requests
import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, types, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.handlers import routers_list
from src.services.bot_cmds_list import get_command_list
# If need proxy on pythneweryvere
# from aiogram.client.session.aiohttp import AiohttpSession


load_dotenv()
bot_token = os.getenv('TOKEN')
# session = AiohttpSession(proxy='http://proxy.server:3128')

bot = Bot(bot_token,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML)) # session=session # for proxy
dp = Dispatcher()
dp.include_routers(*routers_list)


# Delete webhook -------------------------
# The URL for deleting the webhook
delete_webhook_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"

# Make the POST request to delete the webhook
response = requests.post(delete_webhook_url)

# Check the response from Telegram
if response.status_code == 200:
    print("Webhook deleted successfully!")
else:
    print(f"Failed to delete webhook. Status code: {response.status_code}")
# ---------------------------------------

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=get_command_list('RU'), scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, 
                           allowed_updates=["message", "edited_message", "callback_query", "inline_query"],
                           polling_timeout=20)


if __name__ == '__main__':
    asyncio.run(main())
