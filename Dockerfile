FROM python:3.12
COPY . .
RUN apt-get update -qq
RUN apt-get -o DPkg::Options::=--force-confdef -y -qq install xvfb
RUN pip install -e .
EXPOSE 8000
ENTRYPOINT ["cadorchestrator", "serve", "--production"]
