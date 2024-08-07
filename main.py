
# telegrambot with llama 3 api
# writen by : amirhosein heidarinia

import methods
import llama
from creds import bot_token, admin, home, logger
import database as db

from time import sleep

from telegram.update import Update
from threading import Thread, enumerate
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, CallbackQueryHandler


def active_thread(name):
    for thread in enumerate():
        if thread.name == name and thread.is_alive():
            return True
    return False


def thread_start(update, context):
    try:

        firstname = update.message.chat.first_name
        chat_id = update.message.chat_id
        username = update.message.chat.username
        lastname = update.message.chat.last_name

        if db.add_user(chat_id, username, firstname, lastname):
            context.bot.send_message(chat_id=logger,
                                     text=f"bot started by chat_id: {chat_id}\nname: {firstname}-{lastname}\nusername: @{username}")

        if not methods.check_membership(context, chat_id):
            update.message.reply_text('please join our channel in order to use the bot :))',
                                      reply_markup=methods.join_channel_keyboard)
            return

        update.message.reply_text(
            f"wellcome {firstname}, i am llama 3, ask away 🦙")

    except Exception as error:
        context.bot.send_message(
            chat_id=admin, text=f"error in main start handler: " + str(error))


def thread_prompthandler(update, context):

    chat_id = update.message.chat_id
    prompt = update.message.text
    message_id = update.message.message_id

    if not methods.check_membership(context, chat_id):
        update.message.reply_text('please join our channel in order to use the bot 🦙 :))',
                                  reply_markup=methods.join_channel_keyboard)
        return

    stream_answer = "working on your prompt ...\n\n"
    length_strean = len(stream_answer)

    wait = context.bot.send_message(
        chat_id=chat_id, text=stream_answer, reply_to_message_id=message_id)

    try:
        if update.message.reply_to_message:
            answer = llama.ask_llama_reply(
                prompt, update.message.reply_to_message.text, db.get_current_model(chat_id))
        else:
            answer = llama.ask_llama(prompt, db.get_current_model(chat_id))

        i = 0
        for chunk in answer:
            i += 1
            try:
                stream_answer += chunk.choices[0].delta.content
                if i % 29 == 0:
                    context.bot.edit_message_text(
                        chat_id=update.message.chat_id, message_id=wait.message_id, text=stream_answer)
            except:
                pass

        # context.bot.edit_message_text(
        #     chat_id=update.message.chat_id, message_id=wait.message_id, text=stream_answer[length_strean:])
        # # context.bot.send_message(chat_id=chat_id,
        # #                          text=stream_answer[length_strean:] + "\n\n<a href=llama 3 telegram bot </a>", parse_mode='HTML', disable_web_page_preview=True)
        # # print(stream_answer)

        context.bot.edit_message_text(chat_id=chat_id, message_id=wait.message_id,
                                      text=stream_answer[length_strean:] +
                                      "\n\n<a href='https://t.me/Llama3ai_bot'>llama 3 tel bot🦙</a>",
                                      parse_mode='HTML', disable_web_page_preview=True)

        db.add_usage(chat_id)

    except Exception as error:
        update.message.reply_text(
            'unexpected error happend, please try again later 🦙🙄')
        context.bot.send_message(
            chat_id=admin, text=f"error in main q handler: " + str(error))


def thread_help(update, context):
    update.message.reply_text(
        "i am llama 3 🦙\n with both 8 and 70 b parameters\n use /models to change it ")
    if not methods.check_membership(context, update.message.chat_id):
        update.message.reply_text('also make sure to join our channel to use the bot',
                                  reply_markup=methods.join_channel_keyboard)


def thread_callbackquery(update, context):

    query = update.callback_query

    if query.data == 'joined':
        if methods.check_membership(context, query.message.chat_id):
            query.edit_message_text(
                text=f"you joined :))))\nnow you can use the bot")
        else:
            query.answer("you are not joined tho :(((")

    elif query.data.startswith("model"):
        db.change_model(query.message.chat_id, query.data[len("model_"):])
        query.edit_message_text(
            text=f"active model changed to {query.data[len('model_'):]}")
    if query.message.chat_id == admin:
        if query.data == "db":
            context.bot.send_document(
                chat_id=admin, document=open(home + 'db.sqlite', "rb"))


def thread_admin(update, context):
    if update.message.chat_id == admin:
        update.message.reply_text(
            'wellcome admin', reply_markup=methods.admin_panel)


def thread_models(update, context):
    update.message.reply_text(
        f'your current model: {db.get_current_model(update.message.chat_id)}\n\nchoose your model : ', reply_markup=methods.model_keyboard)


######################################################################################################################################
######################################################################################################################################


def start(update: Update, context: CallbackContext):
    if active_thread("start_"+str(update.message.chat_id)):
        return
    Thread(target=thread_start, name="start_" +
           str(update.message.chat_id), args=(update, context,)).start()


def prompthandler(update: Update, context: CallbackContext):
    if active_thread("prompt_"+str(update.message.chat_id)):
        return
    Thread(target=thread_prompthandler, name="prompt_" +
           str(update.message.chat_id), args=(update, context)).start()


def callbackquery(update: Update, context: CallbackContext):
    Thread(target=thread_callbackquery, args=(update, context, )).start()


def help_(update: Update, context: CallbackContext):
    Thread(target=thread_help, args=(update, context)).start()


def admin_(update: Update, context: CallbackContext):
    Thread(target=thread_admin, args=(update, context)).start()


def models(update: Update, context: CallbackContext):
    Thread(target=thread_models, args=(update, context)).start()


print("going live...")
while True:
    try:
        # ,request_kwargs = {'proxy_url': 'socks5://localhost:2080'}
        updater = Updater(token=bot_token, use_context=True)
        updater.dispatcher.add_handler(CommandHandler('start', start))
        updater.dispatcher.add_handler(CommandHandler('restart', start))
        updater.dispatcher.add_handler(CommandHandler('models', models))

        updater.dispatcher.add_handler(CommandHandler('help', help_))
        updater.dispatcher.add_handler(CommandHandler('admin', admin_))

        updater.dispatcher.add_handler(CallbackQueryHandler(callbackquery))
        updater.dispatcher.add_handler(
            MessageHandler(Filters.text, prompthandler))

        updater.start_polling()
        print("bot is live.")
        break
    except Exception as e:
        print(f"Error. Retrying in 10 sec ... : {e}")
        sleep(10)
