#!/usr/bin/env sh

set -exu

apk add --no-cache ca-certificates ruby
pip install -r requirements.txt
