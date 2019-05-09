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

from pyrogram.api import functions
from ...ext import BaseClient


class GetContactsCount(BaseClient):
    def get_contacts_count(self) -> int:
        """Use this method to get the total count of contacts from your Telegram address book.

        Returns:
            ``int``: On success, an integer is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """

        return len(self.send(functions.contacts.GetContacts(hash=0)).contacts)
