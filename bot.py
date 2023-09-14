import sys
import traceback

import time, random
default_print = print
def print(*args, **kwargs):
    default_print(*args, **kwargs)
    while True:
        try:
            f = open('/home/andrew/var/log/bot_log.txt', 'a+')
            f.write(str(args) + '\n')
            f.close()
            break
        except:
            time.sleep(random.random())


from telebot import types
import telebot

import os
from dotenv import load_dotenv
load_dotenv()
bot_token = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(token=bot_token)

from main import execute_program

# We use database to store the macros
# import sqlite3
# conn = sqlite3.connect('macros.db', check_same_thread=False)
# c = conn.cursor()
import pymongo
from pymongo import MongoClient
client = MongoClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('MONGODB_NAME')]

# # Create table of macros if it doesn't exist
# c.execute('''CREATE TABLE IF NOT EXISTS macros
#                 (trigger text, program text, chat_id text)''')
# conn.commit()
#

# Create table of selected languages if it doesn't exist
# c.execute('''CREATE TABLE IF NOT EXISTS languages
#                 (user_id text, language text)''')
# conn.commit()
#

programs = {}
# Get all macros from the database
# for row in c.execute('SELECT * FROM macros'):
#     programs[(row[0], row[2])] = row[1]
c = db["macros"]
for macro in c.find():
    print(f"macro: {macro}")
    time.sleep(1)
    try:
        programs[(macro['trigger'], macro['chat_id'])] = macro['program']
    except:
        pass
print(programs)

с = 1
c = 1

languages = {}
# # Get all languages from the database
# for row in c.execute('SELECT * FROM languages'):
#     languages[int(row[0])] = row[1]
c = db["languages"]
for user in c.find():
    print(f"user: {user}")
    try:
        languages[user['user_id']] = user['language']
    except:
        pass
print(languages)


@bot.message_handler(commands=['superbind'])
def bind(message):
    print(message.text)
    # This command must be replied to a message
    if message.reply_to_message:
        # Get the message that was replied to
        replied = message.reply_to_message
        # Get the text from that message
        program_code = replied.text
        # Save the program code to the dictionary
        programs[(message.text[11:], message.chat.id)] = program_code
        # Save the program code to the database
        # c.execute("INSERT INTO macros VALUES (?, ?, ?)", (message.text[11:], program_code, message.chat.id))
        # conn.commit()
        c = db["macros"]
        c.insert_one({'trigger': message.text[11:], 'program': program_code, 'chat_id': message.chat.id})
        bot.send_message(message.chat.id, "Macro created")
        print(programs)
    else:
        bot.send_message(message.chat.id, "Please reply to a message.")



@bot.message_handler(commands=['start'])
def start(message):
    hello_message = {
        'uk': f'Привіт, мене звуть {bot.get_me().first_name}.\nВикористовуйте /help щоб дізнатись більше про мої можливості',
        'ru': f'Привет, меня зовут {bot.get_me().first_name}.\nИспользуйте /help чтобы узнать больше о моих возможностях',
        'en': f'Hello, my name is {bot.get_me().first_name}.\nUse /help to learn more about my capabilities',
        'de': f'Hallo, mein Name ist {bot.get_me().first_name}.\nVerwenden Sie /help, um mehr über meine Fähigkeiten zu erfahren',
        'be': f'Прывітанне, мяне звалі {bot.get_me().first_name}.\nВыкарыстоўвайце /help каб даведацца больш пра мае магчымасці',
        'pl': f'Cześć, mam na imię {bot.get_me().first_name}.\nUżyj /help, aby dowiedzieć się więcej o moich możliwościach',
        'cs': f'Ahoj, jmenuji se {bot.get_me().first_name}.\nPoužijte /help, abyste se dozvěděli více o mých schopnostech',
    }
    if message.from_user.id not in languages:
        languages[message.from_user.id] = 'uk'
        # c.execute("INSERT INTO languages VALUES (?, ?)", (message.from_user.id, 'uk'))
        # conn.commit()
        c = db["languages"]
        c.insert_one({'user_id': message.from_user.id, 'language': 'uk'})
    bot.send_message(message.chat.id, hello_message[languages[message.from_user.id]], parse_mode='HTML')

