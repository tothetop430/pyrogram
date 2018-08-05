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

import binascii
import mimetypes
import os
import struct

from pyrogram.api import functions, types
from pyrogram.api.errors import FileIdInvalid
from pyrogram.client.ext import BaseClient, utils
from pyrogram.client.types import (
    InputMediaPhoto, InputMediaVideo, InputMediaAudio
)


class EditMessageMedia(BaseClient):
    def edit_message_media(self,
                           chat_id: int or str,
                           message_id: int,
                           media,
                           reply_markup=None):
        style = self.html if media.parse_mode.lower() == "html" else self.markdown
        caption = media.caption

        if isinstance(media, InputMediaPhoto):
            if os.path.exists(media.media):
                media = self.send(
                    functions.messages.UploadMedia(
                        peer=self.resolve_peer(chat_id),
                        media=types.InputMediaUploadedPhoto(
                            file=self.save_file(media.media)
                        )
                    )
                )

                media = types.InputMediaPhoto(
                    id=types.InputPhoto(
                        id=media.photo.id,
                        access_hash=media.photo.access_hash
                    )
                )
            elif media.media.startswith("http"):
                media = types.InputMediaPhotoExternal(
                    url=media.media
                )
            else:
                try:
                    decoded = utils.decode(media.media)
                    fmt = "<iiqqqqi" if len(decoded) > 24 else "<iiqq"
                    unpacked = struct.unpack(fmt, decoded)
                except (AssertionError, binascii.Error, struct.error):
                    raise FileIdInvalid from None
                else:
                    if unpacked[0] != 2:
                        media_type = BaseClient.MEDIA_TYPE_ID.get(unpacked[0], None)

                        if media_type:
                            raise FileIdInvalid("The file_id belongs to a {}".format(media_type))
                        else:
                            raise FileIdInvalid("Unknown media type: {}".format(unpacked[0]))

                    media = types.InputMediaPhoto(
                        id=types.InputPhoto(
                            id=unpacked[2],
                            access_hash=unpacked[3]
                        )
                    )

        if isinstance(media, InputMediaVideo):
            if os.path.exists(media.media):
                media = self.send(
                    functions.messages.UploadMedia(
                        peer=self.resolve_peer(chat_id),
                        media=types.InputMediaUploadedDocument(
                            mime_type=mimetypes.types_map[".mp4"],
                            file=self.save_file(media.media),
                            attributes=[
                                types.DocumentAttributeVideo(
                                    supports_streaming=media.supports_streaming or None,
                                    duration=media.duration,
                                    w=media.width,
                                    h=media.height
                                ),
                                types.DocumentAttributeFilename(os.path.basename(media.media))
                            ]
                        )
                    )
                )

                media = types.InputMediaDocument(
                    id=types.InputDocument(
                        id=media.document.id,
                        access_hash=media.document.access_hash
                    )
                )
            elif media.media.startswith("http"):
                media = types.InputMediaDocumentExternal(
                    url=media.media
                )
            else:
                try:
                    decoded = utils.decode(media.media)
                    fmt = "<iiqqqqi" if len(decoded) > 24 else "<iiqq"
                    unpacked = struct.unpack(fmt, decoded)
                except (AssertionError, binascii.Error, struct.error):
                    raise FileIdInvalid from None
                else:
                    if unpacked[0] != 4:
                        media_type = BaseClient.MEDIA_TYPE_ID.get(unpacked[0], None)

                        if media_type:
                            raise FileIdInvalid("The file_id belongs to a {}".format(media_type))
                        else:
                            raise FileIdInvalid("Unknown media type: {}".format(unpacked[0]))

                    media = types.InputMediaDocument(
                        id=types.InputDocument(
                            id=unpacked[2],
                            access_hash=unpacked[3]
                        )
                    )

        if isinstance(media, InputMediaAudio):
            if os.path.exists(media.media):
                media = self.send(
                    functions.messages.UploadMedia(
                        peer=self.resolve_peer(chat_id),
                        media=types.InputMediaUploadedDocument(
                            mime_type=mimetypes.types_map.get("." + media.media.split(".")[-1], "audio/mpeg"),
                            file=self.save_file(media.media),
                            attributes=[
                                types.DocumentAttributeAudio(
                                    duration=media.duration,
                                    performer=media.performer,
                                    title=media.title
                                ),
                                types.DocumentAttributeFilename(os.path.basename(media.media))
                            ]
                        )
                    )
                )

                media = types.InputMediaDocument(
                    id=types.InputDocument(
                        id=media.document.id,
                        access_hash=media.document.access_hash
                    )
                )
            elif media.media.startswith("http"):
                media = types.InputMediaDocumentExternal(
                    url=media.media
                )
            else:
                try:
                    decoded = utils.decode(media.media)
                    fmt = "<iiqqqqi" if len(decoded) > 24 else "<iiqq"
                    unpacked = struct.unpack(fmt, decoded)
                except (AssertionError, binascii.Error, struct.error):
                    raise FileIdInvalid from None
                else:
                    if unpacked[0] != 9:
                        media_type = BaseClient.MEDIA_TYPE_ID.get(unpacked[0], None)

                        if media_type:
                            raise FileIdInvalid("The file_id belongs to a {}".format(media_type))
                        else:
                            raise FileIdInvalid("Unknown media type: {}".format(unpacked[0]))

                    media = types.InputMediaDocument(
                        id=types.InputDocument(
                            id=unpacked[2],
                            access_hash=unpacked[3]
                        )
                    )

        r = self.send(
            functions.messages.EditMessage(
                peer=self.resolve_peer(chat_id),
                id=message_id,
                reply_markup=reply_markup.write() if reply_markup else None,
                media=media,
                **style.parse(caption)
            )
        )

        for i in r.updates:
            if isinstance(i, (types.UpdateEditMessage, types.UpdateEditChannelMessage)):
                return utils.parse_messages(
                    self, i.message,
                    {i.id: i for i in r.users},
                    {i.id: i for i in r.chats}
                )
