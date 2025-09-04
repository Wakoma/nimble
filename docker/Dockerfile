FROM ubuntu:latest

# Install Linux dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    git \
    curl \
    xvfb \
    libxkbcommon-x11-0 \
    x11-apps \
    xkb-data \
    openscad \
    fontconfig \
    mesa-utils \
    libgl1 \
    libgl1-mesa-dev \
    libglu1-mesa \
    libosmesa6 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm

WORKDIR /app
ENV VIRTUAL_ENV=/app/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
RUN git clone https://github.com/kny5/cq-cli.git --branch server_hotfix_01

WORKDIR /app/cq-cli
RUN pip install -e .

WORKDIR /app
RUN git clone https://gitlab.com/gitbuilding/cadorchestrator.git --branch server_hotfix_01

WORKDIR /app/cadorchestrator/js/cadorchestrator-app
RUN npm install && \
    npm run build

WORKDIR /app/cadorchestrator
RUN pip install -e .

WORKDIR /app
RUN git clone https://github.com/Wakoma/nimble.git --branch server_hotfix_01

# Install dependencies:
WORKDIR /app/nimble
RUN pip install -e .
RUN pip install scad2gltf pytest pylint

# Generate JSON from hardcoded configuration options

ARG NOCODB_TOKEN
ENV NOCODB_TOKEN=${NOCODB_TOKEN}
RUN nimble_devices_updater && \
    gen_nimble_conf_options

# Run pytest
WORKDIR /app/nimble
RUN Xvfb :99 -screen 0 1024x768x24 & \
    export DISPLAY=:99 && \
    python -m pytest

# Test generator
WORKDIR /app/nimble
RUN Xvfb :98 -screen 0 1024x768x24 & \
   export DISPLAY=:98 && \
   cadorchestrator --headless generate '{"device-ids": ["Raspberry_Pi_4B"]}'

# Use port 8000
EXPOSE 8000

WORKDIR /app
COPY entrypoint.sh /app/entrypoint.sh
RUN ["chmod","+x","entrypoint.sh"]

WORKDIR /app/nimble
ENTRYPOINT ["/app/entrypoint.sh"]
