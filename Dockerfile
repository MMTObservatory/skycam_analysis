FROM python:slim

LABEL maintainer="te.pickering@gmail.com"

RUN pip install astropy scipy numpy photutils

COPY skycam_stats.py /usr/local/bin/skycam_stats

VOLUME ["/data"]

WORKDIR /data

ENTRYPOINT ["/usr/local/bin/skycam_stats"]
