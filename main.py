import logging
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
beautiful_buttons = [f'{i}{chr(int("20E3", 16))}' for i in range(1, 11)]
main_keyboard = [['Выбрать игру'], ['Статистика', '/music']]
songs = ['DNCE Move', 'Black Magic', 'Cake By The Ocean', 'uptown funk', 'U Can t Touch This']


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
/music - случайная песня
/stop - выход'''

    markup = ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=False)
    await update.message.reply_text(
        text,
        reply_markup=markup,
    )

    return MAIN_MENU


async def exit_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['/start']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
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
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

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
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
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

    else:
        markup = ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=False)

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
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
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
        markup = ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=False)
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
        MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
        CHOOSE_GAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_game)],
        PLAYING_GAME: [CallbackQueryHandler(playing_game)],
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



