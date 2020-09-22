FROM python:slim

LABEL maintainer="te.pickering@gmail.com"

RUN apt update && apt -y install git
RUN python -m pip install --upgrade pip
RUN pip install astropy scipy numpy photutils pandas scikit-image
RUN pip install git+https://github.com/tepickering/skycam_utils#egg=skycam_utils

COPY iers.py /usr/local/bin/iers.py

VOLUME ["/data"]

WORKDIR /data

RUN /usr/local/bin/iers.py

ENTRYPOINT ["process_stellacam_dir"]
