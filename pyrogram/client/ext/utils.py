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

import logging
import time
from base64 import b64decode, b64encode
from struct import pack
from weakref import proxy

from pyrogram.api.errors import FloodWait
from pyrogram.client import types as pyrogram_types
from ...api import types, functions
from ...api.errors import StickersetInvalid

log = logging.getLogger(__name__)


# TODO: Organize the code better?

class Str(str):
    __slots__ = "_client", "_entities"

    def __init__(self, *args):
        super().__init__()
        self._client = None
        self._entities = None

    def init(self, client, entities):
        self._client = client
        self._entities = entities

    @property
    def text(self):
        return self

    @property
    def markdown(self):
        return self._client.markdown.unparse(self, self._entities)

    @property
    def html(self):
        return self._client.html.unparse(self, self._entities)


ENTITIES = {
    types.MessageEntityMention.ID: "mention",
    types.MessageEntityHashtag.ID: "hashtag",
    types.MessageEntityCashtag.ID: "cashtag",
    types.MessageEntityBotCommand.ID: "bot_command",
    types.MessageEntityUrl.ID: "url",
    types.MessageEntityEmail.ID: "email",
    types.MessageEntityBold.ID: "bold",
    types.MessageEntityItalic.ID: "italic",
    types.MessageEntityCode.ID: "code",
    types.MessageEntityPre.ID: "pre",
    types.MessageEntityTextUrl.ID: "text_link",
    types.MessageEntityMentionName.ID: "text_mention",
    types.MessageEntityPhone.ID: "phone_number"
}


def parse_entities(entities: list, users: dict) -> list:
    output_entities = []

    for entity in entities:
        entity_type = ENTITIES.get(entity.ID, None)

        if entity_type:
            output_entities.append(
                pyrogram_types.MessageEntity(
                    type=entity_type,
                    offset=entity.offset,
                    length=entity.length,
                    url=getattr(entity, "url", None),
                    user=parse_user(
                        users.get(
                            getattr(entity, "user_id", None),
                            None
                        )
                    )
                )
            )

    return output_entities


def parse_chat_photo(photo):
    if not isinstance(photo, (types.UserProfilePhoto, types.ChatPhoto)):
        return None

    if not isinstance(photo.photo_small, types.FileLocation):
        return None

    if not isinstance(photo.photo_big, types.FileLocation):
        return None

    photo_id = getattr(photo, "photo_id", 0)
    loc_small = photo.photo_small
    loc_big = photo.photo_big

    return pyrogram_types.ChatPhoto(
        small_file_id=encode(
            pack(
                "<iiqqqqi", 1, loc_small.dc_id, photo_id, 0, loc_small.volume_id,
                loc_small.secret, loc_small.local_id
            )
        ),
        big_file_id=encode(
            pack(
                "<iiqqqqi", 1, loc_big.dc_id, photo_id, 0, loc_big.volume_id,
                loc_big.secret, loc_big.local_id
            )
        )
    )


def parse_user_status(user_status, user_id: int = None, is_bot: bool = False) -> pyrogram_types.UserStatus or None:
    if is_bot:
        return None

    status = pyrogram_types.UserStatus(user_id)

    if isinstance(user_status, types.UserStatusOnline):
        status.online = True
        status.date = user_status.expires
    elif isinstance(user_status, types.UserStatusOffline):
        status.offline = True
        status.date = user_status.was_online
    elif isinstance(user_status, types.UserStatusRecently):
        status.recently = True
    elif isinstance(user_status, types.UserStatusLastWeek):
        status.within_week = True
    elif isinstance(user_status, types.UserStatusLastMonth):
        status.within_month = True
    else:
        status.long_time_ago = True

    return status


def parse_user(user: types.User) -> pyrogram_types.User or None:
    return pyrogram_types.User(
        id=user.id,
        is_self=user.is_self,
        is_contact=user.contact,
        is_mutual_contact=user.mutual_contact,
        is_deleted=user.deleted,
        is_bot=user.bot,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        language_code=user.lang_code,
        phone_number=user.phone,
        photo=parse_chat_photo(user.photo),
        status=parse_user_status(user.status, is_bot=user.bot),
        restriction_reason=user.restriction_reason
    ) if user else None