@bot.message_handler(commands=['help'])
def help(message):
    macros_description = {
        'uk': """Використовуйте /superbind щоб створити макрос
Для створення макросів використовується проста мова програмування:
    - Кожна команда закінчується символом ";"
    - Доступні математичні операції: +, -, *, /, ^, |(цілочисельне ділення), %, sin, cos, tan, exp, log, sqrt, abs, ln
    - Доступні логічні операції: &lt;, &gt;, &lt;=, &gt;=, ==, !=, and, or
    - Можна створювати змінні: 
<code>a = 1;</code>
    - Можна використовувати змінні: 
<code>b = $a$ + 1;</code>
    - Можна використовувати значення з об'єкту message: 
<code>text = "$message.text$";</code>, <code>id = $message.from_user.id$;</code>, <code>name = "$message.from_user.first_name$";</code>, і т.д.
    - Можна використовувати if-else: 
<code>if ($message.from_user.id$ == 123){text = "Hello";} else{text = "Bye";}</code>
    - Можна створювати списки: 
<code>list = [1, 2, 3, 4]; a = list(0);</code>
    - Можна використовувати регулярні вирази: 
<code>text = re "g/([0-9]+) ([0-9]+)/(\\1 + \\2)/" "1 2";</code>
    - Використовуйте return щоб повернути значення: 
<code>return $a$;</code> (його відправить бот у відповідь на повідомлення, що затригерило макрос)

    - Відправьте команду /superbind TRIGGER-TEXT у відповідь на код макросу, щоб викликати макрос для кожного повідомлення, що містить TRIGGER-TEXT
    - Відправьте команду /superbind -r REGULAR у відповідь на код макросу, щоб викликати макрос для кожного повідомлення, що відповідає регулярному виразу REGULAR

Використовуйте /examples щоб побачити приклади макросів
Використовуйте /settings щоб змінити мову (або інші налаштування)
Використовуйте /superunbind щоб видалити макрос
Використовуйте /superbindings щоб побачити всі макроси в чаті
        """,
        'ru': """Используйте /superbind чтобы создать макрос
Для создания макросов используется простой язык программирования:
    - Каждая команда заканчивается символом ";"
    - Доступны математические операции: +, -, *, /, ^, |(целочисленное деление), %, sin, cos, tan, exp, log, sqrt, abs, ln
    - Доступны логические операции: &lt;, &gt;, &lt;=, &gt;=, ==, !=, and, or
    - Можно создавать переменные: 
<code>a = 1;</code>
    - Можно использовать переменные: 
<code>b = $a$ + 1;</code>
    - Можно использовать значения из объекта message: 
<code>text = "$message.text$";</code>, <code>id = $message.from_user.id$;</code>, <code>name = "$message.from_user.first_name$";</code>, и т.д.
    - Можно использовать if-else: 
<code>if ($message.from_user.id$ == 123){text = "Hello";} else{text = "Bye";}</code>
    - Можно создавать списки: 
<code>list = [1, 2, 3, 4]; a = list(0);</code>
    - Можно использовать регулярные выражения: 
<code>text = re "g/([0-9]+) ([0-9]+)/(\\1 + \\2)/" "1 2";</code>
    - Используйте return чтобы вернуть значение: 
<code>return $a$;</code> (его отправит бот в ответ на сообщение, которое вызвало макрос)

    - Отправьте команду /superbind TRIGGER-TEXT в ответ на код макроса, чтобы вызывать макрос для каждого сообщения, содержащего TRIGGER-TEXT
    - Отправьте команду /superbind -r REGULAR в ответ на код макроса, чтобы вызывать макрос для каждого сообщения, соответствующего регулярному выражению REGULAR

Используйте /examples чтобы увидеть примеры макросов
Используйте /settings чтобы изменить язык (или другие настройки)
Используйте /superunbind чтобы удалить макрос
Используйте /superbindings чтобы увидеть все макросы в чате
        """,
        'en': """Use /superbind to create a macro
A simple programming language is used to create macros:
    - Each command ends with the symbol ";"
    - Mathematical operations are available: +, -, *, /, ^, |(integer division), %, sin, cos, tan, exp, log, sqrt, abs, ln
    - Logical operations are available: &lt;, &gt;, &lt;=, &gt;=, ==, !=, and, or
    - You can create variables: 
<code>a = 1;</code>
    - You can use variables: 
<code>b = $a$ + 1;</code>
    - You can use values from the message object: 
<code>text = "$message.text$";</code>, <code>id = $message.from_user.id$;</code>, <code>name = "$message.from_user.first_name$";</code>, etc.
    - You can use if-else: 
<code>if ($message.from_user.id$ == 123){text = "Hello";} else{text = "Bye";}</code>
    - You can create lists: 
<code>list = [1, 2, 3, 4]; a = list(0);</code>
    - You can use regular expressions: 
<code>text = re "g/([0-9]+) ([0-9]+)/(\\1 + \\2)/" "1 2";</code>
    - Use return to return a value: 
<code>return $a$;</code> (the bot will send it in response to the message that triggered the macro)
    
    - Send the command /superbind TRIGGER-TEXT in response to the macro code to invoke the macro for each message containing TRIGGER-TEXT
    - Send the command /superbind -r REGULAR in response to the macro code to invoke the macro for each message that matches the regular expression REGULAR

Use /examples to see examples of macros
Use /settings to change the language (or other settings)
Use /superunbind to delete a macro
Use /superbindings to see all macros in the chat
        """,
        'de': """Verwenden Sie /superbind, um ein Makro zu erstellen
Es wird eine einfache Programmiersprache verwendet, um Makros zu erstellen:
    - Jeder Befehl endet mit dem Symbol ";"
    - Mathematische Operationen sind verfügbar: +, -, *, /, ^, |(ganzzahlige Division), %, sin, cos, tan, exp, log, sqrt, abs, ln
    - Logische Operationen sind verfügbar: &lt;, &gt;, &lt;=, &gt;=, ==, !=, and, or
    - Sie können Variablen erstellen: 
<code>a = 1;</code>
    - Sie können Variablen verwenden: 
<code>b = $a$ + 1;</code>
    - Sie können Werte aus dem Nachrichtenobjekt verwenden: 
<code>text = "$message.text$";</code>, <code>id = $message.from_user.id$;</code>, <code>name = "$message.from_user.first_name$";</code>, usw.
    - Sie können if-else verwenden: 
<code>if ($message.from_user.id$ == 123){text = "Hello";} else{text = "Bye";}</code>
    - Sie können Listen erstellen: 
<code>list = [1, 2, 3, 4]; a = list(0);</code>
    - Sie können reguläre Ausdrücke verwenden: 
<code>text = re "g/([0-9]+) ([0-9]+)/(\\1 + \\2)/" "1 2";</code>
    - Verwenden Sie return, um einen Wert zurückzugeben: 
<code>return $a$;</code> (der Bot wird ihn als Antwort auf die Nachricht senden, die das Makro ausgelöst hat)

    - Senden Sie den Befehl /superbind TRIGGER-TEXT als Antwort auf den Makrocode, um das Makro für jede Nachricht aufzurufen, die TRIGGER-TEXT enthält
    - Senden Sie den Befehl /superbind -r REGULAR als Antwort auf den Makrocode, um das Makro für jede Nachricht aufzurufen, die dem regulären Ausdruck REGULAR entspricht

Verwenden Sie /examples, um Beispiele für Makros zu sehen
Verwenden Sie /settings, um die Sprache (oder andere Einstellungen) zu ändern
Verwenden Sie /superunbind, um ein Makro zu löschen
Verwenden Sie /superbindings, um alle Makros im Chat anzuzeigen
        """,
        'be': """Выкарыстоўвайце /superbind каб стварыць макрос
Для стварэння макросаў выкарыстоўваецца просты мова праграмавання:
    - Кожная каманда заканчваецца сімвалам ";"
    - Даступны матэматычныя аперацыі: +, -, *, /, ^, |(цэлыя дзяленне), %, sin, cos, tan, exp, log, sqrt, abs, ln
    - Даступны лагічныя аперацыі: &lt;, &gt;, &lt;=, &gt;=, ==, !=, and, or
    - Можна ствараць зменныя: 
<code>a = 1;</code>
    - Можна выкарыстоўваць зменныя: 
<code>b = $a$ + 1;</code>
    - Можна выкарыстоўваць значэнні з аб'екта message: 
<code>text = "$message.text$";</code>, <code>id = $message.from_user.id$;</code>, <code>name = "$message.from_user.first_name$";</code>, і г.д.
    - Можна выкарыстоўваць if-else: 
<code>if ($message.from_user.id$ == 123){text = "Hello";} else{text = "Bye";}</code>
    - Можна ствараць спісы: 
<code>list = [1, 2, 3, 4]; a = list(0);</code>
    - Можна выкарыстоўваць рэгулярныя выразы: 
<code>text = re "g/([0-9]+) ([0-9]+)/(\\1 + \\2)/" "1 2";</code>
    - Выкарыстоўвайце return каб вярнуць значэнне: 
<code>return $a$;</code> (яго адправіць бот у адказ на паведамленне, якое вызвала макрос)

    - Адправіце каманду /superbind TRIGGER-TEXT у адказ на код макроса, каб выклікаць макрос для кожнага паведамлення, якое ўтрымлівае TRIGGER-TEXT
    - Адправіце каманду /superbind -r REGULAR у адказ на код макроса, каб выклікаць макрос для кожнага паведамлення, якое адпавядае рэгулярнаму выразу REGULAR

Выкарыстоўвайце /examples каб пабачыць прыклады макросаў
Выкарыстоўвайце /settings каб змяніць мову (або іншыя налады)
Выкарыстоўвайце /superunbind каб выдаліць макрос
Выкарыстоўвайце /superbindings каб пабачыць усе макросы ў чаце
        """,
        'pl': """Użyj /superbind, aby utworzyć makro
Do tworzenia makr używany jest prosty język programowania:
    - Każda komenda kończy się symbolem ";"
    - Dostępne są operacje matematyczne: +, -, *, /, ^, |(dzielenie całkowitoliczbowe), %, sin, cos, tan, exp, log, sqrt, abs, ln
    - Dostępne są operacje logiczne: &lt;, &gt;, &lt;=, &gt;=, ==, !=, and, or
    - Możesz tworzyć zmienne: 
<code>a = 1;</code>
    - Możesz używać zmiennych: 
<code>b = $a$ + 1;</code>
    - Możesz używać wartości z obiektu message: 
<code>text = "$message.text$";</code>, <code>id = $message.from_user.id$;</code>, <code>name = "$message.from_user.first_name$";</code>, itd.
    - Możesz używać if-else: 
<code>if ($message.from_user.id$ == 123){text = "Hello";} else{text = "Bye";}</code>
    - Możesz tworzyć listy: 
<code>list = [1, 2, 3, 4]; a = list(0);</code>
    - Możesz używać wyrażeń regularnych: 
<code>text = re "g/([0-9]+) ([0-9]+)/(\\1 + \\2)/" "1 2";</code>
    - Użyj return, aby zwrócić wartość: 
<code>return $a$;</code> (bot wyśle go w odpowiedzi na wiadomość, która wywołała makro)

    - Wyślij polecenie /superbind TRIGGER-TEXT w odpowiedzi na kod makra, aby wywołać makro dla każdej wiadomości zawierającej TRIGGER-TEXT
    - Wyślij polecenie /superbind -r REGULAR w odpowiedzi na kod makra, aby wywołać makro dla każdej wiadomości, która pasuje do wyrażenia regularnego REGULAR

Użyj /examples, aby zobaczyć przykłady makr
Użyj /settings, aby zmienić język (lub inne ustawienia)
Użyj /superunbind, aby usunąć makro
Użyj /superbindings, aby zobaczyć wszystkie makra w czacie
        """,
        'cs': """Použijte /superbind k vytvoření makra
K vytváření maker se používá jednoduchý programovací jazyk:
    - Každý příkaz končí symbolem ";"
    - Jsou k dispozici matematické operace: +, -, *, /, ^, |(celočíselné dělení), %, sin, cos, tan, exp, log, sqrt, abs, ln
    - Jsou k dispozici logické operace: &lt;, &gt;, &lt;=, &gt;=, ==, !=, and, or
    - Můžete vytvářet proměnné: 
<code>a = 1;</code>
    - Můžete používat proměnné: 
<code>b = $a$ + 1;</code>
    - Můžete používat hodnoty z objektu message: 
<code>text = "$message.text$";</code>, <code>id = $message.from_user.id$;</code>, <code>name = "$message.from_user.first_name$";</code>, atd.
    - Můžete používat if-else: 
<code>if ($message.from_user.id$ == 123){text = "Hello";} else{text = "Bye";}</code>
    - Můžete vytvářet seznamy: 
<code>list = [1, 2, 3, 4]; a = list(0);</code>
    - Můžete používat regulární výrazy: 
<code>text = re "g/([0-9]+) ([0-9]+)/(\\1 + \\2)/" "1 2";</code>
    - Použijte return k vrácení hodnoty: 
<code>return $a$;</code> (bot ji odešle jako odpověď na zprávu, která spustila makro)

    - Pošlete příkaz /superbind TRIGGER-TEXT jako odpověď na kód makra, abyste makro vyvolali pro každou zprávu obsahující TRIGGER-TEXT
    - Pošlete příkaz /superbind -r REGULAR jako odpověď na kód makra, abyste makro vyvolali pro každou zprávu, která odpovídá regulárnímu výrazu REGULAR

Použijte /examples k zobrazení příkladů maker
Použijte /settings k změně jazyka (nebo jiných nastavení)
Použijte /superunbind k odstranění makra
Použijte /superbindings k zobrazení všech maker v chatu
        """,
    }
    if message.from_user.id not in languages:
        languages[message.from_user.id] = 'uk'
        # c.execute("INSERT INTO languages VALUES (?, ?)", (message.from_user.id, 'uk'))
        # conn.commit()
        c = db["languages"]
        c.insert_one({'user_id': message.from_user.id, 'language': 'uk'})
    print(languages[message.from_user.id])
    print(macros_description[languages[message.from_user.id]])
    bot.send_message(message.chat.id, macros_description[languages[message.from_user.id]], parse_mode='HTML')


