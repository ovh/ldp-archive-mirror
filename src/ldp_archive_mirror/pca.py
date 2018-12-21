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
import requests
import urllib.request

from datetime import datetime, timezone, timedelta
from urllib.error import HTTPError

logger = logging.getLogger(__name__)


class CloudArchive:
    def __init__(self, local_db, local_fs, ovh_api):
        self.busy = True
        self.local_db = local_db
        self.local_fs = local_fs
        self.ovh_api = ovh_api
        self.pca_init()

    def pca_init(self):
        """ Fetch all archive with the todo status
        """
        for archive in self.local_db.db_all_todo_archives():
            archive_id, sha256, filename, stream_id, service, status = archive
            self.pca_download(service=service, stream_id=stream_id,
                              archive_id=archive_id, sha256=sha256,
                              archive_file_name=self.local_fs.
                              get_archive_filename(stream_id, filename))

    def pca_download(self, service, stream_id, archive_id, sha256,
                     archive_file_name):
        """ Download PCA archive

        :param str service: Service name
        :param str stream_id: Stream Id
        :param str archive_id: Archive Id
        :param sha256 sha256: Archive sha256sum
        :param str archive_file_name: archive path
        """
        url = self.ovh_api.api_get_archive_url(
            service=service, stream_id=stream_id, archive_id=archive_id
        )
        if url is None:
            return
        status = "todo"
        delta = None
        try:
            self.busy = True
            with urllib.request.urlopen(url) \
                    as response, open(archive_file_name, 'wb') as out_file:
                data = response.read()
                out_file.write(data)
            logger.info(
                "Archive {} downloaded".format(archive_file_name)
            )
            if self.local_fs.get_sha256_checksum(
                    archive_file_name) == sha256:
                logger.info("Sha256 OK on {}".format(archive_file_name))
                status = "done"
            else:
                os.remove(archive_file_name)
                logger.warning(
                    "Sha256 ERROR on {}".format(archive_file_name)
                )
        except HTTPError as e:
            logger.debug("HTTP error: {}".format(e))
            r = requests.get(url)
            if r.status_code == 429 and 'Retry-After' in r.headers:
                retry_after = int(r.headers['Retry-After'])
                logger.info(
                    "Will retry to download {} after {} seconds".format(
                        archive_file_name, retry_after
                    )
                )
                delta = datetime.now(timezone.utc) + timedelta(0,
                                                               retry_after)
        finally:
            self.local_db.db_archive_update(
                archive_id=archive_id, available=delta, status=status
            )
            self.busy = False

    def pca_retry(self):
        """ Re-download archives
        """
        to_download = self.local_db.db_archive_to_download()
        if to_download:
            archive_id, sha256, filename, stream_id, service = to_download
            if not self.busy and not self.local_fs. \
                    fs_archive_exists(stream_id, filename):
                self.pca_download(
                    service=service, stream_id=stream_id, archive_id=archive_id,
                    sha256=sha256,
                    archive_file_name=self.local_fs.get_archive_filename(
                        stream_id, filename
                    )
                )
        else:
            nb = self.local_db.db_nb_archive_in_queue()
            logger.info(
                "Nothing to download right now. {} in queue".format(nb[0])
            )
