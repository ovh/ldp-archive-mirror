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
import sqlite3
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class LocalDB:
    def __init__(self, db_directory):
        if not os.path.exists(db_directory):
            os.makedirs(db_directory)
        self.database = "{}/ldp.db".format(db_directory)
        logger.info("Create local DB if not exists in {}".format(
            self.database
        ))
        self.exec_sql("""CREATE TABLE IF NOT EXISTS archives (archiveId text,
        sha256 text, md5 text, filename text, size numeric, streamId text,
        service text, status text DEFAULT "todo", available timestamp)""")

    def exec_sql(self, sql, parameters=None, fetch=None, commit=None):
        conn = sqlite3.connect(
            self.database, detect_types=sqlite3.PARSE_DECLTYPES
        )
        cursor = conn.cursor()
        if parameters is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, parameters)
        data = None
        if fetch == "one":
            data = cursor.fetchone()
        elif fetch == "all":
            data = cursor.fetchall()
        if commit:
            conn.commit()
        conn.close()
        return data

    def db_all_archives(self):
        """ List all archives

        :return: Stored archives
        :rtype: list
        """
        return self.exec_sql(
            sql="""SELECT archiveId, sha256, filename, streamId, service,
            status FROM archives""",
            fetch="all"
        )

    def db_all_todo_archives(self):
        """ List archive in todo

        :return: Archives in todo
        :rtype: list
        """
        return self.exec_sql(
            sql="""SELECT archiveId, sha256, filename, streamId, service,
            status FROM archives WHERE status='todo'""",
            fetch="all"
        )

    def db_archive(self, archive_id):
        """ Search the archive

        :param str archive_id: The archive Id
        :return: The archive record
        :rtype: dict
        """
        parameters = (archive_id,)
        sql = """SELECT archiveId, sha256, filename, streamId, service
        FROM archives WHERE archiveId=?"""
        return self.exec_sql(sql=sql, parameters=parameters, fetch="one")

    def db_archive_to_download(self):
        """ Get the first archive to download

        :return: The archive record
        :rtype: dict
        """
        parameters = (datetime.now(timezone.utc),)
        sql = """SELECT archiveId, sha256, filename, streamId, service FROM
        archives WHERE available < ? and status='todo'
        ORDER BY archiveId DESC LIMIT 1"""
        return self.exec_sql(sql=sql, parameters=parameters, fetch="one")

    def db_archive_add(self, archive, stream_id, service):
        """ Store archive in database

        :param dict archive: archive information
        :param str stream_id: stream Id
        :param str service: service name
        """
        parameters = (archive['archiveId'], archive['sha256'], archive['md5'],
                      archive['filename'], archive['size'], stream_id,
                      service, None, None)
        sql = "INSERT INTO archives VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self.exec_sql(sql=sql, parameters=parameters, commit=True)

    def db_archive_cache(self, archive, stream_id, service):
        """ Load archive information from database

        :param dict archive: archive information
        :param str stream_id: stream Id
        :param str service: service name
        """
        exists = self.db_archive(archive_id=archive['archiveId'])
        if exists is None:
            self.db_archive_add(archive, stream_id, service)
            logger.info(
                "Archive {} added to cache".format(archive['archiveId'])
            )

    def db_archive_update(self, archive_id, available, status):
        """ Update archive information in database

        :param str archive_id: Archive ID
        :param datetime available: Availability
        :param str status: status
        """
        parameters = (status, available, archive_id,)
        sql = """UPDATE archives SET status = ?,
        available = ? WHERE archiveId = ?"""
        self.exec_sql(sql=sql, parameters=parameters, commit=True)

    def db_nb_archive_in_queue(self):
        """ Count available archives

        :return: Number of available archives
        :rtype: int
        """
        sql = """SELECT COUNT(*) from archives WHERE status='todo'
        AND available IS NOT NULL"""
        return self.exec_sql(sql=sql, fetch="one")
