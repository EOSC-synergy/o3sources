# Dockerfile has three Arguments: base, tag, branch
# base - base image (default: python)
# tag - tag for base mage (default: stable-slim)
# branch - user repository branch to clone (default: python)
#
# To build the image:
# $ docker build -t <dockerhub_user>/<dockerhub_repo> --build-arg arg=value .
# or using default args:
# $ docker build -t <dockerhub_user>/<dockerhub_repo> .

# set the base image. default is python
ARG base=python
# set the tag (e.g. latest, 3.8, 3.7 : for python)
ARG tag=3.6-slim

# Base image, e.g. python:3.6-slim
FROM ${base}:${tag}

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
        gcc \
        g++ \
        git && \
# Clean up & back to dialog front end
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*
ENV DEBIAN_FRONTEND=dialog

COPY requirements.txt ./
RUN pip install --no-cache -r requirements.txt

# Change user context and drop root privileges
RUN mkdir /app
RUN groupadd -r ${group} && \
    useradd --no-log-init -r -d /app -g ${group} ${user} && \
    chown -R ${user} /app 
USER ${user}

COPY ompi_omp_program /app/ompi_omp_program
RUN mkdir -p /app/Data/Standard
RUN mkdir -p /app/Data/Skimmed

WORKDIR /app/Data

# Start default script
ENTRYPOINT [ "/app/ompi_omp_program" ]
