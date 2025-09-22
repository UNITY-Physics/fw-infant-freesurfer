# Use the latest Python 3 docker image
FROM nialljb/freesurfer8.1.0-base:latest

# Setup environment for Docker image
ENV HOME=/root/
ENV FLYWHEEL="/flywheel/v0"
ENV PYTHONPATH="/flywheel/v0:$PYTHONPATH"
WORKDIR $FLYWHEEL
RUN mkdir -p $FLYWHEEL/input

# Copy the contents of the directory the Dockerfile is into the working directory of the to be container
COPY ./ $FLYWHEEL/
COPY license.txt /usr/local/freesurfer/.license

# Install Dev dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        unzip \
        gzip \
        wget \
        imagemagick \
        tcsh \
        hostname \
        zip \
        python3 \
        python3-pip \
        python3-setuptools \
        python3-wheel && \
    rm -rf /var/lib/apt/lists/*



RUN pip3 install flywheel-gear-toolkit && \
    pip3 install flywheel-sdk && \
    pip3 install jsonschema && \
    pip3 install pandas  && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* 


# Configure entrypoint
RUN bash -c 'chmod +rx $FLYWHEEL/run.py' && \
    bash -c 'chmod +rx $FLYWHEEL/app/' && \
    bash -c 'chmod +rx ${FLYWHEEL}/app/main.sh' 

ENTRYPOINT ["python3", "/flywheel/v0/run.py"] 