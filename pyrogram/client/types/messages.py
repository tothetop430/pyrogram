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


class Messages(Object):
    """This object represents a chat's messages.

    Args:
        total_count (``int``):
            Total number of messages the target chat has.

        messages (List of :obj:`Message <pyrogram.Message>`):
            Requested messages.
    """

    ID = 0xb0700026

    def __init__(self, total_count: int, messages: list):
        self.total_count = total_count  # int
        self.messages = messages  # Vector<Vector<PhotoSize>>