@bot.message_handler(commands=['examples'])
def examples(message):
    examples_text = {
        'uk': """Приклади макросів:
- Повернути повідомлення, що затригерило макрос: 
<code>return "$message.text$";</code>
- Повернути ім'я користувача, що затригерило макрос: 
<code>return "$message.from_user.first_name$";</code>
- Повернути парність тижня з початку навчального року: 
<code>if(($message.date$ - 1693774800) | 86400 | 7 % 2 == 0) {
s = "Зараз непарна неділя";
} else {
s = "Зараз парна неділя";
}
return $s$;</code>
- Замінити всі цифри на 0: 
<code>return re "g/[0-9]/0/" "$message.text$";</code>
""",
        'ru': """Примеры макросов:
- Вернуть сообщение, которое вызвало макрос: 
<code>return "$message.text$";</code>
- Вернуть имя пользователя, которое вызвало макрос: 
<code>return "$message.from_user.first_name$";</code>
- Вернуть четность недели с начала учебного года:
<code>if(($message.date$ - 1693774800) | 86400 | 7 % 2 == 0) {
s = "Сейчас нечетная неделя";
} else {
s = "Сейчас четная неделя";
}
return $s$;</code>
- Заменить все цифры на 0: 
<code>return re "g/[0-9]/0/" "$message.text$";</code>
""",
        'en': """Examples of macros:
- Return the message that triggered the macro: 
<code>return "$message.text$";</code>
- Return the name of the user that triggered the macro: 
<code>return "$message.from_user.first_name$";</code>
- Return the parity of the week from the beginning of the school year:
<code>if(($message.date$ - 1693774800) | 86400 | 7 % 2 == 0) {
s = "Now is an odd week";
} else {
s = "Now is an even week";
}
return $s$;</code>
- Replace all digits with 0: 
<code>return re "g/[0-9]/0/" "$message.text$";</code>
""",
        'de': """Beispiele für Makros:
- Gib die Nachricht zurück, die das Makro ausgelöst hat: 
<code>return "$message.text$";</code>
- Gib den Namen des Benutzers zurück, der das Makro ausgelöst hat: 
<code>return "$message.from_user.first_name$";</code>
- Gib die Parität der Woche seit Beginn des Schuljahres zurück:
<code>if(($message.date$ - 1693774800) | 86400 | 7 % 2 == 0) {
s = "Jetzt ist eine ungerade Woche";
} else {
s = "Jetzt ist eine gerade Woche";
}
return $s$;</code>
- Ersetze alle Ziffern durch 0: 
<code>return re "g/[0-9]/0/" "$message.text$";</code>
""",
        'be': """Прыклады макросаў:
- Вярнуць паведамленне, якое вызвала макрос: 
<code>return "$message.text$";</code>
- Вярнуць імя карыстальніка, якое вызвала макрос: 
<code>return "$message.from_user.first_name$";</code>
- Вярнуць парніцу тыдня з пачатку навучальнага года:
<code>if(($message.date$ - 1693774800) | 86400 | 7 % 2 == 0) {
s = "Зараз непарная неделя";
} else {
s = "Зараз парная неделя";
}
return $s$;</code>
- Замяніць усе лічбы на 0: 
<code>return re "g/[0-9]/0/" "$message.text$";</code>
""",
        'pl': """Przykłady makr:
- Zwróć wiadomość, która wywołała makro: 
<code>return "$message.text$";</code>
- Zwróć nazwę użytkownika, który wywołał makro: 
<code>return "$message.from_user.first_name$";</code>
- Zwróć parzystość tygodnia od początku roku szkolnego:
<code>if(($message.date$ - 1693774800) | 86400 | 7 % 2 == 0) {
s = "Teraz jest nieparzysty tydzień";
} else {
s = "Teraz jest parzysty tydzień";
}
return $s$;</code>
- Zamień wszystkie cyfry na 0: 
<code>return re "g/[0-9]/0/" "$message.text$";</code>
""",
        'cs': """Příklady maker:
- Vraťte zprávu, která spustila makro: 
<code>return "$message.text$";</code>
- Vraťte jméno uživatele, které spustilo makro: 
<code>return "$message.from_user.first_name$";</code>
- Vraťte sudost týdne od začátku školního roku:
<code>if(($message.date$ - 1693774800) | 86400 | 7 % 2 == 0) {
s = "Nyní je lichý týden";
} else {
s = "Nyní je sudý týden";
}
return $s$;</code>
- Nahraďte všechny číslice nulou: ```<code>return re "g/[0-9]/0/" "$message.text$";</code>```
""",}
    if message.from_user.id not in languages:
        languages[message.from_user.id] = 'uk'
        # c.execute("INSERT INTO languages VALUES (?, ?)", (message.from_user.id, 'uk'))
        # conn.commit()
        c = db["languages"]
        c.insert_one({'user_id': message.from_user.id, 'language': 'uk'})
    bot.send_message(message.chat.id, examples_text[languages[message.from_user.id]], parse_mode='HTML')

