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

from pyrogram.api.core import Object


class User(Object):
    """This object represents a Telegram user or bot.

    Args:
        id (``int``):
            Unique identifier for this user or bot.

        is_self(``bool``):
            True, if this user is you yourself.

        is_contact(``bool``):
            True, if this user is in your contacts.

        is_mutual_contact(``bool``):
            True, if you both have each other's contact.

        is_deleted(``bool``):
            True, if this user is deleted.

        is_bot (``bool``):
            True, if this user is a bot.

        first_name (``str``):
            User's or bot's first name.

        status (:obj:`UserStatus <pyrogram.UserStatus>`, *optional*):
            User's Last Seen status. Empty for bots.

        last_name (``str``, *optional*):
            User's or bot's last name.

        username (``str``, *optional*):
            User's or bot's username.

        language_code (``str``, *optional*):
            IETF language tag of the user's language.

        phone_number (``str``, *optional*):
            User's phone number.

        photo (:obj:`ChatPhoto <pyrogram.ChatPhoto>`, *optional*):
            User's or bot's current profile photo. Suitable for downloads only.

        restriction_reason (``str``, *optional*):
            The reason why this bot might be unavailable to some users.
    """

    ID = 0xb0700001

    def __init__(
            self,
            id: int,
            is_self: bool,
            is_contact: bool,
            is_mutual_contact: bool,
            is_deleted: bool,
            is_bot: bool,
            first_name: str,
            status=None,
            last_name: str = None,
            username: str = None,
            language_code: str = None,
            phone_number: str = None,
            photo=None,
            restriction_reason: str = None
    ):
        self.id = id
        self.is_self = is_self
        self.is_contact = is_contact
        self.is_mutual_contact = is_mutual_contact
        self.is_deleted = is_deleted
        self.is_bot = is_bot
        self.first_name = first_name
        self.status = status
        self.last_name = last_name
        self.username = username
        self.language_code = language_code
        self.phone_number = phone_number
        self.photo = photo
        self.restriction_reason = restriction_reason
