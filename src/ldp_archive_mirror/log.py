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
import sys

from djehouty.libgelf.handlers import GELFTCPSocketHandler


def setup_logging(ldp_hostname=None, ldp_token=None):
    """ Setup logging, if no ldp config set we'll use stdout

    :param str ldp_hostname: LDP input
    :param str ldp_token: LDP stream token
    """
    logging.getLogger().setLevel(logging.DEBUG)
    if ldp_hostname and ldp_token:
        logging.getLogger().addHandler(GELFTCPSocketHandler(
            host=ldp_hostname,
            port=12202,
            static_fields={"X-OVH-TOKEN": ldp_token},
            use_tls=True,
            level=logging.INFO,
            null_character=True,
        ))
        logging.info("LDP configured, stdout logger disabled")
    else:
        stdout = logging.StreamHandler(sys.stdout)
        stdout.setLevel(logging.INFO)
        stdout.setFormatter(logging.Formatter(
            "[%(asctime)s %(levelname)s %(name)s] %(message)s"
        ))
        logging.getLogger().addHandler(stdout)
        logging.info("LDP is not configured, stdout logger will be used")
