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
import os
import time

import argparse
import pkg_resources
import schedule
from ldp_archive_mirror.log import setup_logging

PARSER = argparse.ArgumentParser(
    description="LDP archive Mirror CLI - {}".format(
        pkg_resources.get_distribution('ldp-archive-mirror').version
    )
)
PARSER.add_argument(
    "--app-key", help="OVH application key (default: %(default)s)",
    default=os.getenv('OVH_API_AK', None), metavar="KEY"
)
PARSER.add_argument(
    "--app-secret", help="OVH application secret (default: %(default)s)",
    default=os.getenv('OVH_API_AS', None), metavar="SECRET"
)
PARSER.add_argument(
    "--consumer-key", help="OVH consumer key (default: %(default)s)",
    default=os.getenv('OVH_API_CK', None), metavar="SECRET"
)
PARSER.add_argument(
    "--ovh-region", help="OVH region (default: %(default)s)",
    default=os.getenv('OVH_API_REGION', "ovh-eu"), metavar="REGION"
)
PARSER.add_argument(
    "--db", default=os.getenv('DB_DIRECTORY', "db"), metavar="DIR",
    help="Where to place the local sqlite database (default: %(default)s)"
)
PARSER.add_argument(
    "--mirror", default=os.getenv('MIRROR_DIRECTORY', "mirror"), metavar="DIR",
    help="Where to place your archives (default: %(default)s)"
)
PARSER.add_argument(
    "--ldp-host", default=os.getenv('LDP_HOST', None), metavar="HOST",
    help="If set, push logs of the current application to given LDP hostname"
)
PARSER.add_argument(
    "--ldp-token", default=os.getenv('LDP_TOKEN', None), metavar="TOKEN",
    help="If set, push logs of the current application to associated LDP stream token"
)
PARSER.add_argument(
    "--chunk-size", default=int(os.getenv('CHUNK_SIZE', "16384")),
    metavar="CHUNK", help="Download chunk size in bytes (default: %(default)s)"
)
PARSER.add_argument(
    "stream", nargs="+", help="LDP Stream UUIDs", metavar="STREAM_ID"
)


def main():
    args = PARSER.parse_args()
    setup_logging(args.ldp_host, args.ldp_token)

    try:
        from ldp_archive_mirror.ldp_mirror import LDPMirror
        mirror = LDPMirror(
            db_directory=os.path.realpath(args.db), app_key=args.app_key,
            app_secret=args.app_secret, consumer_key=args.consumer_key,
            ovh_region=args.ovh_region, streams=args.stream,
            mirror_directory=os.path.realpath(args.mirror),
            chunk_size=args.chunk_size
        )
        schedule.every().hour.do(mirror.check_for_new_archive)
        schedule.every(1).minutes.do(mirror.attempt_to_download_again)
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted by user!")
