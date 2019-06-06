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

from typing import List

import pyrogram
from .photo import Photo
from ..object import Object


class ProfilePhotos(Object):
    """Contains a user's profile pictures.

    Parameters:
        total_count (``int``):
            Total number of profile pictures the target user has.

        profile_photos (List of :obj:`Photo`):
            Requested profile pictures.
    """

    __slots__ = ["total_count", "profile_photos"]

    def __init__(
        self,
        *,
        client: "pyrogram.BaseClient" = None,
        total_count: int,
        profile_photos: List[Photo]
    ):
        super().__init__(client)

        self.total_count = total_count
        self.profile_photos = profile_photos

    @staticmethod
    def _parse(client, photos) -> "ProfilePhotos":
        return ProfilePhotos(
            total_count=getattr(photos, "count", len(photos.photos)),
            profile_photos=[Photo._parse(client, photo) for photo in photos.photos],
            client=client
        )
