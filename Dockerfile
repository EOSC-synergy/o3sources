# Dockerfile has three Arguments: base, tag, branch
# base - base image (default: python)
# tag - tag for base mage (default: stable-slim)
# branch - user repository branch to clone (default: python)
#
# To build the image:
# $ docker build -t <dockerhub_user>/<dockerhub_repo> --build-arg arg=value .
# or using default args:
# $ docker build -t <dockerhub_user>/<dockerhub_repo> .

# set the tag (e.g. latest, 3.8, 3.7 : for python)
ARG tag=3.8-slim

# Base image, e.g. python:3.8-slim
FROM python:${tag} as build
LABEL maintainer='B.Esteban, T.Kerzenmacher, V.Kozlov (KIT)'

# Which user and group to use 
ARG user=application
ARG group=standard

# Set environments
ENV LANG C.UTF-8

# Install system updates and tools
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Install system updates and tools
    ca-certificates \
    gcc g++ \
    libproj-dev proj-data proj-bin \
    libudunits2-0 udunits-bin \
    libgeos-dev \
    libeccodes-dev \
    git && \
    # Clean up & back to dialog front end
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*
ENV DEBIAN_FRONTEND=dialog

COPY requirements.txt ./
RUN pip install --no-cache -r requirements.txt
RUN rm requirements.txt

# Change user context and drop root privileges
RUN mkdir /app
RUN groupadd -r ${group} && \
    useradd --no-log-init -r -d /app -g ${group} ${user} && \
    chown -R ${user} /app 
USER ${user}

RUN mkdir -p /app/Sources
RUN mkdir -p /app/Skimmed

# Start default script
COPY ./scripts /app/scripts
WORKDIR /app


# Target stage to build cfchecks image
# docker build --target cfchecks -t cfchecks:<tag> .
FROM build as cfchecks
ENTRYPOINT ["/app/scripts/cfchecks.py"]

# target stage to build tco3_zm image
# docker build --target tco3_zm -t tco3_zm:<tag> .
FROM build as tco3_zm
ENTRYPOINT ["/app/scripts/tco3_zm.py"]

# Target stage for simple running
# docker build --target tco3_zm -t tco3_zm:<tag> .
FROM build as o3sources
ENTRYPOINT ["/bin/bash"]