@bot.message_handler(commands=['settings'])
def settings(message):
    settings_text = {
        'uk': """Налаштування:
/language_uk - встановити українську мову
/language_ru - встановити російську мову
/language_en - встановити англійську мову
/language_de - встановити німецьку мову
/language_be - встановити білоруську мову
/language_pl - встановити польську мову
/language_cs - встановити чеську мову
        """,
        'ru': """Настройки:
/language_uk - установить украинский язык
/language_ru - установить русский язык
/language_en - установить английский язык
/language_de - установить немецкий язык
/language_be - установить белорусский язык
/language_pl - установить польский язык
/language_cs - установить чешский язык
        """,
        'en': """Settings:
/language_uk - set Ukrainian language
/language_ru - set Russian language
/language_en - set English language
/language_de - set German language
/language_be - set Belarusian language
/language_pl - set Polish language
/language_cs - set Czech language
        """,
        'de': """Einstellungen:
/language_uk - Ukrainische Sprache einstellen
/language_ru - Russische Sprache einstellen
/language_en - Englische Sprache einstellen
/language_de - Deutsche Sprache einstellen
/language_be - Weißrussische Sprache einstellen
/language_pl - Polnische Sprache einstellen
/language_cs - Tschechische Sprache einstellen
        """,
        'be': """Налады:
/language_uk - усталяваць украінскую мову
/language_ru - усталяваць рускую мову
/language_en - усталяваць англійскую мову
/language_de - усталяваць нямецкую мову
/language_be - усталяваць беларускую мову
/language_pl - усталяваць польскую мову
/language_cs - усталяваць чэшскую мову
        """,
        'pl': """Ustawienia:
/language_uk - ustaw język ukraiński
/language_ru - ustaw język rosyjski
/language_en - ustaw język angielski
/language_de - ustaw język niemiecki
/language_be - ustaw język białoruski
/language_pl - ustaw język polski
/language_cs - ustaw język czeski
        """,
        'cs': """Nastavení:
/language_uk - nastavit ukrajinský jazyk
/language_ru - nastavit ruský jazyk
/language_en - nastavit anglický jazyk
/language_de - nastavit německý jazyk
/language_be - nastavit běloruský jazyk
/language_pl - nastavit polský jazyk
/language_cs - nastavit český jazyk
        """,
    }
    if message.from_user.id not in languages:
        languages[message.from_user.id] = 'uk'
        # c.execute("INSERT INTO languages VALUES (?, ?)", (message.from_user.id, 'uk'))
        # conn.commit()
        c = db["languages"]
        c.insert_one({'user_id': message.from_user.id, 'language': 'uk'})
    bot.send_message(message.chat.id, settings_text[languages[message.from_user.id]], parse_mode='HTML')



