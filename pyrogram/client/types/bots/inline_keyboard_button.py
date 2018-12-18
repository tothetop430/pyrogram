# Pyrogram - Telegram MTProto API Client Library for Python
# Copyright (C) 2017-2018 Dan Tès <https://github.com/delivrance>
#
# This file is part of Pyrogram.
#
# Pyrogram is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pyrogram is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from pyrogram.api.types import (
    KeyboardButtonUrl, KeyboardButtonCallback,
    KeyboardButtonSwitchInline
)
from ..pyrogram_type import PyrogramType


class InlineKeyboardButton(PyrogramType):
    """This object represents one button of an inline keyboard. You must use exactly one of the optional fields.

    Args:
        text (``str``):
            Label text on the button.

        callback_data (``bytes``, *optional*):
            Data to be sent in a callback query to the bot when button is pressed, 1-64 bytes.

        url (``str``, *optional*):
            HTTP url to be opened when button is pressed.

        switch_inline_query (``str``, *optional*):
            If set, pressing the button will prompt the user to select one of their chats, open that chat and insert
            the bot's username and the specified inline query in the input field. Can be empty, in which case just
            the bot's username will be inserted.Note: This offers an easy way for users to start using your bot in
            inline mode when they are currently in a private chat with it. Especially useful when combined with
            switch_pm… actions – in this case the user will be automatically returned to the chat they switched from,
            skipping the chat selection screen.

        switch_inline_query_current_chat (``str``, *optional*):
            If set, pressing the button will insert the bot's username and the specified inline query in the current
            chat's input field. Can be empty, in which case only the bot's username will be inserted.This offers a
            quick way for the user to open your bot in inline mode in the same chat – good for selecting something
            from multiple options.
    """

    # TODO: Add callback_game and pay fields

    def __init__(self, text: str, callback_data: bytes = None, url: str = None,
                 switch_inline_query: str = None, switch_inline_query_current_chat: str = None):
        super().__init__(None)

        self.text = text
        self.url = url
        self.callback_data = callback_data
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat
        # self.callback_game = callback_game
        # self.pay = pay

    @staticmethod
    def read(o):
        if isinstance(o, KeyboardButtonUrl):
            return InlineKeyboardButton(
                text=o.text,
                url=o.url
            )

        if isinstance(o, KeyboardButtonCallback):
            return InlineKeyboardButton(
                text=o.text,
                callback_data=o.data
            )

        if isinstance(o, KeyboardButtonSwitchInline):
            if o.same_peer:
                return InlineKeyboardButton(
                    text=o.text,
                    switch_inline_query_current_chat=o.query
                )
            else:
                return InlineKeyboardButton(
                    text=o.text,
                    switch_inline_query=o.query
                )

    def write(self):
        if self.callback_data:
            return KeyboardButtonCallback(self.text, self.callback_data)

        if self.url:
            return KeyboardButtonUrl(self.text, self.url)

        if self.switch_inline_query:
            return KeyboardButtonSwitchInline(self.text, self.switch_inline_query)

        if self.switch_inline_query_current_chat:
            return KeyboardButtonSwitchInline(self.text, self.switch_inline_query_current_chat, same_peer=True)
