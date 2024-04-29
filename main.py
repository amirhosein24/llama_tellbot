
# telegrambot with llama 3 api
# writen by : amirhosein heidarinia

import methods
import llama
from creds import bot_token, admin
import database as db

from json import load
from time import sleep
from os import remove

from telegram.update import Update
from threading import Thread, enumerate, Lock
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

# home = __file__[:-7] TODO


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
            context.bot.send_message(chat_id=admin,
                                     text=f"bot started by chat_id: {chat_id}\nname: {firstname}-{lastname}\nusername: @{username}")

        if not methods.check_membership(context, chat_id):
            update.message.reply_text('please join our channel in order to use the bot :))',
                                      reply_markup=methods.join_channel_keyboard)
            return

        update.message.reply_text(f"wellcome {firstname}, i am llama 3")

    except Exception as error:
        context.bot.send_message(
            chat_id=admin, text=f"error in main start handler: " + str(error))


def thread_promthandler(update, context):
    chat_id = update.message.chat_id
    promt = update.message.text
    message_id = update.message.message_id

    if not methods.check_membership(context, chat_id):
        update.message.reply_text('please join our channel in order to use the bot :))',
                                  reply_markup=methods.join_channel_keyboard)
        return

    stream_answer = "working on your promt ...\n\n"
    length_strean = len(stream_answer)
    wait = context.bot.send_message(
        chat_id=chat_id, text=stream_answer, reply_to_message_id=message_id)

    try:
        answer = llama.ask_llama(promt)

        for chunk in answer:
            try:
                stream_answer += chunk.choices[0].delta.content
                context.bot.edit_message_text(
                    chat_id=update.message.chat_id, message_id=wait.message_id, text=stream_answer)
            except:
                pass

        context.bot.edit_message_text(
            chat_id=update.message.chat_id, message_id=wait.message_id, text=stream_answer[length_strean:])

    except Exception as e:
        context.bot.send_message(
            chat_id=admin, text=f"error in main q handler: " + str(e))


def thread_help(update, context):
    update.message.reply_text("i am llama 3 🦙")
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


######################################################################################################################################
######################################################################################################################################


def start(update: Update, context: CallbackContext):
    if active_thread("start_"+str(update.message.chat_id)):
        return
    Thread(target=thread_start, name="start_" +
           str(update.message.chat_id), args=(update, context,)).start()


def promthandler(update: Update, context: CallbackContext):
    if active_thread("promt_"+str(update.message.chat_id)):
        return
    Thread(target=thread_promthandler, name="promt_" +
           str(update.message.chat_id), args=(update, context)).start()


def callbackquery(update: Update, context: CallbackContext):
    Thread(target=thread_callbackquery, args=(update, context, )).start()


def help(update: Update, context: CallbackContext):
    Thread(target=thread_help, args=(update, context)).start()


print("going live...")
while True:
    try:
        # ,request_kwargs = {'proxy_url': 'socks5://localhost:2080'}
        updater = Updater(token=bot_token, use_context=True)
        updater.dispatcher.add_handler(CommandHandler('start', start))
        updater.dispatcher.add_handler(CommandHandler('restart', start))

        updater.dispatcher.add_handler(CommandHandler('help', help))

        updater.dispatcher.add_handler(CallbackQueryHandler(callbackquery))
        updater.dispatcher.add_handler(
            MessageHandler(Filters.text, promthandler))

        updater.start_polling()
        print("bot is live.")
        break
    except Exception as e:
        print(f"Error. Retrying in 10 sec ... : {e}")
        sleep(10)
