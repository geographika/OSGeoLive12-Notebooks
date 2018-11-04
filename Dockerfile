#FROM python:2.7-slim
FROM ubuntu:18.04

RUN apt-get update && apt-get install -y --fix-missing --no-install-recommends unzip python python-pip mapserver-bin python-mapscript

# see https://github.com/pypa/pip/issues/5221#issuecomment-381568428
RUN hash -d pip

# install the notebook package
RUN pip install --no-cache --upgrade pip && \
    pip install --no-cache notebook

# create user with a home directory
ARG NB_USER
ARG NB_UID
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}
WORKDIR ${HOME}

RUN wget https://github.com/geographika/OSGeoLive12-Notebooks/archive/master.zip && \
	unzip master.zip

RUN https://github.com/mapserver/mapserver-demo/archive/master.zip && \
	unzip master.zip
