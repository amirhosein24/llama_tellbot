

from creds import join_channel
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def check_membership(context, chat_id):
    try:
        for channel in join_channel.keys():
            if context.bot.get_chat_member(chat_id=join_channel[channel][0], user_id=chat_id).status == 'member':
                continue
            else:
                return False
        return True
    except Exception:
        return True


# ###################################################### keyboards


admin_panel = [
    InlineKeyboardButton("send to all", callback_data='sendall')], [
    InlineKeyboardButton("send data base", callback_data='db')]
admin_panel = InlineKeyboardMarkup(admin_panel)


join_channel_keyboard = []
for channel in join_channel.keys():

    join_channel_keyboard.append(
        [InlineKeyboardButton(channel, url=join_channel[channel][1])])

join_channel_keyboard.append(
    [InlineKeyboardButton("i joined :)", callback_data='joined')])

join_channel_keyboard = InlineKeyboardMarkup(join_channel_keyboard)