@bot.message_handler(commands=['language_uk'])
def language_uk(message):
    languages[message.from_user.id] = 'uk'
    # c.execute("UPDATE languages SET language = 'uk' WHERE user_id = ?", (message.from_user.id,))
    # if c.rowcount == 0:
    #     c.execute("INSERT INTO languages VALUES (?, ?)", (message.from_user.id, 'uk'))
    # conn.commit()
    c = db["languages"]
    c.update_one({'user_id': message.from_user.id}, {'$set': {'language': 'uk'}})
    bot.reply_to(message, "Ваша мова успішно змінена на українську")

@bot.message_handler(commands=['language_ru'])
def language_ru(message):
    languages[message.from_user.id] = 'ru'
    # c.execute("UPDATE languages SET language = 'ru' WHERE user_id = ?", (message.from_user.id,))
    # if c.rowcount == 0:
    #     c.execute("INSERT INTO languages VALUES (?, ?)", (message.from_user.id, 'ru'))
    # conn.commit()
    c = db["languages"]
    c.update_one({'user_id': message.from_user.id}, {'$set': {'language': 'ru'}})
    bot.reply_to(message, "Ваш язык успешно изменен на русский")

@bot.message_handler(commands=['language_en'])
def language_en(message):
    languages[message.from_user.id] = 'en'
    # c.execute("UPDATE languages SET language = 'en' WHERE user_id = ?", (message.from_user.id,))
    # if c.rowcount == 0:
    #     c.execute("INSERT INTO languages VALUES (?, ?)", (message.from_user.id, 'en'))
    # conn.commit()
    c = db["languages"]
    c.update_one({'user_id': message.from_user.id}, {'$set': {'language': 'en'}})
    bot.reply_to(message, "Your language has been successfully changed to English")

