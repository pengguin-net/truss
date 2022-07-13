ARG CUDA_VERSION="11.4.0"
ARG CUDNN_VERSION="8"
ARG UBUNTU_VERSION="20.04"

FROM nvidia/cuda:${CUDA_VERSION}-cudnn${CUDNN_VERSION}-devel-ubuntu${UBUNTU_VERSION}

ARG VARIANT="3.9"


ARG VARIANT="3.9"

ENV LANG="C.UTF-8"

FROM mcr.microsoft.com/vscode/devcontainers/cuda:${VARIANT}

# Copy library scripts to execute
COPY .devcontainer/library-scripts/*.sh .devcontainer/library-scripts/*.env /tmp/library-scripts/

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

ARG INSTALL_ZSH="false"
ARG UPGRADE_PACKAGES="false"
ARG USE_MOBY="true"
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN apt-get update && /bin/bash /tmp/library-scripts/common-debian.sh "${INSTALL_ZSH}" "${USERNAME}" "${USER_UID}" "${USER_GID}" "${UPGRADE_PACKAGES}" "true" "true" \
    && /bin/bash /tmp/library-scripts/docker-in-docker-debian.sh "true" "${USERNAME}" "${USE_MOBY}" \
    && /bin/bash /tmp/library-scripts/baseten.sh "true" "${USERNAME}" "${USE_MOBY}" \
    && apt-get purge -y imagemagick imagemagick-6-common \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install --yes --no-install-recommends git fzf vim \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/* /tmp/library-scripts/

USER vscode
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH=/home/vscode/.poetry/bin:$PATH

USER root

VOLUME [ "/var/lib/docker" ]

# Setting the ENTRYPOINT to docker-init.sh will start up the Docker Engine
# inside the container "overrideCommand": false is set in devcontainer.json.
# The script will also execute CMD if you need to alter startup behaviors.
ENTRYPOINT [ "/usr/local/share/docker-init.sh" ]
CMD [ "sleep", "infinity" ]
