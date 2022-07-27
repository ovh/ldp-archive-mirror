FROM python:3
LABEL maintainer="OVH Group <opensource@ovh.net>"

ENV OVH_API_REGION="ovh-eu" DB_DIRECTORY="/data/db" MIRROR_DIRECTORY="/data/mirror"

ARG USER_NAME
ARG UID
ARG GROUP_NAME
ARG GID
RUN if [ ! "${USER_NAME}" -o ! "${UID}" -o ! "${GROUP_NAME}" -o ! "${GID}" ]; then \
    echo "\"USER_NAME\", \"GROUP_NAME\", \"UID\ and \"GID\" build args must be set" && \
    exit 1; \
    fi

# Execution env
RUN mkdir -p "${DB_DIRECTORY}" "${MIRROR_DIRECTORY}"
VOLUME "${DB_DIRECTORY}"
VOLUME "${MIRROR_DIRECTORY}"

# Create the needed user & group
RUN if [ "${USER_NAME}" != "root" ]; then \
    groupadd -g "${GID}" -o "${GROUP_NAME}" && \
    useradd "${USER_NAME}" -m -u "${UID}" -g "${GID}" -s /bin/bash && \
    chown "${USER_NAME}" "${DB_DIRECTORY}" && \
    chown "${USER_NAME}" "${MIRROR_DIRECTORY}"; \
    fi

# ldp-archive-mirror install
COPY ldp-archive-mirror-*.tar.gz /tmp
RUN pip3 install /tmp/ldp-archive-mirror-*.tar.gz

# cleaning
RUN rm -f /tmp/get-pip.py /tmp/ldp-archive-mirror-*.tar.gz

USER $USER_NAME
WORKDIR "${MIRROR_DIRECTORY}"

# process
ENTRYPOINT ["/usr/local/bin/ldp-mirror"]
CMD ["exec", "$@"]
