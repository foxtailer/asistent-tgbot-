import random
import pandas as pd
import time

# TODO show sentense for some time Shuffle the words in sentense, show blank  spaces and comas. piple must bild virgin sentense.)

data = pd.read_csv(r"/home/aska/Documents/GIT/projects/telegram/eng_asistenf/consol_version/eng.csv")
# Words in dict separated by the days. sep = @,@
my_dict = list(zip(data.eng, data.rus, data.example))
amount_of_days = my_dict.count(('@','@','@'))


def day_selector(n, days=my_dict):
    """Return day(n) list of sets"""
    result = []
    flag = 0
    for item in days:
        if item == ('@', '@', '@') and flag == n - 1:
            return result
        elif item == ('@', '@', '@'):
            result.clear()
            flag += 1
            continue
        result.append(item)

def max_word_len(n, list_of_sets):
    """Return len of longest word in list"""
    max_len = 0
    for item in list_of_sets:
        if len(item[n]) > max_len:
            max_len = len(item[n])
    max_len += 1
    return max_len

def dict(list_of_sets):
    """Play dictant whith user"""
    score = 0
    temp = []
    misstakes = []
    x = len(list_of_sets)
    while x > 0:
        set = random.choice(list_of_sets)
        if set not in temp:
            temp.append(set)
            print(f">>> {set[1].title()} ... {set[2].replace(set[0], '*'*len(set[0])).capitalize()}")
        else:
            continue
        answer = input(": ")
        if answer ==  set[0]:
            score += 1
            print(' + ')
            print("")
        elif answer == "stop":
            break
        else:
            print(f' - ({set[0]})')
            print('Type full example.')
            while answer != set[2]:
                answer = input(": ")
            print("")
            misstakes.append(set[0])
        x -= 1

    print(f'{score}/{len(list_of_sets)} Misstakes {misstakes}')

    while len(misstakes) > 0:
        print('Repeat pls: ', misstakes.pop())
        for i in range(3):
            _ = input()

def three(list_of_sets):
    while True:
        temp = {}
        while len(temp) < 3:
            set = random.choice(list_of_sets)
            temp[set[0]] = set[1]

        word = random.choice(list(temp.keys()))

        for _ in temp.keys():
            print(_, ':', temp[_])

        print('')
        time.sleep(10)

        for i in range(10,0,-1):
            print(i)
            time.sleep(0.5)
        print("")

        answer = input(f"{temp[word]} : ")

        if answer == 'stop':
            break
        elif answer == word:
            print("")
            print("~_~ >> Nice! ++")
            print("")
        else:
            print("")
            print(f"~_~ >> :(  -- ({word})")
            print("")

def first(list_of_sets):
    random.shuffle(list_of_sets)

    for i in range(len(list_of_sets)):
        temp = list_of_sets.pop()
        shuffled = list(temp[0])
        random.shuffle(shuffled)
        shuffled = '_'.join(shuffled)
        print(temp[1], ':', shuffled, ' ', temp[2].replace(temp[0], '*'*len(temp[0])).capitalize() )
        while True:
            answer = input(':')
            if answer == temp[0]:
                print('+')
                print('')
                break
            elif answer == "stop":
                print('')
                print(f'{temp[0]}')
                break

def repeat(list_of_sets):
    random.shuffle(list_of_sets)
    print("~_~ >> Repeat the words pls.\n")
    while list_of_sets:
        print("")
        item = list_of_sets.pop()
        print(f"{item[0]} : {item[1]}")

        flag = 0
        while flag < 3:
            answer = input(": ")
            if answer == item[0]:
                flag += 1

        print(item[2])

def eng(list_of_sets):
    for item in list_of_sets:
        print(item[0])

def rus(list_of_sets):
    for item in list_of_sets:
        print(item[1])

def askrus():
    while True:
        item = random.choice(my_dict)
        if item == ("@","@","@"):
            continue
        print(item[1])
        while True:
            answer = input(": ")
            if answer == item[0]:
                print('+')
                print('')
                break
            print(f'({item[0]})')
            print('-')
            print('')
            break

def asksentense():
    while True:
        item = random.choice(my_dict)
        if item == ("@","@","@"):
            continue
        print(item[2].replace(item[0], "*" * len(item[0])))
        while True:
            answer = input(": ")
            if answer == item[0]:
                print('+')
                print('')
                break
            print(f'({item[0]})')
            print('-')
            print('')
            break

def mein():
    print('')
    while True:
        try:
            day = int(input(f'~_~ >> You have {amount_of_days} day-set in dictionary. Select day : '))
        except:
            day = int(input(f'~_~ >> Pls chose day betwen 0 and {amount_of_days} : '))
        if day >= 0 and day <= amount_of_days:
            selected_day = day_selector(day)
            break

    print(f'~_~ >> You select day {day}.')
    
    while True:
        user_say = input('~_~ >> What can i do for you? \n: ').lower().strip()
        print("")

        if user_say == "help":
            print(
                f"""
                Show - Print words from day {day}.
                Dict - Start a dictation of words from day {day}.
                Three - Start a 'Three game' using words from day {day}.
                """)
            
        elif user_say == "all":
            print("")
            for item in my_dict:
                print("  " + item[0].title(), ' '*(max_word_len(0, my_dict) - len(item[0])), '- ', item[1].title(), ' '*(max_word_len(1, my_dict) - len(item[1])), item[2].capitalize())
            print("")

        elif user_say == "show":
            print(f"~_~ >> Day {day} words:")
            print("")
            for item in selected_day:
                print("  " + item[0].title(), ' '*(max_word_len(0, selected_day) - len(item[0])), '- ', item[1].title(), ' '*(max_word_len(1, selected_day) - len(item[1])), item[2].capitalize())
            print("")

        elif user_say == "dict":
            print('')
            dict(selected_day)

        elif user_say == "dictall":
            print('')
            dict(my_dict)

        elif user_say == 'three':
            print('')
            three(selected_day)

        elif user_say == 'first':
            print('')
            first(selected_day)

        elif user_say == "repeat":
            print('')
            repeat(selected_day)

        elif user_say == "eng":
            print('')
            eng(selected_day)

        elif user_say == "rus":
            print('')
            rus(selected_day)

        elif user_say == "askrus":
            print('')
            askrus()

        elif user_say == "asksentense":
            print('')
            asksentense()

        elif user_say.isdigit():
            day = int(user_say)
            print(f'~_~ >> You select day {user_say}.')
            selected_day = day_selector(day)

        else:
            print('')
            print("~_~ >> Sory I dont anderstand, you :(")


if __name__ == "__main__":
    mein()