def parse_chat(message: types.Message, users: dict, chats: dict) -> pyrogram_types.Chat:
    if isinstance(message.to_id, types.PeerUser):
        return parse_user_chat(users[message.to_id.user_id if message.out else message.from_id])
    elif isinstance(message.to_id, types.PeerChat):
        return parse_chat_chat(chats[message.to_id.chat_id])
    else:
        return parse_channel_chat(chats[message.to_id.channel_id])


def parse_user_chat(user: types.User) -> pyrogram_types.Chat:
    return pyrogram_types.Chat(
        id=user.id,
        type="private",
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        photo=parse_chat_photo(user.photo),
        restriction_reason=user.restriction_reason
    )


def parse_chat_chat(chat: types.Chat) -> pyrogram_types.Chat:
    admins_enabled = getattr(chat, "admins_enabled", None)

    if admins_enabled is not None:
        admins_enabled = not admins_enabled

    return pyrogram_types.Chat(
        id=-chat.id,
        type="group",
        title=chat.title,
        all_members_are_administrators=admins_enabled,
        photo=parse_chat_photo(getattr(chat, "photo", None))
    )


def parse_channel_chat(channel: types.Channel) -> pyrogram_types.Chat:
    return pyrogram_types.Chat(
        id=int("-100" + str(channel.id)),
        type="supergroup" if channel.megagroup else "channel",
        title=channel.title,
        username=getattr(channel, "username", None),
        photo=parse_chat_photo(getattr(channel, "photo", None)),
        restriction_reason=getattr(channel, "restriction_reason")
    )


def parse_thumb(thumb: types.PhotoSize or types.PhotoCachedSize) -> pyrogram_types.PhotoSize or None:
    if isinstance(thumb, (types.PhotoSize, types.PhotoCachedSize)):
        loc = thumb.location

        if isinstance(thumb, types.PhotoSize):
            file_size = thumb.size
        else:
            file_size = len(thumb.bytes)

        if isinstance(loc, types.FileLocation):
            return pyrogram_types.PhotoSize(
                file_id=encode(
                    pack(
                        "<iiqqqqi",
                        0,
                        loc.dc_id,
                        0,
                        0,
                        loc.volume_id,
                        loc.secret,
                        loc.local_id
                    )
                ),
                width=thumb.w,
                height=thumb.h,
                file_size=file_size
            )


def decode(s: str) -> bytes:
    s = b64decode(s + "=" * (-len(s) % 4), "-_")
    r = b""

    assert s[-1] == 2

    i = 0
    while i < len(s) - 1:
        if s[i] != 0:
            r += bytes([s[i]])
        else:
            r += b"\x00" * s[i + 1]
            i += 1

        i += 1

    return r


