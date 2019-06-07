#!/usr/bin/env sh

set -exuo pipefail

apk add --no-cache ca-certificates ruby
pip install -r requirements.txt
