import os
from dotenv import load_dotenv
from aiohttp import web

from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.handlers import routers_list
from src.services.bot_cmds_list import get_command_list


load_dotenv()

API_TOKEN = os.getenv('TOKEN')
WEBHOOK_HOST = "https://bfe4-213-231-21-243.ngrok-free.app"  # Your ngrok public URL
WEBHOOK_PATH = "/webhook/"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(API_TOKEN,
          default=DefaultBotProperties(
              parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_routers(*routers_list)


# Handle incoming updates
async def handle_webhook(request):
    update = Update(**await request.json())
    await dp.feed_webhook_update(bot, update)
    return web.Response(text="OK")


# aiohttp setup
app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle_webhook)


async def on_startup(app):
    # Set the webhook when the aiohttp app starts
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    await bot.set_my_commands(commands=get_command_list('RU'), scope=types.BotCommandScopeAllPrivateChats())

async def on_shutdown(app):
    # Remove the webhook on aiohttp shutdown
    await bot.delete_webhook()


app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)


if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8001)
