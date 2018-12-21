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
import ovh
import sys
from ovh.exceptions import APIError

logger = logging.getLogger(__name__)


class OvhAPI:
    def __init__(self, streams, local_db, app_key=None, app_secret=None,
                 consumer_key=None, ovh_region='ovh-eu'):
        self.local_db = local_db
        self.streams = streams
        self.client = None
        if app_key and app_secret and consumer_key:
            self.client = ovh.Client(
                endpoint=ovh_region, application_key=app_key,
                application_secret=app_secret, consumer_key=consumer_key
            )
        else:
            logger.critical('Missing OVH_API_* environment variables. Dying...')
            sys.exit(0)
        self.api_update_cache()

    def api_get_services(self):
        """ List Account services

        :return: OVH API accounts
        :rtype: dict
        """
        try:
            return self.client.get('/dbaas/logs')
        except APIError as e:
            logger.warning("API error, will retry later: {}".format(e))

    def api_get_streams(self, service):
        """ List service streams UUID

        :param str service: LDP service name
        :return: Stream UUIDs
        :rtype: list(str)
        """
        try:
            return self.client.get(
                '/dbaas/logs/{}/output/graylog/stream'.format(service)
            )
        except APIError as e:
            logger.warning("API error, will retry later: {}".format(e))

    def api_get_archives(self, service, stream_id):
        """ List stream archives

        :param str service: LDP service name
        :param str stream_id: Stream UUID
        :return: Archive UUIDs
        :rtype: list(str)
        """
        try:
            return self.client.get(
                '/dbaas/logs/{}/output/graylog/stream/{}/archive'.format(
                    service, stream_id
                )
            )
        except APIError as e:
            logger.warning("API error, will retry later: {}".format(e))

    def api_get_archive(self, service, stream_id, archive_id):
        """  Get archive information

        :param str service: LDP service name
        :param str stream_id: Stream UUID
        :param str archive_id: Archive UUID
        :return: Archive information
        :rtype: dict
        """
        try:
            return self.client.get(
                '/dbaas/logs/{}/output/graylog/stream/{}/archive/{}'.format(
                    service, stream_id, archive_id
                )
            )
        except APIError as e:
            logger.warning("API error, will retry later: {}".format(e))

    def api_get_archive_url(self, service, stream_id, archive_id):
        """ Get archive temporary URL

        :param str service: LDP service name
        :param str stream_id: Stream UUID
        :param str archive_id: Archive UUID
        :return: Archive URL
        :rtype: str
        """
        try:
            archive_url = self.client.post(
                '/dbaas/logs/{}/output/graylog/stream/{}/archive/{}/url'.format(
                    service, stream_id, archive_id
                )
            )
            return archive_url['url']
        except APIError as e:
            logger.warning("API error, will retry later: {}".format(e))

    def api_lookup_service(self, stream_ref):
        """ Find the given stream's service

        :param str stream_ref: Stream UUID
        :return: Service account
        :rtype: Service Uuid
        """
        for service in self.api_get_services():
            for stream_id in self.api_get_streams(service):
                if stream_id == stream_ref:
                    logger.info("Service {} found for stream {}".format(
                        service, stream_id
                    ))
                    return service

    def api_update_cache(self):
        """ Update database cache
        """
        stored_archives = []
        for archive in self.local_db.db_all_archives():
            stored_archives.append(archive[0])
        for stream_id in self.streams:
            logger.info(
                "Looking for new archives of stream {}".format(stream_id)
            )
            service = self.api_lookup_service(stream_id)
            api_archives = self.api_get_archives(service, stream_id)
            if service and api_archives:
                for archiveId in api_archives:
                    if archiveId not in stored_archives:
                        archive = self.api_get_archive(
                            service, stream_id, archiveId
                        )
                        self.local_db.db_archive_cache(archive, stream_id, service)
