# Use the latest Python 3 docker image
FROM nialljb/freesurfer8.0.1-ubuntu:latest

# Setup environment for Docker image
ENV HOME=/root/
ENV FLYWHEEL="/flywheel/v0"
WORKDIR $FLYWHEEL
RUN mkdir -p $FLYWHEEL/input

# Copy the contents of the directory the Dockerfile is into the working directory of the to be container
COPY ./ $FLYWHEEL/

# Clean first
# Install Dev dependencies
RUN apt-get clean && \
    rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/* && \
    echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid && \
    echo 'APT::Get::AllowUnauthenticated "true";' >> /etc/apt/apt.conf.d/99no-check-valid && \
    apt-get update --allow-insecure-repositories && \
    apt-get install jq -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --allow-unauthenticated --no-install-recommends \
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


# FSL setup
# Install Miniconda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh

# Set up environment variables
ENV CONDA_DIR=/opt/conda
ENV PATH="${CONDA_DIR}/bin:${PATH}"
ENV FSL_CONDA_CHANNEL="https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/public"

# Accept Anaconda Terms of Service (needed for repo.anaconda.com)
RUN /opt/conda/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    /opt/conda/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# Install tini and FSL packages from FSL’s public conda channel
RUN /opt/conda/bin/conda install -n base -y -c conda-forge tini && \
    /opt/conda/bin/conda install -n base -y -c ${FSL_CONDA_CHANNEL} -c conda-forge fsl-base fsl-utils fsl-avwutils

# Define FSLDIR so tools know where to find FSL binaries
ENV FSLDIR=/opt/conda

# Since conda installs a new python, we need to reinstall the python dependencies
RUN pip3 install flywheel-gear-toolkit && \
    pip3 install flywheel-sdk && \
    pip3 install jsonschema && \
    pip3 install pandas  && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* 

# Configure entrypoint
RUN bash -c 'chmod +rx $FLYWHEEL/run.py' && \
    bash -c 'chmod +rx $FLYWHEEL/start.sh' && \
    bash -c 'chmod +rx $FLYWHEEL/app/' && \
    bash -c 'chmod +rx ${FLYWHEEL}/app/main.sh' && \
    bash -c 'chmod +rx -R /usr/local/freesurfer/8.1.0/*'

ENTRYPOINT ["bash", "/flywheel/v0/start.sh"] 