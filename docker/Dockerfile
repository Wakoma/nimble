FROM python:3.10-slim

# Install Linux dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    xvfb \
    # openscad \
    fontconfig \
    # mesa-demos \
    # mesa-dev \
    # glu \
    # libx11 \
    # libxrender \
    # libxext \
    # libsm \
    # libice \
    unzip
 #   && rm -rf /var/lib/apt/lists/*


RUN curl -fsSL https://bun.sh/install | bash && \
    mv /root/.bun/bin/bun /usr/local/bin/bun


WORKDIR /app
ENV VIRTUAL_ENV=/app/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --upgrade pip

WORKDIR /app
RUN pip install pytest pylint 
# cadquery-ocp

WORKDIR /app
RUN pip install git+https://github.com/CadQuery/cq-cli.git --branch server_hotfix_01

WORKDIR /app
RUN git clone https://gitlab.com/gitbuilding/cadorchestrator.git --branch server_hotfix_01

WORKDIR /app/cadorchestrator/js/cadorchestrator-app
RUN bun install && \
    bun run build

WORKDIR /app/cadorchestrator
RUN pip install -e .

WORKDIR /app
RUN git clone https://github.com/Wakoma/nimble.git@server_hotfix_01

WORKDIR /app/nimble
RUN pip install -e .

# Generate JSON from hardcoded configuration options
ARG NOCODB_TOKEN
ENV NOCODB_TOKEN=${NOCODB_TOKEN}

WORKDIR /app/nimble
RUN nimble_devices_updater && \
    gen_nimble_conf_options

# Run pytest
WORKDIR /app/nimble
RUN Xvfb :99 -screen 0 1024x768x24 & \
    export DISPLAY=:99 && \
    python -m pytest

RUN pip install -e .

# Test generator
# WORKDIR /app/nimble
# RUN Xvfb :98 -screen 0 1024x768x24 & \
#    export DISPLAY=:98 && \
#    cadorchestrator --headless generate '{"device-ids": ["Raspberry_Pi_4B"]}'

# Use port 8000
EXPOSE 8000

WORKDIR /app
COPY entrypoint.sh /app/entrypoint.sh
RUN ["chmod","+x","entrypoint.sh"]

WORKDIR /app/nimble
ENTRYPOINT ["/app/entrypoint.sh"]
