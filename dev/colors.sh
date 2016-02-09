#!/bin/bash
# Bash color echo <http://blenderfds.org/>.
# Copyright (C) 2016 Emanuele Gissi

BOLD="\033[1;10m"
RED="\033[0;31m"
REDBOLD="\033[1;31m"
GREEN="\033[0;32m"
GREENBOLD="\033[1;32m"
YELLOW="\033[0;33m"
YELLOWBOLD="\033[1;33m"
BLUE="\033[0;34m"
BLUEBOLD="\033[1;34m"
ENDCOLOR="\033[0m"

echo_title() {
    echo -e $BLUEBOLD"$@"$ENDCOLOR
}

echo_msg() {
    echo -e $YELLOW"$@"$ENDCOLOR
}

echo_ok() {
    echo -e $GREEN"$@"$ENDCOLOR
}

echo_err() {
    echo -e $RED"$@"$ENDCOLOR
}

