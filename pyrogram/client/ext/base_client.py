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

import os
import platform
import re
from queue import Queue
from threading import Lock

from pyrogram import __version__
from ..style import Markdown, HTML
from ...session.internals import MsgId


class BaseClient:
    class StopTransmission(StopIteration):
        pass

    APP_VERSION = "Pyrogram {}".format(__version__)

    DEVICE_MODEL = "{} {}".format(
        platform.python_implementation(),
        platform.python_version()
    )

    SYSTEM_VERSION = "{} {}".format(
        platform.system(),
        platform.release()
    )

    LANG_CODE = "en"

    INVITE_LINK_RE = re.compile(r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/joinchat/)([\w-]+)$")
    BOT_TOKEN_RE = re.compile(r"^\d+:[\w-]+$")
    DIALOGS_AT_ONCE = 100
    UPDATES_WORKERS = 1
    DOWNLOAD_WORKERS = 1
    OFFLINE_SLEEP = 900
    WORKERS = 4
    WORKDIR = "."
    CONFIG_FILE = "./config.ini"

    MEDIA_TYPE_ID = {
        0: "photo_thumbnail",
        1: "chat_photo",
        2: "photo",
        3: "voice",
        4: "video",
        5: "document",
        8: "sticker",
        9: "audio",
        10: "animation",
        13: "video_note",
        14: "document_thumbnail"
    }

    mime_types_to_extensions = {}
    extensions_to_mime_types = {}

    with open("{}/mime.types".format(os.path.dirname(__file__)), "r", encoding="UTF-8") as f:
        for match in re.finditer(r"^([^#\s]+)\s+(.+)$", f.read(), flags=re.M):
            mime_type, extensions = match.groups()

            extensions = [".{}".format(ext) for ext in extensions.split(" ")]

            for ext in extensions:
                extensions_to_mime_types[ext] = mime_type

            mime_types_to_extensions[mime_type] = " ".join(extensions)

    def __init__(self):
        self.is_bot = None
        self.dc_id = None
        self.auth_key = None
        self.user_id = None
        self.date = None

        self.rnd_id = MsgId

        self.peers_by_id = {}
        self.peers_by_username = {}
        self.peers_by_phone = {}

        self.markdown = Markdown(self)
        self.html = HTML(self)

        self.session = None
        self.media_sessions = {}
        self.media_sessions_lock = Lock()

        self.is_started = None
        self.is_idle = None

        self.takeout_id = None

        self.updates_queue = Queue()
        self.updates_workers_list = []
        self.download_queue = Queue()
        self.download_workers_list = []

        self.disconnect_handler = None

    def send(self, *args, **kwargs):
        pass

    def resolve_peer(self, *args, **kwargs):
        pass

    def fetch_peers(self, *args, **kwargs):
        pass

    def add_handler(self, *args, **kwargs):
        pass

    def save_file(self, *args, **kwargs):
        pass

    def get_messages(self, *args, **kwargs):
        pass

    def get_history(self, *args, **kwargs):
        pass

    def get_dialogs(self, *args, **kwargs):
        pass

    def get_chat_members(self, *args, **kwargs):
        pass

    def get_chat_members_count(self, *args, **kwargs):
        pass

    def answer_inline_query(self, *args, **kwargs):
        pass

    def guess_mime_type(self, *args, **kwargs):
        pass

    def guess_extension(self, *args, **kwargs):
        pass

    def get_profile_photos(self, *args, **kwargs):
        pass