@bot.message_handler(commands=['language_de'])
def language_de(message):
    languages[message.from_user.id] = 'de'
    # c.execute("UPDATE languages SET language = 'de' WHERE user_id = ?", (message.from_user.id,))
    # if c.rowcount == 0:
    #     c.execute("INSERT INTO languages VALUES (?, ?)", (message.from_user.id, 'de'))
    # conn.commit()
    c = db["languages"]
    c.update_one({'user_id': message.from_user.id}, {'$set': {'language': 'de'}})
    bot.reply_to(message, "Ihre Sprache wurde erfolgreich auf Deutsch geändert")

@bot.message_handler(commands=['language_be'])
def language_be(message):
    languages[message.from_user.id] = 'be'
    # c.execute("UPDATE languages SET language = 'be' WHERE user_id = ?", (message.from_user.id,))
    # if c.rowcount == 0:
    #     c.execute("INSERT INTO languages VALUES (?, ?)", (message.from_user.id, 'be'))
    # conn.commit()
    c = db["languages"]
    c.update_one({'user_id': message.from_user.id}, {'$set': {'language': 'be'}})
    bot.reply_to(message, "Ваша мова успішно зменена на беларускую")

@bot.message_handler(commands=['language_pl'])
def language_pl(message):
    languages[message.from_user.id] = 'pl'
    # c.execute("UPDATE languages SET language = 'pl' WHERE user_id = ?", (message.from_user.id,))
    # if c.rowcount == 0:
    #     c.execute("INSERT INTO languages VALUES (?, ?)", (message.from_user.id, 'pl'))
    # conn.commit()
    c = db["languages"]
    c.update_one({'user_id': message.from_user.id}, {'$set': {'language': 'pl'}})
    bot.reply_to(message, "Twoja język został pomyślnie zmieniony na polski")

