FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    xvfb \
    fontconfig \
    unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://bun.sh/install | bash && \
    mv /root/.bun/bin/bun /usr/local/bin/bun

WORKDIR /app
ENV VIRTUAL_ENV=/app/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --upgrade pip

RUN pip install pytest pylint

RUN pip install git+https://github.com/kny5/cq-cli.git@server_hotfix_01

RUN git clone https://gitlab.com/gitbuilding/cadorchestrator.git --branch server_hotfix_01

WORKDIR /app/cadorchestrator/js/cadorchestrator-app
RUN bun install && \
    bun run build

WORKDIR /app/cadorchestrator
RUN pip install -e .

WORKDIR /app
RUN git clone https://github.com/Wakoma/nimble.git --branch alpha

WORKDIR /app/nimble
RUN pip install -e .

ARG NOCODB_TOKEN
ENV NOCODB_TOKEN=${NOCODB_TOKEN}

RUN Xvfb :98 -screen 0 1024x768x24 & \
    export DISPLAY=:98 && \
    python -m pytest

RUN rm -rf build _cache_ _gb_temp_ && \
    rm OrchestratorConfigOptions.json devices.json

RUN nimble_devices_updater && \
    gen_nimble_conf_options

RUN pip freeze -l > requirements.txt

EXPOSE 8000

WORKDIR /app
COPY entrypoint.sh /app/entrypoint.sh
RUN ["chmod","+x","entrypoint.sh"]

WORKDIR /app/nimble
ENTRYPOINT ["/app/entrypoint.sh"]
