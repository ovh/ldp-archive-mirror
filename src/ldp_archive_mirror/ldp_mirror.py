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
from ldp_archive_mirror.db import LocalDB
from ldp_archive_mirror.fs import LocalFS
from ldp_archive_mirror.api import OvhAPI
from ldp_archive_mirror.pca import CloudArchive

logger = logging.getLogger(__name__)


class LDPMirror:
    def __init__(self, db_directory, app_key, app_secret, consumer_key,
                 ovh_region, mirror_directory, streams, chunk_size):
        self.local_db = LocalDB(db_directory)
        self.ovh_api = OvhAPI(
            streams=streams, local_db=self.local_db, app_key=app_key,
            app_secret=app_secret, consumer_key=consumer_key,
            ovh_region=ovh_region
        )
        self.local_fs = LocalFS(
            streams=streams, local_db=self.local_db,
            mirror_directory=mirror_directory
        )
        self.pca = CloudArchive(
            local_db=self.local_db, local_fs=self.local_fs,
            ovh_api=self.ovh_api, chunk_size=chunk_size
        )

    def check_for_new_archive(self):
        """ Launch a synchronisation
        """
        logger.info("Looking for new archives")
        self.ovh_api.api_update_cache()

    def attempt_to_download_again(self):
        """ Retry archive download
        """
        logger.info("Trying to download some archives")
        self.pca.pca_retry()
