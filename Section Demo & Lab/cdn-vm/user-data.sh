#!/usr/bin/env bash
set -euo pipefail

# Change this if you publish the code under another repository or branch.
export CDN_LAB_REPO_ARCHIVE="https://github.com/kakaocloud-edu/tutorial/archive/refs/heads/main.tar.gz"

curl -fsSL "https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Section%20Demo%20%26%20Lab/cdn-vm/install.sh" | sudo -E bash
