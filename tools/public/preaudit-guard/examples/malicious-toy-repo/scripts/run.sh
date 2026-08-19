#!/usr/bin/env bash
set -e

# Decode and execute a hidden payload.
echo "ZWNobyBwd25lZAo=" | base64 -d | bash

# Clean up traces.
rm -rf ~/.config/some-app
