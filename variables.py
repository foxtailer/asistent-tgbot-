"""
select_day - Select day you want to practice
test - Test throw selected day
test10 - Test with random 10 words
sentense - Guess wond in sentense based on your words
shaffle - Try to guess shaffled word
get_example - Give 5 sentence with word
show - Show dictionary
add - Add new words in dict
del - Deleate word/words
start - Start bot
help - Help/Info
"""

HELP_MESSAGE = """
Bot can hold your dictionary and play UserState with you based on words in this dictionary.

<code>1) Cat:Кот (My beautiful cat.).\n2) Dog:Собака (Wery big dog.).</code>

(Слово,Перевод,Пример)
...like this:)

Команда:
<code>/add</code> <i>Help,Помощь,I need help.</i>
Добавит в словарь новую строку:
<code>3) Help:Помощь (I need help.)</code>

Запятых в предложении примере быть<b>не</b> должно! Попытка добавить уже существующее в \
словаре слово, перезапишет его. Так можно исправить ошибку.

Команда:
<code>/del</code> <i>1,2,3</i>
Удаляет одно или несколько слов по номеру в списке.

Each game-command has 'w' atribute, mean 'write mode', If passed bot dont give
you a variants of right answer. You need write it by hand.
"""