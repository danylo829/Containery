#!/bin/bash

# Used by GitHub Actions to extract a tag's annotation message.
# Called from workflow YAML via `run: .github/scripts/get-tag-message.sh`

set -euo pipefail

git fetch --depth=1 origin +refs/tags/*:refs/tags/*

echo "message<<EOF"
git for-each-ref "$GITHUB_REF" --format='%(contents)'
echo "EOF"