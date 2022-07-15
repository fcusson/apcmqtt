#!/bin/bash

function _main() {

    SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
    CONFIG_LOCATION="/etc/apcmqtt"
    LIB_LOCATION="/lib/apcmqtt"

    # check for dependencies
    install_dependencies

    # copy service file
    cp "$SCRIPT_DIR/config/apcmqtt.service" "/etc/systemd/system/"
    chmod +x "/etc/systemd/system/apcmqtt.service"

    # copy module to /lib
    mkdir -p "$LIB_LOCATION"
    cp -r "$SCRIPT_DIR/apcmqtt" "$LIB_LOCATION/"

    # copy config to /etc
    mkdir -p "$CONFIG_LOCATION"
    cp "$SCRIPT_DIR/config/apcmqtt.yaml.exemple" "$CONFIG_LOCATION/apcmqtt.yaml"

}

function install_dependencies() {

    if [ -x "$(command -v apt)" ]; then
        apt install -y apcupsd
    elif [ -x "$(command -v dnf)" ]; then
        dnf install -y apcupsd
    elif [ -x "$(command -v zypper)" ]; then
        zypper addrepo https://download.opensuse.org/repositories/openSUSE:Factory/standard/openSUSE:Factory.repo
        zypper refresh
        zypper -n install apcupsd
    elif [ -x "$(command -v pacman)" ]; then
        yes | pacman -S apcupsd
    elif [ -x "$(command -v emerge)" ]; then
        emerge sync && emerge -y apcupsd
    elif [ -x "$(command -v apk)" ]; then
        apk add apcupsd
    fi

    pip install paho-mqtt

}

if [ "$EUID" -ne 0 ]; then
    echo "Must be run as root"
    exit
fi

_main
