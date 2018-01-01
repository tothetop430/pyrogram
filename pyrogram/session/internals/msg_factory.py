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

from pyrogram.api.core import Message, MsgContainer, Object
from pyrogram.api.functions import Ping, HttpWait
from pyrogram.api.types import MsgsAck
from .msg_id import MsgId
from .seq_no import SeqNo

not_content_related = [Ping, HttpWait, MsgsAck, MsgContainer]


class MsgFactory:
    def __init__(self, msg_id: MsgId):
        self.msg_id = msg_id
        self.seq_no = SeqNo()

    def __call__(self, body: Object) -> Message:
        return Message(
            body,
            self.msg_id(),
            self.seq_no(type(body) not in not_content_related),
            len(body)
        )
