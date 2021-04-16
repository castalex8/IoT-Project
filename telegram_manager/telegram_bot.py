from abc import abstractmethod
from QR_code_generator import qrcode_generator

from telegram import Update
from typing import Dict
from telegram.ext import (
    Updater,
    CommandHandler,
    PicklePersistence,
    CallbackContext,
)


class TelegramBot:
    def __init__(self):
        # Create the Updater and pass it your bot's token.
        persistence = PicklePersistence(filename='telegram_bot.conversation')
        updater = Updater("1794260533:AAHmR78HyAe9vy5Gm8IqPcLuBxyGDS3JjFM", persistence=persistence)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CommandHandler("help", self.help_msg))
        dispatcher.add_handler(CommandHandler('show_data', self.show_data))
        dispatcher.add_handler(CommandHandler('set_data', self.set_data))
        # dispatcher.add_handler(CommandHandler('find_bridge', self.abstract_find_bridge))
        dispatcher.add_handler(CommandHandler('find_book', self.abstract_find_book))
        dispatcher.add_handler(CommandHandler('reserve_book', self.abstract_reserve_book))
        dispatcher.add_handler(CommandHandler('freespace', self.abstract_freespace))
        dispatcher.add_handler(CommandHandler('sign_in', self.abstract_sign_in))
        dispatcher.add_handler(CommandHandler('qr_code', self.qr_code))

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()

    @staticmethod
    def user_data_to_str(user_data: Dict[str, str]) -> str:
        facts = list()

        for key, value in user_data.items():
            facts.append(f'{key} : {value}')

        return "\n".join(facts).join(['\n', '\n'])

    @staticmethod
    def help_msg(update: Update, context: CallbackContext) -> None:
        update.message.reply_text(
            f"HELP! all the commands:\n"
            "start - welcome message\n"
            "help - help message\n"
            "show_data - show all the user data\n"
            "set_data <state> <region> - set all the user data\n"
            # "find_bridge - find an available bridge for you\n"
            "find_book <title> - find a book with specific title\n"
            "freespace - check if your bridge is free\n"
            "reserve_book <title> - reserve a book with specific title\n"
            "sign_in <name> <email> - sign_in user to the bridge\n"
            "\n"
            "PS: no whitespace inside <...>\n"
        )

    def start(self, update: Update, context: CallbackContext) -> None:
        reply_text = "Hi! My name is BOOK SHARING bot.\n"
        if context.user_data:
            reply_text += (
                f"You already told me your {self.user_data_to_str(context.user_data)}\n"
                "Why don't you search a new book to read or share ones with the community!"
            )
        else:
            reply_text += (
                "Why don't you search a book?\n"
                "Or share with the other your books!"
            )
        update.message.reply_text(reply_text)
        self.help_msg(update, context)

    def show_data(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(
            f"This is what you already told me: {self.user_data_to_str(context.user_data)}"
        )

    @staticmethod
    def set_data(update: Update, context: CallbackContext) -> None:
        info = update.message.text.lower().split()
        # check user input
        if len(info) != 3:
            update.message.reply_text(
                "Error: the correct syntax is:\n"
                "set_data <state> <region> \n- set all the user data, no whitespace inside <...>"
            )
        else:
            state, region = info[1], info[2]
            context.user_data['state'] = state
            context.user_data['region'] = region
            update.message.reply_text(
                "OK, you set:\n"
                f"{state} {region}\n"
                "if you want to change something, repeat \'set_data\' command."
            )

    def abstract_find_bridge(self, update: Update, context: CallbackContext) -> None:
        user_id = update.message.from_user['id']
        self.find_bridge(user_id, context.user_data)
        bridge_id = self.last_rc(user_id)
        if bridge_id != 0:
            context.user_data['bridge'] = bridge_id
            reply_text = f'your Locker is the: {bridge_id}'
            update.message.reply_text(reply_text)
        else:
            update.message.reply_text(
                'Sorry, at the moment no bridge are available, check later!'
            )

    def abstract_find_book(self, update: Update, context: CallbackContext) -> None:
        user_id = update.message.from_user['id']
        info = update.message.text.split()
        # check user input
        if len(info) != 2:
            update.message.reply_text(
                "Error: the correct syntax is:\n"
                "find_book <title>\n- find a book with specific title, no whitespace inside <...>"
            )
        else:
            title = info[1]
            self.find_book(user_id, context.user_data, title)
            ret = self.last_rc(user_id)
            if ret != 0:
                update.message.reply_text(f'Bridge {ret} has the book')
            else:
                update.message.reply_text('NO bridges have this book')

    def abstract_freespace(self, update: Update, context: CallbackContext) -> None:
        user_id = update.message.from_user['id']
        self.freespace(user_id, context.user_data)
        ret = self.last_rc(user_id)
        if ret != 0:
            update.message.reply_text(f'Bridge {ret} has freespace')
        else:
            update.message.reply_text('NO bridges have freespace')

    def abstract_reserve_book(self, update: Update, context: CallbackContext) -> None:
        user_id = update.message.from_user['id']
        info = update.message.text.split()
        # check user input
        if len(info) != 2:
            update.message.reply_text(
                "Error: the correct syntax is:\n"
                "reserve_book <title>\n- reserve a book with specific title,  no whitespace inside <...>"
            )
        else:
            title = info[1]
            self.reserve_book(user_id, context.user_data, title)
            ret = self.last_rc(user_id)
            if ret != 0:
                update.message.reply_text(f'Bridge {ret} reserved the book')
            else:
                update.message.reply_text('No one can reserve this book, it\'s not available now')

    def abstract_sign_in(self, update: Update, context: CallbackContext) -> None:
        user_id = update.message.from_user['id']
        info = update.message.text.split()
        if len(info) != 3:
            update.message.reply_text(
                "Error: the correct syntax is:\n"
                "sign_in <name> <email>\n- sign_in user to the bridge, no whitespace inside <...>\n"
            )
        else:
            self.abstract_find_bridge(update, context)
            name = info[1]
            email = info[2]
            self.sign_in(user_id, context.user_data, name, email)
            ret = self.last_rc(user_id)
            if ret != 0:
                update.message.reply_text(f'SIGN_IN to bridge {ret} completed')
            else:
                update.message.reply_text('Error SIGN_IN, operation not completed')

    @staticmethod
    def qr_code(update: Update, context: CallbackContext):
        user_id = int(update.message.from_user['id'])
        img = qrcode_generator(user_id)
        img_path = "qr_codes/" + str(user_id)+".png"
        img.save(img_path)
        update.message.reply_photo(open(img_path, 'rb'))
        pass

    @abstractmethod
    def find_bridge(self, client_id: int, user_data: dict) -> None:
        pass

    @abstractmethod
    def find_book(self, client_id: int, user_data: dict, title: str) -> None:
        pass

    @abstractmethod
    def freespace(self, client_id: int, user_data: dict) -> None:
        pass

    @abstractmethod
    def reserve_book(self, client_id: int, user_data: dict, title: str) -> None:
        pass

    @abstractmethod
    def sign_in(self, client_id: int, user_data: dict, name: str, email: str) -> None:
        pass

    @abstractmethod
    def last_rc(self, client_id: int) -> str:
        pass
