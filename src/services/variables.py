HELP_MESSAGE_ENG = """
📖 
The bot can store your dictionary and play games with you using the words in this dictionary.\


The dictionary looks like this:\

<code>
1) Cat:Кот (My beautiful cat.)
2) Dog:Собака (Very big dog.)
...
</code>\

(Word, Translation, Example)

You can interact with the bot using the commands menu (≡ Menu) in the bottom-left corner of \
your screen or by typing commands in the chat, like:

<code>/add Help,Помощь,I need help.</code>

In this case, the command will add a new word, "Help," to the dictionary.  
*Note: When adding a word, translation, and example, separate them with a comma. This means \
you cannot use commas in the example sentence.

Each command behaves differently and may require specific arguments. To learn how a command works, \
type 'help' as a parameter for the command.  
*A parameter is a word or letter that comes after a command.

<code>/test help</code>

This will provide a description of the command.

To change bot languege enter <code>/start</code> egein.

I hope this bot helps you enjoy your learning journey! 😊\
"""

HELP_MESSAGE_RUS = """
📖 
Бот может хранить ваш словарь и играть с вами в игры, используя слова из этого словаря.

Словарь выглядит так:

<code>
1) Cat:Кот (My beautiful cat.)
2) Dog:Собака (Very big dog.)
...
</code>

(Слово, Перевод, Пример)

Вы можете взаимодействовать с ботом через меню команд (≡ Menu) в левом нижнем углу экрана\
или вводя команды в чат, например:

<code>/add Help,Помощь,I need help.</code>

В этом случае команда добавит в словарь новое слово "Help".  
*Примечание: При добавлении слова, перевода и примера они разделяются запятой. Это означает,\
что в предложении-примере нельзя использовать запятые.

Каждая команда работает по-разному и может требовать определённых аргументов. Чтобы узнать,\
как работает команда, введите 'help' в качестве параметра к команде.  
*Параметр — это слово или буква, которые идут после команды.

<code>/test help</code>

Это даст вам описание команды.

Надеюсь, этот бот поможет вам наслаждаться вашим путешествием в обучении! 😊
"""

COMANDS = (
    'help',
    'test',
    'shuffle',
    'show',
    'add',
    'del',
    'start',
    'sentense',
    'get_example',
)

COMAND_TITLES_ENG = (
    'Help/Info',
    'Test throw selected day',
    'Try to guess shuffled word',
    'Show dictionary',
    'Add new words in dict',
    'Delete word/words',
    'Start bot',
)

COMAND_TITLES_RU = (
    'Помощь/Информация',
    'Тест по выбранному дню',
    'Попробуйте угадать перемешанное слово',
    'Показать словарь',
    'Добавить новые слова в словарь',
    'Удалить слово/слова',
    'Запустить бота',
)