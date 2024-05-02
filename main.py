import logging
import random
from random import choice

import requests

from data import db_session
from data.models.user import User
from data.models.game import Game
from data.models.question import Question
from data.models.answer import Answer
from data.models.result import Result

from support.make_agree_with_number import make_agree_with_number
from support.get_result import get_result

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes, ConversationHandler, \
    CallbackQueryHandler
from dotenv import dotenv_values

config = dotenv_values(".env")
BOT_TOKEN = config["TOKEN"]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARNING
)

logger = logging.getLogger(__name__)

MAIN_MENU = 'main_menu'
CHOOSE_GAME = 'choose_game'
PLAYING_GAME = 'playing_game'
FOR_GAMES = 'for_games'
PLAYING_HANGMAN = 'playing_hangman'

beautiful_buttons = [f'{i}{chr(int("20E3", 16))}' for i in range(1, 11)]
main_keyboard = [
    ['Выбрать игру', 'для игр'],
    ['Статистика', '/music'],
]
songs = ['DNCE Move', 'Black Magic', 'Cake By The Ocean', 'uptown funk', 'U Can t Touch This']

HANGMAN = (
    """
     ------
     |    |
     |
     |
     |
     |
     |
    ----------
    """,
    """
     ------
     |    |
     |    O
     |
     |
     |
     |
    ----------
    """,
    """
     ------
     |    |
     |    O
     |    |
     | 
     |   
     |    
    ----------
    """,
    """
     ------
     |    |
     |    O
     |   /|
     |   
     |   
     |   
    ----------
    """,
    """
     ------
     |    |
     |    O
     |   /|\\
     |   
     |   
     |     
    ----------
    """,
    """
     ------
     |    |
     |    O
     |   /|\\
     |   /
     |   
     |    
    ----------
    """,
    """
     ------
     |    |
     |    O
     |   /|\\
     |   / \\
     |   
     |   
    ----------
    """
)

WORDS = ("питон", "игра", "программирование")  # Слова для угадывания


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    db_sess = db_session.create_session()
    if list(db_sess.query(User).filter(User.name == user.name)):
        text = f'С возвращением, {user.first_name}! (/help - помощь)'
    else:
        new_bd_user = User(name=user.name)
        db_sess.add(new_bd_user)
        db_sess.commit()
        text = f'''Добро пожаловать в игру "Кто ты из мультиков", {user.first_name}!
Для взаимодействия с ботом используйте встроенную в него клавиатуру с командами.
Также эти команды можно вводить с помощью клавиатуры вашего устройства.

Для выбора варианта ответа в момент ответа на вопрос нажмите на кнопку в чате с нужным номером.

Эти команды работают в любое время:
/help - помощь
/music - случайная песня
/stop - выход'''

    markup = ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text(
        text,
        reply_markup=markup,
    )

    return MAIN_MENU


async def exit_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['/start']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Заходите поиграть снова! Ваши результаты сохранены.",
        reply_markup=markup,
    )
    return ConversationHandler.END


async def game_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """Помощь.
Этот бот скажет вам, кто ты из мультиков.
Для взаимодействия с ботом используйте встроенную в него клавиатуру с командами.
Также эти команды можно вводить с помощью клавиатуры вашего устройства.

Для выбора варианта ответа в момент ответа на вопрос нажмите на кнопку в чате с нужным номером.

Эти команды работают в любое время:
/music - случайная песня
/stop - выход""",
    )