def encode(s: bytes) -> str:
    r = b""
    n = 0

    for i in s + bytes([2]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0

            r += bytes([i])

    return b64encode(r, b"-_").decode().rstrip("=")


# TODO: Reorganize code, maybe split parts as well
def parse_messages(
        client,
        messages: list or types.Message or types.MessageService or types.MessageEmpty,
        users: dict,
        chats: dict,
        replies: int = 1
) -> pyrogram_types.Message or list:
    is_list = isinstance(messages, list)
    messages = messages if is_list else [messages]
    parsed_messages = []

    for message in messages:
        if isinstance(message, types.Message):
            entities = parse_entities(message.entities, users)

            forward_from = None
            forward_from_chat = None
            forward_from_message_id = None
            forward_signature = None
            forward_date = None

            forward_header = message.fwd_from  # type: types.MessageFwdHeader

            if forward_header:
                forward_date = forward_header.date

                if forward_header.from_id:
                    forward_from = parse_user(users[forward_header.from_id])
                else:
                    forward_from_chat = parse_channel_chat(chats[forward_header.channel_id])
                    forward_from_message_id = forward_header.channel_post
                    forward_signature = forward_header.post_author

            photo = None
            location = None
            contact = None
            venue = None
            audio = None
            voice = None
            animation = None
            video = None
            video_note = None
            sticker = None
            document = None

            media = message.media

            if media:
                if isinstance(media, types.MessageMediaPhoto):
                    photo = media.photo

                    if isinstance(photo, types.Photo):
                        sizes = photo.sizes
                        photo_sizes = []

                        for size in sizes:
                            if isinstance(size, (types.PhotoSize, types.PhotoCachedSize)):
                                loc = size.location

                                if isinstance(size, types.PhotoSize):
                                    file_size = size.size
                                else:
                                    file_size = len(size.bytes)

                                if isinstance(loc, types.FileLocation):
                                    photo_size = pyrogram_types.PhotoSize(
                                        file_id=encode(
                                            pack(
                                                "<iiqqqqi",
                                                2,
                                                loc.dc_id,
                                                photo.id,
                                                photo.access_hash,
                                                loc.volume_id,
                                                loc.secret,
                                                loc.local_id
                                            )
                                        ),
                                        width=size.w,
                                        height=size.h,
                                        file_size=file_size
                                    )

                                    photo_sizes.append(photo_size)

                        photo = pyrogram_types.Photo(
                            id=b64encode(
                                pack(
                                    "<qq",
                                    photo.id,
                                    photo.access_hash
                                ),
                                b"-_"
                            ).decode().rstrip("="),
                            date=photo.date,
                            sizes=photo_sizes
                        )
                elif isinstance(media, types.MessageMediaGeo):
                    geo_point = media.geo

                    if isinstance(geo_point, types.GeoPoint):
                        location = pyrogram_types.Location(
                            longitude=geo_point.long,
                            latitude=geo_point.lat
                        )
                elif isinstance(media, types.MessageMediaContact):
                    contact = pyrogram_types.Contact(
                        phone_number=media.phone_number,
                        first_name=media.first_name,
                        last_name=media.last_name or None,
                        vcard=media.vcard or None,
                        user_id=media.user_id or None
                    )
                elif isinstance(media, types.MessageMediaVenue):
                    venue = pyrogram_types.Venue(
                        location=pyrogram_types.Location(
                            longitude=media.geo.long,
                            latitude=media.geo.lat
                        ),
                        title=media.title,
                        address=media.address,
                        foursquare_id=media.venue_id or None,
                        foursquare_type=media.venue_type
                    )
                elif isinstance(media, types.MessageMediaDocument):
                    doc = media.document

                    if isinstance(doc, types.Document):
                        attributes = {type(i): i for i in doc.attributes}

                        file_name = getattr(
                            attributes.get(
                                types.DocumentAttributeFilename, None
                            ), "file_name", None
                        )

                        if types.DocumentAttributeAudio in attributes:
                            audio_attributes = attributes[types.DocumentAttributeAudio]

                            if audio_attributes.voice:
                                voice = pyrogram_types.Voice(
                                    file_id=encode(
                                        pack(
                                            "<iiqq",
                                            3,
                                            doc.dc_id,
                                            doc.id,
                                            doc.access_hash
                                        )
                                    ),
                                    duration=audio_attributes.duration,
                                    mime_type=doc.mime_type,
                                    file_size=doc.size,
                                    waveform=audio_attributes.waveform,
                                    date=doc.date
                                )
                            else:
                                audio = pyrogram_types.Audio(
                                    file_id=encode(
                                        pack(
                                            "<iiqq",
                                            9,
                                            doc.dc_id,
                                            doc.id,
                                            doc.access_hash
                                        )
                                    ),
                                    duration=audio_attributes.duration,
                                    performer=audio_attributes.performer,
                                    title=audio_attributes.title,
                                    mime_type=doc.mime_type,
                                    file_size=doc.size,
                                    thumb=parse_thumb(doc.thumb),
                                    file_name=file_name,
                                    date=doc.date
                                )
                        elif types.DocumentAttributeAnimated in attributes:
                            video_attributes = attributes.get(types.DocumentAttributeVideo, None)

                            animation = pyrogram_types.Animation(
                                file_id=encode(
                                    pack(
                                        "<iiqq",
                                        10,
                                        doc.dc_id,
                                        doc.id,
                                        doc.access_hash
                                    )
                                ),
                                width=getattr(video_attributes, "w", 0),
                                height=getattr(video_attributes, "h", 0),
                                duration=getattr(video_attributes, "duration", 0),
                                thumb=parse_thumb(doc.thumb),
                                mime_type=doc.mime_type,
                                file_size=doc.size,
                                file_name=file_name,
                                date=doc.date
                            )
                        elif types.DocumentAttributeVideo in attributes:
                            video_attributes = attributes[types.DocumentAttributeVideo]

                            if video_attributes.round_message:
                                video_note = pyrogram_types.VideoNote(
                                    file_id=encode(
                                        pack(
                                            "<iiqq",
                                            13,
                                            doc.dc_id,
                                            doc.id,
                                            doc.access_hash
                                        )
                                    ),
                                    length=video_attributes.w,
                                    duration=video_attributes.duration,
                                    thumb=parse_thumb(doc.thumb),
                                    file_size=doc.size,
                                    mime_type=doc.mime_type,
                                    date=doc.date
                                )
                            else:
                                video = pyrogram_types.Video(
                                    file_id=encode(
                                        pack(
                                            "<iiqq",
                                            4,
                                            doc.dc_id,
                                            doc.id,
                                            doc.access_hash
                                        )
                                    ),
                                    width=video_attributes.w,
                                    height=video_attributes.h,
                                    duration=video_attributes.duration,
                                    thumb=parse_thumb(doc.thumb),
                                    mime_type=doc.mime_type,
                                    file_size=doc.size,
                                    file_name=file_name,
                                    date=doc.date
                                )
                        elif types.DocumentAttributeSticker in attributes:
                            image_size_attributes = attributes.get(types.DocumentAttributeImageSize, None)
                            sticker_attribute = attributes[types.DocumentAttributeSticker]

                            if isinstance(sticker_attribute.stickerset, types.InputStickerSetID):
                                try:
                                    set_name = client.send(
                                        functions.messages.GetStickerSet(sticker_attribute.stickerset)
                                    ).set.short_name
                                except StickersetInvalid:
                                    set_name = None
                            else:
                                set_name = None

                            sticker = pyrogram_types.Sticker(
                                file_id=encode(
                                    pack(
                                        "<iiqq",
                                        8,
                                        doc.dc_id,
                                        doc.id,
                                        doc.access_hash
                                    )
                                ),
                                width=image_size_attributes.w if image_size_attributes else 0,
                                height=image_size_attributes.h if image_size_attributes else 0,
                                thumb=parse_thumb(doc.thumb),
                                # TODO: mask_position
                                set_name=set_name,
                                emoji=sticker_attribute.alt or None,
                                file_size=doc.size,
                                mime_type=doc.mime_type,
                                file_name=file_name,
                                date=doc.date
                            )
                        else:
                            document = pyrogram_types.Document(
                                file_id=encode(
                                    pack(
                                        "<iiqq",
                                        5,
                                        doc.dc_id,
                                        doc.id,
                                        doc.access_hash
                                    )
                                ),
                                thumb=parse_thumb(doc.thumb),
                                file_name=file_name,
                                mime_type=doc.mime_type,
                                file_size=doc.size,
                                date=doc.date
                            )
                else:
                    media = None

            reply_markup = message.reply_markup

            if reply_markup:
                if isinstance(reply_markup, types.ReplyKeyboardForceReply):
                    reply_markup = pyrogram_types.ForceReply.read(reply_markup)
                elif isinstance(reply_markup, types.ReplyKeyboardMarkup):
                    reply_markup = pyrogram_types.ReplyKeyboardMarkup.read(reply_markup)
                elif isinstance(reply_markup, types.ReplyInlineMarkup):
                    reply_markup = pyrogram_types.InlineKeyboardMarkup.read(reply_markup)
                elif isinstance(reply_markup, types.ReplyKeyboardHide):
                    reply_markup = pyrogram_types.ReplyKeyboardRemove.read(reply_markup)
                else:
                    reply_markup = None

            m = pyrogram_types.Message(
                message_id=message.id,
                date=message.date,
                chat=parse_chat(message, users, chats),
                from_user=parse_user(users.get(message.from_id, None)),
                text=Str(message.message) or None if media is None else None,
                caption=Str(message.message) or None if media is not None else None,
                entities=entities or None if media is None else None,
                caption_entities=entities or None if media is not None else None,
                author_signature=message.post_author,
                forward_from=forward_from,
                forward_from_chat=forward_from_chat,
                forward_from_message_id=forward_from_message_id,
                forward_signature=forward_signature,
                forward_date=forward_date,
                edit_date=message.edit_date,
                media_group_id=message.grouped_id,
                photo=photo,
                location=location,
                contact=contact,
                venue=venue,
                audio=audio,
                voice=voice,
                animation=animation,
                video=video,
                video_note=video_note,
                sticker=sticker,
                document=document,
                views=message.views,
                via_bot=parse_user(users.get(message.via_bot_id, None)),
                outgoing=message.out,
                client=proxy(client),
                reply_markup=reply_markup
            )

            if m.text:
                m.text.init(m._client, m.entities or [])

            if m.caption:
                m.caption.init(m._client, m.caption_entities or [])

            if message.reply_to_msg_id and replies:
                while True:
                    try:
                        m.reply_to_message = client.get_messages(
                            m.chat.id,
                            reply_to_message_ids=message.id,
                            replies=replies - 1
                        )
                    except FloodWait as e:
                        log.warning("get_messages flood: waiting {} seconds".format(e.x))
                        time.sleep(e.x)
                        continue
                    else:
                        break
        elif isinstance(message, types.MessageService):
            action = message.action

            new_chat_members = None
            left_chat_member = None
            new_chat_title = None
            delete_chat_photo = None
            migrate_to_chat_id = None
            migrate_from_chat_id = None
            group_chat_created = None
            channel_chat_created = None
            new_chat_photo = None

            if isinstance(action, types.MessageActionChatAddUser):
                new_chat_members = [parse_user(users[i]) for i in action.users]
            elif isinstance(action, types.MessageActionChatJoinedByLink):
                new_chat_members = [parse_user(users[message.from_id])]
            elif isinstance(action, types.MessageActionChatDeleteUser):
                left_chat_member = parse_user(users[action.user_id])
            elif isinstance(action, types.MessageActionChatEditTitle):
                new_chat_title = action.title
            elif isinstance(action, types.MessageActionChatDeletePhoto):
                delete_chat_photo = True
            elif isinstance(action, types.MessageActionChatMigrateTo):
                migrate_to_chat_id = action.channel_id
            elif isinstance(action, types.MessageActionChannelMigrateFrom):
                migrate_from_chat_id = action.chat_id
            elif isinstance(action, types.MessageActionChatCreate):
                group_chat_created = True
            elif isinstance(action, types.MessageActionChannelCreate):
                channel_chat_created = True
            elif isinstance(action, types.MessageActionChatEditPhoto):
                photo = action.photo

                if isinstance(photo, types.Photo):
                    sizes = photo.sizes
                    photo_sizes = []

                    for size in sizes:
                        if isinstance(size, (types.PhotoSize, types.PhotoCachedSize)):
                            loc = size.location

                            if isinstance(size, types.PhotoSize):
                                file_size = size.size
                            else:
                                file_size = len(size.bytes)

                            if isinstance(loc, types.FileLocation):
                                photo_size = pyrogram_types.PhotoSize(
                                    file_id=encode(
                                        pack(
                                            "<iiqqqqi",
                                            2,
                                            loc.dc_id,
                                            photo.id,
                                            photo.access_hash,
                                            loc.volume_id,
                                            loc.secret,
                                            loc.local_id
                                        )
                                    ),
                                    width=size.w,
                                    height=size.h,
                                    file_size=file_size
                                )

                                photo_sizes.append(photo_size)

                    new_chat_photo = pyrogram_types.Photo(
                        id=b64encode(
                            pack(
                                "<qq",
                                photo.id,
                                photo.access_hash
                            ),
                            b"-_"
                        ).decode().rstrip("="),
                        date=photo.date,
                        sizes=photo_sizes
                    )

            m = pyrogram_types.Message(
                message_id=message.id,
                date=message.date,
                chat=parse_chat(message, users, chats),
                from_user=parse_user(users.get(message.from_id, None)),
                new_chat_members=new_chat_members,
                left_chat_member=left_chat_member,
                new_chat_title=new_chat_title,
                new_chat_photo=new_chat_photo,
                delete_chat_photo=delete_chat_photo,
                migrate_to_chat_id=int("-100" + str(migrate_to_chat_id)) if migrate_to_chat_id else None,
                migrate_from_chat_id=-migrate_from_chat_id if migrate_from_chat_id else None,
                group_chat_created=group_chat_created,
                channel_chat_created=channel_chat_created,
                client=proxy(client)
                # TODO: supergroup_chat_created
            )

            if isinstance(action, types.MessageActionPinMessage):
                while True:
                    try:
                        m.pinned_message = client.get_messages(
                            m.chat.id,
                            reply_to_message_ids=message.id,
                            replies=0
                        )
                    except FloodWait as e:
                        log.warning("get_messages flood: waiting {} seconds".format(e.x))
                        time.sleep(e.x)
                        continue
                    else:
                        break
        else:
            m = pyrogram_types.Message(message_id=message.id, client=proxy(client))

        parsed_messages.append(m)

    return parsed_messages if is_list else parsed_messages[0]


def parse_deleted_messages(
        messages: list,
        channel_id: int
) -> pyrogram_types.Messages:
    parsed_messages = []

    for message in messages:
        parsed_messages.append(
            pyrogram_types.Message(
                message_id=message,
                chat=(pyrogram_types.Chat(id=int("-100" + str(channel_id)), type="channel")
                      if channel_id is not None
                      else None)
            )
        )

    return pyrogram_types.Messages(len(parsed_messages), parsed_messages)


def get_peer_id(input_peer) -> int:
    return (
        input_peer.user_id if isinstance(input_peer, types.InputPeerUser)
        else -input_peer.chat_id if isinstance(input_peer, types.InputPeerChat)
        else int("-100" + str(input_peer.channel_id))
    )


def get_input_peer(peer_id: int, access_hash: int):
    return (
        types.InputPeerUser(peer_id, access_hash) if peer_id > 0
        else types.InputPeerChannel(int(str(peer_id)[4:]), access_hash)
        if (str(peer_id).startswith("-100") and access_hash)
        else types.InputPeerChat(-peer_id)
    )


def get_offset_date(dialogs):
    for m in reversed(dialogs.messages):
        if isinstance(m, types.MessageEmpty):
            continue
        else:
            return m.date
    else:
        return 0


def parse_profile_photos(photos):
    if isinstance(photos, types.photos.Photos):
        total_count = len(photos.photos)
    else:
        total_count = photos.count

    user_profile_photos = []

    for photo in photos.photos:
        if isinstance(photo, types.Photo):
            sizes = photo.sizes
            photo_sizes = []

            for size in sizes:
                if isinstance(size, (types.PhotoSize, types.PhotoCachedSize)):
                    loc = size.location

                    if isinstance(size, types.PhotoSize):
                        file_size = size.size
                    else:
                        file_size = len(size.bytes)

                    if isinstance(loc, types.FileLocation):
                        photo_size = pyrogram_types.PhotoSize(
                            file_id=encode(
                                pack(
                                    "<iiqqqqi",
                                    2,
                                    loc.dc_id,
                                    photo.id,
                                    photo.access_hash,
                                    loc.volume_id,
                                    loc.secret,
                                    loc.local_id
                                )
                            ),
                            width=size.w,
                            height=size.h,
                            file_size=file_size
                        )

                        photo_sizes.append(photo_size)

            user_profile_photos.append(
                pyrogram_types.Photo(
                    id=b64encode(
                        pack(
                            "<qq",
                            photo.id,
                            photo.access_hash
                        ),
                        b"-_"
                    ).decode().rstrip("="),
                    date=photo.date,
                    sizes=photo_sizes
                )
            )

    return pyrogram_types.UserProfilePhotos(
        total_count=total_count,
        photos=user_profile_photos
    )


def parse_callback_query(client, callback_query, users):
    peer = callback_query.peer

    if isinstance(peer, types.PeerUser):
        peer_id = peer.user_id
    elif isinstance(peer, types.PeerChat):
        peer_id = -peer.chat_id
    else:
        peer_id = int("-100" + str(peer.channel_id))

    return pyrogram_types.CallbackQuery(
        id=str(callback_query.query_id),
        from_user=parse_user(users[callback_query.user_id]),
        message=client.get_messages(peer_id, callback_query.msg_id),
        chat_instance=str(callback_query.chat_instance),
        data=callback_query.data.decode(),
        game_short_name=callback_query.game_short_name,
        client=client
    )


def parse_inline_callback_query(client, callback_query, users):
    return pyrogram_types.CallbackQuery(
        id=str(callback_query.query_id),
        from_user=parse_user(users[callback_query.user_id]),
        chat_instance=str(callback_query.chat_instance),
        inline_message_id=b64encode(
            pack(
                "<iqq",
                callback_query.msg_id.dc_id,
                callback_query.msg_id.id,
                callback_query.msg_id.access_hash
            ),
            b"-_"
        ).decode().rstrip("="),
        game_short_name=callback_query.game_short_name,
        client=client
    )


def parse_chat_full(
        client,
        chat_full: types.messages.ChatFull or types.UserFull
) -> pyrogram_types.Chat:
    if isinstance(chat_full, types.UserFull):
        parsed_chat = parse_user_chat(chat_full.user)
        parsed_chat.description = chat_full.about
    else:
        full_chat = chat_full.full_chat
        chat = None

        for i in chat_full.chats:
            if full_chat.id == i.id:
                chat = i

        if isinstance(full_chat, types.ChatFull):
            parsed_chat = parse_chat_chat(chat)

            if isinstance(full_chat.participants, types.ChatParticipants):
                parsed_chat.members_count = len(full_chat.participants.participants)
        else:
            parsed_chat = parse_channel_chat(chat)
            parsed_chat.members_count = full_chat.participants_count
            parsed_chat.description = full_chat.about or None
            # TODO: Add StickerSet type
            parsed_chat.can_set_sticker_set = full_chat.can_set_stickers
            parsed_chat.sticker_set_name = full_chat.stickerset

            if full_chat.pinned_msg_id:
                parsed_chat.pinned_message = client.get_messages(
                    parsed_chat.id,
                    message_ids=full_chat.pinned_msg_id
                )

        if isinstance(full_chat.exported_invite, types.ChatInviteExported):
            parsed_chat.invite_link = full_chat.exported_invite.link

    return parsed_chat


def parse_dialog_chat(peer, users: dict, chats: dict):
    if isinstance(peer, types.PeerUser):
        return parse_user_chat(users[peer.user_id])
    elif isinstance(peer, types.PeerChat):
        return parse_chat_chat(chats[peer.chat_id])
    else:
        return parse_channel_chat(chats[peer.channel_id])


def parse_chat_members(members: types.channels.ChannelParticipants or types.messages.ChatFull):
    users = {i.id: i for i in members.users}
    parsed_members = []

    if isinstance(members, types.channels.ChannelParticipants):
        members = members.participants

        for member in members:
            user = parse_user(users[member.user_id])

            if isinstance(member, (types.ChannelParticipant, types.ChannelParticipantSelf)):
                parsed_members.append(
                    pyrogram_types.ChatMember(
                        user=user,
                        status="member"
                    )
                )
            elif isinstance(member, types.ChannelParticipantCreator):
                parsed_members.append(
                    pyrogram_types.ChatMember(
                        user=user,
                        status="creator"
                    )
                )
            elif isinstance(member, types.ChannelParticipantAdmin):
                rights = member.admin_rights  # type: types.ChannelAdminRights

                parsed_members.append(
                    pyrogram_types.ChatMember(
                        user=user,
                        status="administrator",
                        can_be_edited=member.can_edit,
                        can_change_info=rights.change_info,
                        can_post_messages=rights.post_messages,
                        can_edit_messages=rights.edit_messages,
                        can_delete_messages=rights.delete_messages,
                        can_invite_users=rights.invite_users or rights.invite_link,
                        can_restrict_members=rights.ban_users,
                        can_pin_messages=rights.pin_messages,
                        can_promote_members=rights.add_admins
                    )
                )
            elif isinstance(member, types.ChannelParticipantBanned):
                rights = member.banned_rights  # type: types.ChannelBannedRights

                chat_member = pyrogram_types.ChatMember(
                    user=user,
                    status="kicked" if rights.view_messages else "restricted",
                    until_date=0 if rights.until_date == (1 << 31) - 1 else rights.until_date
                )

                if chat_member.status == "restricted":
                    chat_member.can_send_messages = not rights.send_messages
                    chat_member.can_send_media_messages = not rights.send_media
                    chat_member.can_send_other_messages = (
                            not rights.send_stickers or not rights.send_gifs or
                            not rights.send_games or not rights.send_inline
                    )
                    chat_member.can_add_web_page_previews = not rights.embed_links

                parsed_members.append(chat_member)

        return pyrogram_types.ChatMembers(
            total_count=members.count,
            chat_members=parsed_members
        )
    else:
        members = members.full_chat.participants.participants

        for member in members:
            user = parse_user(users[member.user_id])

            if isinstance(member, types.ChatParticipant):
                parsed_members.append(
                    pyrogram_types.ChatMember(
                        user=user,
                        status="member"
                    )
                )
            elif isinstance(member, types.ChatParticipantCreator):
                parsed_members.append(
                    pyrogram_types.ChatMember(
                        user=user,
                        status="creator"
                    )
                )
            elif isinstance(member, types.ChatParticipantAdmin):
                parsed_members.append(
                    pyrogram_types.ChatMember(
                        user=user,
                        status="administrator"
                    )
                )

        return pyrogram_types.ChatMembers(
            total_count=len(members),
            chat_members=parsed_members
        )
