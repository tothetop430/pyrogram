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

import abc
from typing import Type, Union

import pyrogram
from pyrogram.api import types


class SessionDoesNotExist(Exception):
    pass


class SessionStorage(abc.ABC):
    def __init__(self, client: 'pyrogram.client.BaseClient'):
        self._client = client

    @abc.abstractmethod
    def load(self):
        ...

    @abc.abstractmethod
    def save(self, sync=False):
        ...

    @abc.abstractmethod
    def sync_cleanup(self):
        ...
    
    @property
    @abc.abstractmethod
    def dc_id(self):
        ...

    @dc_id.setter
    @abc.abstractmethod
    def dc_id(self, val):
        ...

    @property
    @abc.abstractmethod
    def test_mode(self):
        ...

    @test_mode.setter
    @abc.abstractmethod
    def test_mode(self, val):
        ...

    @property
    @abc.abstractmethod
    def auth_key(self):
        ...

    @auth_key.setter
    @abc.abstractmethod
    def auth_key(self, val):
        ...

    @property
    @abc.abstractmethod
    def user_id(self):
        ...

    @user_id.setter
    @abc.abstractmethod
    def user_id(self, val):
        ...

    @property
    @abc.abstractmethod
    def date(self):
        ...

    @date.setter
    @abc.abstractmethod
    def date(self, val):
        ...

    @property
    @abc.abstractmethod
    def is_bot(self):
        ...

    @is_bot.setter
    @abc.abstractmethod
    def is_bot(self, val):
        ...

    @abc.abstractmethod
    def clear_cache(self):
        ...

    @abc.abstractmethod
    def cache_peer(self, entity: Union[types.User,
                                       types.Chat, types.ChatForbidden,
                                       types.Channel, types.ChannelForbidden]):
        ...

    @abc.abstractmethod
    def get_peer_by_id(self, val: int):
        ...

    @abc.abstractmethod
    def get_peer_by_username(self, val: str):
        ...

    @abc.abstractmethod
    def get_peer_by_phone(self, val: str):
        ...

    def get_peer(self, peer_id: Union[int, str]):
        if isinstance(peer_id, int):
            return self.get_peer_by_id(peer_id)
        else:
            peer_id = peer_id.lstrip('+@')
            if peer_id.isdigit():
                return self.get_peer_by_phone(peer_id)
            return self.get_peer_by_username(peer_id)

    @abc.abstractmethod
    def peers_count(self):
        ...

    @abc.abstractmethod
    def contacts_count(self):
        ...
