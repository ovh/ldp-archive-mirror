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
from pathlib import Path
from typing import Union

import gnupg

logger = logging.getLogger(__name__)


class PgpDecryptor:
    """
    Wrapper to decrypt PGP encrypted files
    """

    def __init__(self, gpg_passphrase: str = None) -> None:

        self.gpg = gnupg.GPG()
        self.passphrase = gpg_passphrase

    def decrypt_file(self, file_path: Path, output_path: Path) -> Union[bytes, str]:
        """ Decrypt a file

        :param Path file_path: Path of the file to decrypt
        :param Path output_path: Path of the decrypted file to write
        :return: The decrypted file content (can be bytes or readable string)
        :rtype: Union[bytes, str]
        """

        try:
            with open(file_path, "rb") as f:
                result = self.gpg.decrypt_file(
                    file=f,
                    output=output_path,
                    always_trust=True,
                    passphrase=self.passphrase
                )
                if result.ok == True and result.status == 'decryption ok':
                    return result.data.decode(self.gpg.encoding)
                else:
                    raise RuntimeError(
                        f"PGP decryption error on {file_path.stem}: "
                        f"{result.status}"
                    )
        except Exception as exc:
            raise RuntimeError(exc)

    def display_archive_encryption_keys(
            self, api, service, stream_id, archive_id) -> None:
        """ Display the details of the encryption keys used by a given archive

        :param OvhAPI api: OVH API wrapper
        :param str service: LDP service name
        :param str stream_id: Stream UUID
        :param str archive_id: Archive UUID
        """

        keys_id = api.api_get_archive_encryption_keys(
            service, stream_id, archive_id
        )
        if keys_id:
            logger.info(
                f"Archive {archive_id} was encrypted with these PGP "
                "public keys :"
            )
        for key_id in keys_id:
            key_info = api.api_get_encryption_key(service, key_id)
            logger.info(f" - {key_info['fingerprint']} / {key_info['title']}")
        if keys_id:
            logger.info(
                "Ensure the corresponding PGP private keys are "
                "imported in your gpg keyring"
            )
