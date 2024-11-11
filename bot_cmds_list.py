from aiogram.types import BotCommand


private = [
    BotCommand(command='select_day', description='Select day you want to practice'),
    BotCommand(command='test', description='Test throw selected day'),
    BotCommand(command='test10', description='Test with random 10 words'),
    #BotCommand(command='sentense', description='Guess word in sentense based on your words'),
    BotCommand(command='shuffle', description='Try to guess shaffled word'),
    #BotCommand(command='get_example', description='Give 5 sentence with word'),
    BotCommand(command='show', description='Show dictionary'),
    BotCommand(command='add', description='Add new words in dict'),
    BotCommand(command='del', description='Deleate word/words'),
    BotCommand(command='start', description='Start bot'),
    BotCommand(command='help', description='Help/Info'),
]