async def music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://spotify23.p.rapidapi.com/search/"
    song = choice(songs)
    querystring = {"q": song, "type": "multi", "offset": "0", "limit": "10", "numberOfTopResults": "5"}

    headers = {
        "X-RapidAPI-Key": "81aa96d6bamsh080a667c145161ep135b79jsncb93f929b216",
        "X-RapidAPI-Host": "spotify23.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    track_id = data['tracks']['items'][0]['data']['id']
    name = data['tracks']['items'][0]['data']['name']
    url = "https://spotify23.p.rapidapi.com/tracks/"
    querystring = {"ids": track_id}
    headers = {
        "X-RapidAPI-Key": "81aa96d6bamsh080a667c145161ep135b79jsncb93f929b216",
        "X-RapidAPI-Host": "spotify23.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    file = requests.get(data['tracks'][0]['preview_url'])
    with open(f'audio.mp3', 'wb') as f:
        f.write(file.content)

    await update.message.reply_audio('audio.mp3', title=f'{name}.mp3')


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.lower()
    if command == 'выбрать игру':
        db_sess = db_session.create_session()
        games = list(db_sess.query(Game).order_by(Game.created_at))

        reply_keyboard = []
        text = 'Выберете игру из списка:\n'

        for i, game in enumerate(games):
            if i % 3 == 0:
                reply_keyboard.append([])
            reply_keyboard[-1].append(str(i + 1))
            text += f'{i + 1}) {game.name}\n'
        text += '(Введите номер игры или выберете номер на клавиатуре бота)'
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

        context.user_data['games_to_choose_ids'] = [g.id for g in games]

        await update.message.reply_text(text, reply_markup=markup)
        return CHOOSE_GAME

    elif command == 'статистика':
        user = update.effective_user
        db_sess = db_session.create_session()
        is_player = list(db_sess.query(User).filter(User.name == user.name))
        if is_player:
            player = is_player[0]
        else:
            reply_keyboard = [['/start']]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(
                "Почему-то вас нету в списке игроков. Перезапустите бота, пожалуйста.",
                reply_markup=markup
            )
            return ConversationHandler.END
        logging.info(f'Player id: {player.id}')
        answered_questions = make_agree_with_number('раз', player.answered_questions)
        text = f'''Вот ваша статистика:
Кол-во уникальных игр: {len(player.unique_games.split(',')) - 1}
Кол-во сыгранных игр всего: {player.total_games}
Получено различных результатов: {len(player.unique_results.split(',')) - 1}
Отвечено на вопросы: {answered_questions}'''

        await update.message.reply_text(text)
        return MAIN_MENU

    elif command == 'для игр':
        text = f'''Вы находитесь в разделе "Для игр"
Здесь вы можете воспользоваться функцией броска кубика, монетки или поставить таймер.
Команды:
/one_dice - кинуть один шестигранный кубик
/two_dices - кинуть 2 шестигранных кубика одновременно
/twenty_sides_dice - кинуть 20-гранный кубик
/throw_coin - бросить монетку
/timer_30s - поставить таймер на 30 секунд
/timer_1m - поставить таймер на 1 минуту
/timer_5m - поставить таймер на 5 минут
/timer_10m - поставить таймер на 10 минут
/back
'''

        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardRemove(),
        )
        return FOR_GAMES

    else:
        markup = ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=False, resize_keyboard=True)

        await update.message.reply_text(
            f"Вы в главом меню. Выберите команду на клавиатуре бота",
            reply_markup=markup,
        )
        return MAIN_MENU


async def choose_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game = update.message.text
    games_to_choose_ids = context.user_data['games_to_choose_ids']

    if not game.isdigit() or int(game) - 1 < 0 or int(game) - 1 >= len(games_to_choose_ids):
        await update.message.reply_text('Воспользуйтесь клавиатурой бота для выбора игры.')
    else:
        db_sess = db_session.create_session()
        game_id = context.user_data['games_to_choose_ids'][int(game) - 1]
        game = db_sess.query(Game).get(game_id)
        logging.info(f'Chosen game: {game.id} {game.name}')
        logging.info(f'Questions amount: {len(game.questions)}')

        context.user_data['curr_game_id'] = game.id
        context.user_data['curr_question'] = 0
        context.user_data['results_count'] = {}

        for res in game.results:
            context.user_data['results_count'][res.name] = 0

        await update.message.reply_text(
            f'Вы выбрали игру "{game.name}"'
        )

        reply_keyboard = [['/music']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
        await update.message.reply_text(
            game.description,
            reply_markup=markup,
        )

        context.user_data['last_update'] = update

        text, reply_markup = ask_question(game.questions[0].answers, game.questions[0].text)
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
        )

        return PLAYING_GAME


def remove_job_if_exists(name, context: ContextTypes.DEFAULT_TYPE):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def task(context: ContextTypes.DEFAULT_TYPE):
    text = f'Время истекло'
    await context.bot.send_message(context.job.chat_id, text=text)


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)


def get_dice_emoji(n):
    dice_emojis = '⚀⚁⚂⚃⚄⚅'
    emoji = dice_emojis[n - 1]
    return emoji


