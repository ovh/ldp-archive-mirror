#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2019, OVH SAS.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of OVH SAS nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY OVH SAS AND CONTRIBUTORS ````AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL OVH SAS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
.. codeauthor:: OVH Group <opensource@ovh.net>


"""
import logging
import os
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class LocalFS:
    def __init__(self, streams, local_db, mirror_directory='mirror'):
        logger.debug("Mirror_directory: {}".format(mirror_directory))
        self.mirror_directory = mirror_directory
        self.streams = streams
        self.local_db = local_db
        self.fs_init()
        self.fs_sync()

    def fs_init(self):
        """ Create stream's folders if needed
        """
        for streamId in self.streams:
            stream_repository = '{}/{}'.format(self.mirror_directory, streamId)
            if not os.path.exists(stream_repository):
                os.makedirs(stream_repository)
                logger.info("Directory {} created".format(stream_repository))

    def fs_sync(self):
        """ Synchronize the fiel system with the local file system
        """
        for archive in self.local_db.db_all_archives():
            archive_id, sha256, filename, stream_id, service, status = archive
            exists = self.fs_archive_exists(stream_id, filename)
            if exists and status == "todo":
                self.local_db.db_archive_update(
                    archive_id=archive_id, available=None, status="done"
                )
                logger.info("Archive {}/{} already available".format(
                    stream_id, filename
                ))
            if not exists and status != "todo":
                self.local_db.db_archive_update(
                    archive_id=archive_id, available=None, status="todo"
                )
                logger.info(
                    "Archive {}/{} missing, download scheduled".format(
                        stream_id, filename
                    )
                )

    def fs_archive_exists(self, stream_id, filename):
        """ Check if the archive exists in local

        :param str stream_id: Stream ID
        :param str filename: File name
        :return: If the file exists
        :rtype: bool
        """
        archive_file_name = self.get_archive_filename(stream_id, filename)
        archive = Path(archive_file_name)
        return archive.is_file()

    def get_archive_filename(self, stream_id, archive_name):
        """ Get archive path

        :param str stream_id: Stream ID
        :param str archive_name: Archive name
        :return: The archive path
        :rtype: str
        """
        return '{}/{}/{}'.format(self.mirror_directory, stream_id, archive_name)

    @staticmethod
    def get_sha256_checksum(filename, block_size=65536):
        """ Compute archive SHA256 checksum

        :param str filename: file path
        :param int block_size: Block size
        :return: The archive SHA256
        :rtype: SHA256
        """
        sha256 = hashlib.sha256()
        with open(filename, 'rb') as f:
            for block in iter(lambda: f.read(block_size), b''):
                sha256.update(block)
        return sha256.hexdigest()
