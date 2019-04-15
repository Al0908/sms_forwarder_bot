from telebot import TeleBot, types

from bot.models import TgUser
from bot.singleton import SingletonType
from forwarder.settings import TELEGRAM_TOKEN


class Bot(TeleBot, metaclass=SingletonType):
    """
    TeleBot with singleton metaclass.
    """

    def __init__(self, token: str):
        """
        Instantiates the bot.
        :param token: Telegram bot token
        """
        super().__init__(token)

        # Setup handlers
        self.handle_start = self.message_handler(commands=["start"])(self.handle_start)

    def handle_start(self, msg: types.Message) -> types.Message:
        """
        Handles the `/start [code] [username]` command.

        :param msg: Message instance
        :return: API call result
        """
        if msg.text.strip() == "/start":
            return self.send_message(
                msg.chat.id,
                'Install the <a href="https://github.com/OptimalStrategy/sms_forwarder_app">android app</a> '
                "to get your SMS messages delivered straight to your inbox.",
                parse_mode="HTML",
            )
        data = msg.text.split(maxsplit=1)
        data = data[-1].split("_", maxsplit=1)
        if len(data) < 2:
            return self.send_message(msg.chat.id, "Invalid setup command.")
        code, username = data
        username = username.lower()

        # Check if provided username and account are the same
        if username != msg.from_user.username.lower():
            return self.send_message(
                msg.chat.id, "You cannot setup bot for other users."
            )

        u = TgUser.by_username(username)
        # Create new TgUser account if such user does not exist
        if u is None:
            TgUser.create(msg.chat.id, code, username)
        # Otherwise update the code
        else:
            u.code = code
            u.save()
        return self.send_message(
            msg.chat.id, "Done! You are ready to receive notifications."
        )


__bot__ = Bot(TELEGRAM_TOKEN)
