import requests
import asyncio

from aiogram import Bot, types, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
# If need proxy on pythneweryvere
# from aiogram.client.session.aiohttp import AiohttpSession
# session = AiohttpSession(proxy='http://proxy.server:3128')

from src.handlers import routers_list
from src.services.bot_cmds_list import get_command_list
from src.config import TOKEN


bot = Bot(TOKEN,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML)) # session=session # for proxy
dp = Dispatcher()
dp.include_routers(*routers_list)


# Delete webhook -------------------------
# The URL for deleting the webhook
delete_webhook_url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"

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
