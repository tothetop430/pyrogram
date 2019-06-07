# Pyrogram - Telegram MTProto API Client Library for Python
# Copyright (C) 2017-2019 Dan Tès <https://github.com/delivrance>
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

from typing import Union

import pyrogram
from pyrogram.api import functions, types
from pyrogram.errors import UserNotParticipant
from ...ext import BaseClient


class GetChatMember(BaseClient):
    def get_chat_member(
        self,
        chat_id: Union[int, str],
        user_id: Union[int, str]
    ) -> "pyrogram.ChatMember":
        """Get information about one member of a chat.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            user_id (``int`` | ``str``)::
                Unique identifier (int) or username (str) of the target user.
                For you yourself you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

        Returns:
            :obj:`ChatMember`: On success, a chat member is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        chat = self.resolve_peer(chat_id)
        user = self.resolve_peer(user_id)

        if isinstance(chat, types.InputPeerChat):
            full_chat = self.send(
                functions.messages.GetFullChat(
                    chat_id=chat.chat_id
                )
            )

            for member in pyrogram.ChatMembers._parse(self, full_chat).chat_members:
                if isinstance(user, types.InputPeerSelf):
                    if member.user.is_self:
                        return member
                else:
                    if member.user.id == user.user_id:
                        return member
            else:
                raise UserNotParticipant
        elif isinstance(chat, types.InputPeerChannel):
            r = self.send(
                functions.channels.GetParticipant(
                    channel=chat,
                    user_id=user
                )
            )

            users = {i.id: i for i in r.users}

            return pyrogram.ChatMember._parse(self, r.participant, users)
        else:
            raise ValueError("The chat_id \"{}\" belongs to a user".format(chat_id))