@bot.message_handler(commands=['language_cs'])
def language_cs(message):
    languages[message.from_user.id] = 'cs'
    # c.execute("UPDATE languages SET language = 'cs' WHERE user_id = ?", (message.from_user.id,))
    # if c.rowcount == 0:
    #     c.execute("INSERT INTO languages VALUES (?, ?)", (message.from_user.id, 'cs'))
    # conn.commit()
    c = db["languages"]
    c.update_one({'user_id': message.from_user.id}, {'$set': {'language': 'cs'}})
    bot.reply_to(message, "Váš jazyk byl úspěšně změněn na češtinu")


@bot.message_handler(commands=['superunbind'])
def superunbind(message):
    if message.from_user.id not in languages:
        languages[message.from_user.id] = 'uk'
        # c.execute("INSERT INTO languages VALUES (?, ?)", (message.from_user.id, 'uk'))
        # conn.commit()
        c = db["languages"]
        c.insert_one({'user_id': message.from_user.id, 'language': 'uk'})
    if (message.text[13:], str(message.chat.id)) in programs:
        del programs[(message.text[13:], str(message.chat.id))]
        bot.reply_to(message, "Макрос успішно видалено")
    else:
        bot.reply_to(message, "Макрос не знайдено")

@bot.message_handler(commands=['superbindings'])
def superbindings(message):
    if message.from_user.id not in languages:
        languages[message.from_user.id] = 'uk'
        # c.execute("INSERT INTO languages VALUES (?, ?)", (message.from_user.id, 'uk'))
        # conn.commit()
        c = db["languages"]
        c.insert_one({'user_id': message.from_user.id, 'language': 'uk'})

    macros_title = {
        'uk': "Макроси",
        'ru': "Макросы",
        'en': "Macros",
        'de': "Makros",
        'be': "Макросы",
        'pl': "Makra",
        'cs': "Makra",
    }
    macros_not_found = {
        'uk': "Макроси не знайдено",
        'ru': "Макросы не найдены",
        'en': "No macros found",
        'de': "Keine Makros gefunden",
        'be': "Макросы не знойдзены",
        'pl': "Nie znaleziono makr",
        'cs': "Nenalezena žádná makra",
    }
    
    bindings = ""
    for (program, chat_id) in programs.keys():
        if int(chat_id) == message.chat.id:
            bindings += "· <code>" + program + "</code>\n"
    if bindings == "":
        bindings = macros_not_found[languages[message.from_user.id]]
    else:
        bindings = f"⛓ {macros_title[languages[message.from_user.id]]}:\n" + bindings
    bot.reply_to(message, bindings, parse_mode='HTML')


