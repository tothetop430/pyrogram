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

from pyrogram.api import functions, types
from ...ext import BaseClient


class UnpinChatMessage(BaseClient):
    def unpin_chat_message(self, chat_id: int or str):
        # TODO: Docstrings
        peer = self.resolve_peer(chat_id)

        if isinstance(peer, types.InputPeerChannel):
            self.send(
                functions.channels.UpdatePinnedMessage(
                    channel=peer,
                    id=0
                )
            )
        elif isinstance(peer, types.InputPeerChat):
            raise ValueError("The chat_id \"{}\" belongs to a basic group".format(chat_id))
        else:
            raise ValueError("The chat_id \"{}\" belongs to a user".format(chat_id))

        return True
