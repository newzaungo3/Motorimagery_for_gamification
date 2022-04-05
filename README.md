## Docker Prerequisite (Akraradet & Raknatee)

1. Docker
2. Docker-Compose

## How to use

The docker is designed to use with Visual Studio Code with Docker Extension. This way we can attach `visual code` to the docker environment.

edit projeccts name to your name such as EEG_Model in volumes on both gpu and cpu

There are 2 types of docker-compose. CPU only and GPU

- CPU
```sh
docker-compose -f docker-compose-cpu.yml up --build -d
```

- GPU
```sh
docker-compose -f docker-compose-gpu.yml up --build -d
```
---

Down docker
```sh
docker-compose -f docker-compose-gpu.yml down
```

