Assuming Docker is installed, and this repository has been cloned.
Run the following commands:

Enter this directory level:

`cd docker`

Build Docker image:
`docker build --no-cache -t nimble_cadorch_server .`

Run Standalone Docker server with created image:
`docker run -p 8000:8000 nimble_cadorch_server`

Docker compose:

Run the following command to deploy a complete devops setup:

```docker compose up -d```


