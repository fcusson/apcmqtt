#!/bin/bash

function _main() {

    SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
    CONFIG_LOCATION="/etc/apcmqtt"
    LIB_LOCATION="/lib/apcmqtt"

    # check for dependencies
    install_dependencies

    # copy service file
    if [ ! -f "/etc/systemd/system/apcmqtt.service" ]; then
        cp "$SCRIPT_DIR/config/apcmqtt.service" "/etc/systemd/system/"
        chmod +x "/etc/systemd/system/apcmqtt.service"
    else
        echo "service file already exist, skip step"
    fi

    # copy module to /lib
    mkdir -p "$LIB_LOCATION"
    cp -r "$SCRIPT_DIR/apcmqtt" "$LIB_LOCATION/"

    # copy config to /etc
    if [ ! -f "$CONFIG_LOCATION/apcmqtt.yaml" ]; then
        mkdir -p "$CONFIG_LOCATION"
        cp "$SCRIPT_DIR/config/apcmqtt.yaml.exemple" "$CONFIG_LOCATION/apcmqtt.yaml"
    else
        echo "config file already exist, skip step"
    fi

}

function install_dependencies() {

    if [ -x "$(command -v apt)" ]; then
        apt install -y apcupsd python3 python3-pip
    elif [ -x "$(command -v dnf)" ]; then
        dnf install -y apcupsd python3 python3-pip
    elif [ -x "$(command -v zypper)" ]; then
        zypper addrepo https://download.opensuse.org/repositories/openSUSE:Factory/standard/openSUSE:Factory.repo
        zypper refresh
        zypper -n install apcupsd python3 python3-pip
    elif [ -x "$(command -v pacman)" ]; then
        yes | pacman -S apcupsd python python-pip
    elif [ -x "$(command -v emerge)" ]; then
        emerge sync
        emerge -y dev-lang/python:3.10
        emerge -y dev-python/pip
        emerge -y apcupsd
    elif [ -x "$(command -v apk)" ]; then
        apk add apcupsd
        apk add python3
        python -m ensurepip
    fi

    pip install paho-mqtt

}

if [ "$EUID" -ne 0 ]; then
    echo "Must be run as root"
    exit
fi

_main
