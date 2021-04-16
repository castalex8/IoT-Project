from telegram_manager import Update
from typing import Dict
from telegram_manager.ext import (
    Updater,
    CommandHandler,
    PicklePersistence,
    CallbackContext,
)


def user_data_to_str(user_data: Dict[str, str]) -> str:
    facts = list()

    for key, value in user_data.items():
        facts.append(f'{key} : {value}')

    return "\n".join(facts).join(['\n', '\n'])


def start(update: Update, context: CallbackContext) -> None:
    reply_text = "Hi! My name is BOOK SHARING bot.\n"
    if context.user_data:
        reply_text += (
            f"You already told me your {user_data_to_str(context.user_data)}\n"
            "Why don't you search new book to read or share whit the community your books!"
        )
    else:
        reply_text += (
            "Why don't you search a book?\n"
            "Or share with the other your books!"
        )
    update.message.reply_text(reply_text)


def help_msg(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        f"HELP! all the commands:\n"
        "start - welcome message\n"
        "help - help message\n"
        "show_data - show all the user data\n"
        "set_data <state> <region> <town> - set all the user data\n"
        "find_bridge - find an available bridge for you\n"
        "find_book <title> - find a book with specific title\n"
        "freespace - check if your bridge is free\n"
        "reserve_book <title> - reserve a book with specific title\n"
        "sign_in <name> <email> - sign_in user to the bridge\n"
        "\n"
        "PS: no whitespace inside <...>\n"
    )


# Create the Updater and pass it your bot's token.
persistence = PicklePersistence(filename='telegram_bot.conversation')
updater = Updater("1461110529:AAGM-pRZrQINcEFae-0sGMng630laeAQACM", persistence=persistence)

# Get the dispatcher to register handlers
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_msg))

# Start the Bot
updater.start_polling()

# Run the bot until you press Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.
updater.idle()



