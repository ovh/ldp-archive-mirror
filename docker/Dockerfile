FROM python:3
MAINTAINER OVH Group <opensource@ovh.net>

ENV OVH_API_REGION="ovh-eu" DB_DIRECTORY="/data/db" MIRROR_DIRECTORY="/data/mirror"

# Execution env
RUN mkdir -p "${DB_DIRECTORY}" "${MIRROR_DIRECTORY}"
VOLUME "${DB_DIRECTORY}"
VOLUME "${MIRROR_DIRECTORY}"

# ldp-archive-mirror install
COPY ldp-archive-mirror-*.tar.gz /tmp
RUN pip3 install /tmp/ldp-archive-mirror-*.tar.gz

# cleaning
RUN rm -f /tmp/get-pip.py /tmp/ldp-archive-mirror-*.tar.gz

# process
ENTRYPOINT ["/usr/local/bin/ldp-mirror"]
CMD ["exec", "$@"]
