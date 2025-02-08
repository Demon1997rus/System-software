#!/bin/bash

# Путь к папке, в которой будет располагаться репозиторий
REPO_DIR="cmake-helper"

if [ -d "$REPO_DIR" ]; then
    cd "$REPO_DIR" || exit
    git pull origin main
else
    git clone git@github.com:Demon1997rus/cmake-helper.git
fi
