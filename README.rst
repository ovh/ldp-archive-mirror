***********************************
Logs Data Platform - Archive mirror
***********************************

.. image:: https://img.shields.io/pypi/v/ldp-archive-mirror.svg
   :target: https://pypi.python.org/pypi/ldp-archive-mirror/
   :alt: Latest Version

.. image:: https://travis-ci.org/ovh/ldp-archive-mirror.svg?branch=master
   :target: https://travis-ci.org/ovh/ldp-archive-mirror
   :alt: Latest version

This tools allows you to get a local copy of all your cold stored archives on Logs Data Platform::

    [2018-12-14 17:20:00,200 INFO LDP Mirror] Create local DB if not exists
    [2018-12-14 17:20:00,204 INFO LDP Mirror] Looking for new archives of stream e9397556-31d1-4d4d-b2bd-e5367b522cc8
    [2018-12-14 17:20:05,190 INFO LDP Mirror] Service ldp-jb-52560 found for stream e9397556-31d1-4d4d-b2bd-e5367b522cc8
    [2018-12-14 17:20:05,579 INFO LDP Mirror] Archive 9fb75957-2cde-435e-bdd9-6dfd33663f2c added to cache
    [2018-12-14 17:20:05,850 INFO LDP Mirror] Archive 11d8630a-7b38-4fa4-9d7c-dfd17b0b00f6 added to cache
    ...
    [2018-12-14 17:20:08,392 INFO LDP Mirror] Directory mirror/e9397556-31d1-4d4d-b2bd-e5367b522cc8 created
    [2018-12-14 17:20:08,535 INFO LDP Mirror] Archive e9397556-31d1-4d4d-b2bd-e5367b522cc8/2018-12-10.zst missing, download scheduled
    [2018-12-14 17:20:08,635 INFO LDP Mirror] Archive e9397556-31d1-4d4d-b2bd-e5367b522cc8/2018-12-11.zst missing, download scheduled
    ...
    [2018-12-14 17:20:09,535 INFO LDP Mirror] Will retry to download e9397556-31d1-4d4d-b2bd-e5367b522cc8/2018-12-10.zst after 596 seconds
    [2018-12-14 17:20:09,745 INFO LDP Mirror] Will retry to download e9397556-31d1-4d4d-b2bd-e5367b522cc8/2018-12-11.zst after 598 seconds
    ...
    [2018-12-14 17:20:10,927 INFO LDP Mirror] Archive e9397556-31d1-4d4d-b2bd-e5367b522cc8/2018-12-10.zst downloaded
    [2018-12-14 17:20:11,655 INFO LDP Mirror] Sha256 OK on e9397556-31d1-4d4d-b2bd-e5367b522cc8/2018-12-10.zst
    [2018-12-14 17:20:10,927 INFO LDP Mirror] Archive e9397556-31d1-4d4d-b2bd-e5367b522cc8/2018-12-11.zst downloaded
    [2018-12-14 17:20:11,655 INFO LDP Mirror] Sha256 OK on e9397556-31d1-4d4d-b2bd-e5367b522cc8/2018-12-11.zst


Quickstart
==========

First, install **ldp-archive-mirror** using `pip <https://pip.pypa.io/en/stable/>`_::

    pip install -U ldp-archive-mirror

Then you can use the binary `ldp-mirror`::

    usage: ldp-mirror [-h] [--app-key KEY] [--app-secret SECRET]
                  [--consumer-key KEY] [--ovh-region REGION] [--db DIR]
                  [--mirror DIR] [--ldp-host HOST] [--ldp-token TOKEN]
                  STREAM_ID [STREAM_ID ...]

    LDP archive Mirror CLI - 0.1.0

    positional arguments:
      STREAM_ID            LDP Stream UUIDs

    optional arguments:
      -h, --help           show this help message and exit
      --app-key KEY        OVH application key (default: None)
      --app-secret SECRET  OVH application secret (default: None)
      --consumer-key KEY   OVH consumer key (default: None)
      --ovh-region REGION  OVH region (default: ovh-eu)
      --db DIR             Where to place the local sqlite database (default: db)
      --mirror DIR         Where to place your archives (default: mirror)
      --ldp-host HOST      If set, push logs of the current application to given
                           LDP hostname
      --ldp-token TOKEN    If set, push logs of the current application to
                           associated LDP stream token

