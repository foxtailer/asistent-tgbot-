from collections import namedtuple
from aiogram.types import BotCommand

from src.services import variables


def get_command_list(bot_lang):
    title_lang = 'COMAND_TITLES_' + bot_lang
    comand_titles = getattr(variables, title_lang)

    comand_list = zip(variables.COMANDS, comand_titles)
    Comand = namedtuple('Comand', ['name', 'title'])
    comand_list = [Comand(name, title) for name, title in comand_list]

    bot_cmnds = [BotCommand(command=comand.name, description=comand.title) for comand in comand_list]

    return bot_cmnds
