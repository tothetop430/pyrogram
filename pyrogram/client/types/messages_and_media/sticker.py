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


class Sticker(Object):
    """This object represents a sticker.

    Args:
        file_id (``str``):
            Unique identifier for this file.

        width (``int``):
            Sticker width.

        height (``int``):
            Sticker height.

        thumb (:obj:`PhotoSize <pyrogram.PhotoSize>`, *optional*):
            Sticker thumbnail in the .webp or .jpg format.

        file_name (``str``, *optional*):
            Sticker file name.

        mime_type (``str``, *optional*):
            MIME type of the file as defined by sender.

        file_size (``int``, *optional*):
            File size.

        date (``int``, *optional*):
            Date the sticker was sent in Unix time.

        emoji (``str``, *optional*):
            Emoji associated with the sticker.

        set_name (``str``, *optional*):
            Name of the sticker set to which the sticker belongs.
    """

    # TODO: Add mask position
    ID = 0xb0700017

    def __init__(
            self,
            file_id: str,
            width: int,
            height: int,
            thumb=None,
            file_name: str = None,
            mime_type: str = None,
            file_size: int = None,
            date: int = None,
            emoji: str = None,
            set_name: str = None,
            mask_position=None
    ):
        self.file_id = file_id
        self.thumb = thumb
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size
        self.date = date
        self.width = width
        self.height = height
        self.emoji = emoji
        self.set_name = set_name
        self.mask_position = mask_position