Setup
=====

1. Create an application
------------------------

To interact with the APIs, the application needs to identify itself using an
`application_key` and an `application_secret`. To get them, you need
to register your application. Depending the API you plan to use, visit:

- `OVH Europe <https://eu.api.ovh.com/createApp/>`_
- `OVH US <https://api.ovhcloud.com/createApp/>`_
- `OVH North-America <https://ca.api.ovh.com/createApp/>`_
- `So you Start Europe <https://eu.api.soyoustart.com/createApp/>`_
- `So you Start North America <https://ca.api.soyoustart.com/createApp/>`_
- `Kimsufi Europe <https://eu.api.kimsufi.com/createApp/>`_
- `Kimsufi North America <https://ca.api.kimsufi.com/createApp/>`_

On the restriction step, we invite you to set the following access rules::

    curl -XPOST -H"X-Ovh-Application: OVH_API_AK" -H "Content-type: application/json" \
    https://eu.api.ovh.com/1.0/auth/credential  -d '{
        "accessRules": [
            {
                "method": "GET",
                "path": "/dbaas/logs"
            },
            {
                "method": "GET",
                "path": "/dbaas/logs/*/output/graylog/stream"
            },
            {
                "method": "GET",
                "path": "/dbaas/logs/*/output/graylog/stream/*/archive*"
            },
            {
                "method": "POST",
                "path": "/dbaas/logs/*/output/graylog/stream/*/archive/*/url"
            }
        ],
        "redirection":"https://www.mywebsite.com/"
    }'


Once created, you will obtain an **application key (OVH_API_AK)** and an **application
secret (OVH_API_AS)**.

2. Environment variables
------------------------

Default cli values can be set using environment:

============================  ====================  ============================================================================
Cli parameter                 Name                  About
============================  ====================  ============================================================================
--app-key                     OVH_API_AK            OVH application key
--app-secret                  OVH_API_AS            OVH application secret
--consumer-key                OVH_API_CK            OVH customer key
--ovh-region                  OVH_API_REGION        OVH api location. Default: *ovh-eu*
--db                          DB_DIRECTORY          Where to place the local sqlite database. Default: *db*
--mirror                      MIRROR_DIRECTORY      Where to place your archives. Default: *mirror*
--ldp-host                    LDP_HOST              If set, push logs of the current application to given LDP hostname
--ldp-token                   LDP_TOKEN             If set, push logs of the current application to associated LDP stream token
============================  ====================  ============================================================================


3. Launch
---------

Once all the mandatory environment variables set, launch the process like this::

    $ ldp-mirror STREAM_ID [STREAM_ID ...]

This will:

- looks for the LDP service associated with the given **STREAM_ID** (s)
- populate a local cache with all the archives found on the API
- request for each of them a temporary download url
- download the files when unseal time is reached
- ask every hour the api if a new archive is available

Create docker image from sources
================================

As this application is supposed to be kept alive indefinitely, launching it from a Docker daemon looks obvious.

To build the image form the sources, uses the given `Makefile`::

    $ git clone https://github.com/ovh/ldp-archive-mirror
    $ cd ldp-archive-mirror
    $ make build-docker

And to run it::

    $ docker run -v /my_backup/mirror/:/data/mirror -v /my_backup/db:/data/db \
    -e OVH_API_AK=MY_OVH_AK -e OVH_API_AS=MY_OVH_AS -e OVH_API_CK=MY_OVH_CK \
    -t MY_LDP_STREAM_ID_1 MY_LDP_STREAM_ID_2

Requirements
============

- Python >= 3.3

Project Links
=============

- PyPI: https://pypi.python.org/pypi/ldp-archive-mirror
- Issues: https://github.com/ovh/ldp-archive-mirror/issues

License
=======

`OVH SAS <https://github.com/ovh/ldp-archive-mirror/blob/master/LICENSE>`_