async def one_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n = random.randint(1, 6)
    emoji = get_dice_emoji(n)
    text = f'Вам выпало {n} {emoji}'
    await update.effective_message.reply_text(text)


async def two_dices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n1 = random.randint(1, 6)
    emoji1 = get_dice_emoji(n1)
    n2 = random.randint(1, 6)
    emoji2 = get_dice_emoji(n2)
    text = f'Вам выпали {n1} {emoji1}, {n2} {emoji2}'
    await update.effective_message.reply_text(text)


async def twenty_sides_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n = random.randint(1, 6)
    text = f'Вам выпало {n}'
    await update.effective_message.reply_text(text)


async def throw_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n = random.randint(1, 2)
    if n == 1:
        side_name = 'орёл'
    else:
        side_name = 'решка'

    text = f'Результат броска: {side_name}'
    await update.effective_message.reply_text(text)


async def timer_30s(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.user_data["timer_text"] = 'тридцать секунд'
    context.job_queue.run_once(task, 30, chat_id=chat_id, name=str(chat_id), data=30)
    text = f'Засек 30 секунд!'

    if job_removed:
        text += ' Старый таймер удалён.'
    await update.effective_message.reply_text(text)



async def timer_1m(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.user_data["timer_text"] = 'одна минута'
    context.job_queue.run_once(task, 60, chat_id=chat_id, name=str(chat_id), data=60)
    text = f'Засек минуту!'

    if job_removed:
        text += ' Старый таймер удалён.'
    await update.effective_message.reply_text(text)


async def timer_5m(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.user_data["timer_text"] = 'пять минут'
    context.job_queue.run_once(task, 60 * 5, chat_id=chat_id, name=str(chat_id), data=60 * 5)
    text = f'Засек 5 минут!'

    if job_removed:
        text += ' Старый таймер удалён.'
    await update.effective_message.reply_text(text)


async def timer_10m(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    context.user_data["timer_text"] = 'десять минут'
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task, 60 * 10, chat_id=chat_id, name=str(chat_id), data=60*10)
    text = f'Засек 10 минут!'

    if job_removed:
        text += ' Старый таймер удалён.'
    await update.effective_message.reply_text(text)




async def timer_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = main_keyboard
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    text = 'Вы в главном меню.'
    await update.message.reply_html(
        text,
        reply_markup=markup
    )

    return MAIN_MENU


async def start_hangman(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["max_wrong"] = len(HANGMAN) - 1
    context.user_data["word"] = choice(WORDS)  # Слово, которое нужно угадать
    context.user_data["so_far"] = "_" * len(context.user_data["word"])  # Одна черточка для каждой буквы в слове, которое нужно угадать
    context.user_data["wrong"] = 0  # Количество неверных предположений, сделанных игроком
    context.user_data["used"] = []  # Буквы уже угаданы

    await update.message.reply_html(
        HANGMAN[0]
    )

    await update.message.reply_html(
        "Введите свое предположение:"
    )

    return PLAYING_HANGMAN


async def play_hangman(update: Update, context: ContextTypes.DEFAULT_TYPE):
    max_wrong = context.user_data["max_wrong"]
    word = context.user_data["word"]
    so_far = context.user_data["so_far"]
    wrong = context.user_data["wrong"]
    used = context.user_data["used"]
    if wrong < max_wrong and so_far != word:

        guess = update.message.text

        while guess in used:
            await update.message.reply_html(
                f"Вы уже вводили букву {guess}"
            )
            await update.message.reply_html(
                "Введите свое предположение:"
            )
            return

        used.append(guess)  # В список использованных букв добавляется введённая буква

        if guess in word:  # Если введённая буква есть в загаданном слове, то выводим соответствующее сообщение
            await update.message.reply_html(
                f"Да! {guess} есть в слове!"
            )
            new = ""
            for i in range(len(word)):  # В цикле добавляем найденную букву в нужное место
                if guess == word[i]:
                    new += guess
                else:
                    new += so_far[i]
            so_far = new

        else:
            await update.message.reply_html(
                f'Извините, буквы "{guess}" нет в слове.'
            )

            wrong += 1

        context.user_data["max_wrong"] = max_wrong
        context.user_data["word"] = word
        context.user_data["so_far"] = so_far
        context.user_data["wrong"] = wrong
        context.user_data["used"] = used

        await update.message.reply_html(
            HANGMAN[wrong]
        )
        await update.message.reply_html(
            f"Вы использовали следующие буквы:\n{used}"
        )
        await update.message.reply_html(
            f"На данный момент слово выглядит так:\n{so_far}"
        )

        await update.message.reply_html(
            "Введите свое предположение:"
        )

    else:
        if wrong == max_wrong:  # Если игрок превысил кол-во ошибок, то его повесили
            await update.message.reply_html(
                HANGMAN[wrong]
            )
            await update.message.reply_html(
                "Тебя повесили!"
            )
        else:
            await update.message.reply_html(
                "Вы угадали слово!"
            )

        await update.message.reply_html(
            f'Загаданное слово было "{word}"'
        )

        return MAIN_MENU


def ask_question(answers, text):
    keyboard = []
    for i in range(len(answers)):
        if i % 4 == 0:
            keyboard.append([])
        keyboard[-1].append(InlineKeyboardButton(beautiful_buttons[i], callback_data=i))

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = text + '\n'
    for i, ans in enumerate(answers):
        text += f'{i + 1}) {ans.text}\n'
    return text, reply_markup


async def playing_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    db_sess = db_session.create_session()

    game_id = context.user_data['curr_game_id']

    game = db_sess.query(Game).get(game_id)

    question = game.questions[context.user_data['curr_question']]
    last_text = ask_question(question.answers, question.text)[0]
    last_text += f'\n|Вы выбрали {int(query.data) + 1}|'
    await query.edit_message_text(text=last_text)

    chosen_answer = question.answers[int(query.data)]
    logger.info(f'chosen_answer: {chosen_answer.id} {chosen_answer.text}')

    for add in chosen_answer.add_point.split(','):
        context.user_data['results_count'][add] += 1

    context.user_data['curr_question'] += 1

    user = update.effective_user
    player = db_sess.query(User).filter(User.name == user.name).first()
    player.answered_questions += 1

    db_sess.commit()

    game_id = context.user_data['curr_game_id']

    game = db_sess.query(Game).get(game_id)

    if context.user_data['curr_question'] == len(game.questions):
        res_id, name, description, image_url, count_users = get_result(context.user_data['results_count'])
        player.total_games += 1
        played_game = player.unique_games.split(',')
        if str(game.id) not in played_game:
            player.unique_games += str(game.id) + ','
        unique_results = player.unique_results.split(',')
        if str(res_id) not in unique_results:
            player.unique_results += str(res_id) + ','
        db_sess.commit()
        chat_id = context.user_data['last_update'].message.chat_id
        await context.bot.send_photo(chat_id=chat_id, photo=open(image_url, 'rb'))
        markup = ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=False, resize_keyboard=True)
        await context.user_data['last_update'].message.reply_text(
            f'''Вы {name}!
{description}

Сколько раз был получен этот результат: {count_users}.

Вы можете снова выбрать игру или посмотреть свою статистику.''',
            reply_markup=markup
        )

        return MAIN_MENU

    next_question = game.questions[context.user_data['curr_question']]

    text, reply_markup = ask_question(next_question.answers, next_question.text)
    await context.user_data['last_update'].message.reply_text(
        text,
        reply_markup=reply_markup,
    )

    return PLAYING_GAME

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    db_session.global_init("db/database.sqlite")

    states = {
        MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu),
                    CommandHandler('start_hangman', start_hangman)],
        CHOOSE_GAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_game)],
        PLAYING_GAME: [CallbackQueryHandler(playing_game)],
        FOR_GAMES: [
            CommandHandler('one_dice', one_dice),
            CommandHandler('two_dices', two_dices),
            CommandHandler('twenty_sides_dice', twenty_sides_dice),
            CommandHandler('throw_coin', throw_coin),
            CommandHandler('timer_30s', timer_30s),
            CommandHandler('timer_1m', timer_1m),
            CommandHandler('timer_5m', timer_5m),
            CommandHandler('timer_10m', timer_10m),
            CommandHandler('back',timer_back),
        ],
        PLAYING_HANGMAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, play_hangman)]
    }

    # Добавляю функции, которыми можно воспользоваться в любой момент
    for s in states:
        states[s].append(CommandHandler('help', game_help))
        states[s].append(CommandHandler('music', music))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states=states,
        fallbacks=[CommandHandler('stop', exit_game)]
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()



