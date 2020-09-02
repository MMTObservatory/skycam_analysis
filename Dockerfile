FROM python:slim

LABEL maintainer="te.pickering@gmail.com"

RUN pip install astropy scipy numpy photutils

COPY skycam_stats.py /usr/local/bin/skycam_stats
COPY iers.py /usr/local/bin/iers.py

VOLUME ["/data"]

WORKDIR /data

RUN /usr/local/bin/iers.py

ENTRYPOINT ["/usr/local/bin/skycam_stats"]
