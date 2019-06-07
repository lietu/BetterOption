#!/usr/bin/env sh

set -exuo pipefail

CONTAINER="betteroption"
IMAGE="betteroption-build"

docker build . -t "$IMAGE"
docker run -d --name "$CONTAINER" "$IMAGE"
docker exec "$CONTAINER" python build_data.py
docker cp "$CONTAINER":/src/web artifacts
docker rm -f "$CONTAINER"