@bot.message_handler(commands=['execute'])
def one_time_execute(message):
    try:
        result = execute_program(message.reply_to_message.text, {}, message = message)
        bot.reply_to(message, result, parse_mode='HTML', disable_web_page_preview=True)
    except Exception as e:
        bot.reply_to(message, str(e) + "\n\n" + traceback.format_exc())


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    #bot.leave_chat(-1001756869879)
    print(message.text)
    print(programs.keys())

    if message.text == '\\':
        try:
            reply_to = message.reply_to_message.text
            try:
                result = execute_program(reply_to, {}, message = message)
                bot.reply_to(message, result, parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                bot.reply_to(message, str(e) + "\n\n" + traceback.format_exc())
        except:
            pass

    for (program, chat_id) in programs.keys():
        if message.chat.id == int(chat_id):
            def action():
                try:
                    result = execute_program(programs[(program, chat_id)], {}, message = message)
                    bot.reply_to(message, result, parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    bot.reply_to(message, str(e) + "\n\n" + traceback.format_exc())    
            if program[0:2] == '-r':
                import regex
                if regex.search(program[3:], message.text):
                    action()
            else:
                if program in message.text:
                    action()

from ruiji import img_search
# Handle image messages
@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    # Check that the message in direct chat
    if message.chat.type != 'private':
        #bot.reply_to(message, f"Please send me this image in private chat, your chat id is {message.chat.type}")
        return
    try:
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = 'images/' + file_info.file_path

        # Create folder if not exists
        os.makedirs("/".join(src.split("/")[:-1]), exist_ok=True)

        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, img_search(src))
    except Exception as e:
        bot.reply_to(message, str(e) + "\n\n" + traceback.format_exc())

import pybooru
# inline command for danbooru search
@bot.inline_handler(lambda query: query.query.startswith('danbooru '))
def query_text(inline_query):
    print(inline_query.query)
    try:
        query = inline_query.query.split(' ')
        if len(query) == 1:
            return
        tags = ' '.join(query[1:])
        booru = pybooru.Danbooru('danbooru', username=os.getenv("DANBOORU_USERNAME"), api_key=os.getenv("DANBOORU_API_KEY"))
        posts = booru.post_list(tags=tags, limit=10, random=True)
        results = []
        for post in posts:
            if post['file_url'].endswith('webm') or post['file_url'].endswith('mp4') or post['file_url'].endswith('gif'):
                continue
            results.append(types.InlineQueryResultPhoto(
                id=post['id'],
                photo_url=post['file_url'],
                thumbnail_url=post['preview_file_url'],
                caption=f"{post['tag_string']} | {post['rating']} | {post['score']} | {post['file_ext']}"
            ))
        bot.answer_inline_query(inline_query.id, results)
    except Exception as e:
        print(e)
        bot.answer_inline_query(inline_query.id, [])

bot.polling()
